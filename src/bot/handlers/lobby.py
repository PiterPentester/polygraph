import logging
from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from bot import keyboards, messages
from config import settings
from game.manager import RoomManager
from game.models import Player
from game.questions import QuestionManager

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data == "create_room")
async def handle_create_room(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    player = Player(id=user.id, full_name=user.full_name, username=user.username)
    room = room_manager.create_room(host=player)

    bot_info = await bot.get_me()
    bot_username = bot_info.username or settings.bot_username

    await callback.message.edit_text(
        messages.lobby_text(room, bot_username=bot_username),
        reply_markup=keyboards.lobby_kb(room, user.id),
        parse_mode="HTML",
    )
    await callback.answer("Кімнату створено!")


@router.callback_query(lambda c: c.data == "refresh_lobby")
async def handle_refresh_lobby(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room:
        await callback.answer("Ви не знаходитесь у кімнаті.", show_alert=True)
        await callback.message.edit_text(
            messages.welcome_text(),
            reply_markup=keyboards.main_menu_kb(),
            parse_mode="HTML",
        )
        return

    bot_info = await bot.get_me()
    bot_username = bot_info.username or settings.bot_username

    await callback.message.edit_text(
        messages.lobby_text(room, bot_username=bot_username),
        reply_markup=keyboards.lobby_kb(room, user.id),
        parse_mode="HTML",
    )
    await callback.answer("Оновлено")


@router.callback_query(lambda c: c.data == "change_spies")
async def handle_change_spies(callback: CallbackQuery, room_manager: RoomManager):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or not room.is_host(user.id):
        await callback.answer(
            "Тільки хост може змінювати кількість шпигунів.", show_alert=True
        )
        return

    await callback.message.edit_text(
        "🕵️ <b>Оберіть кількість шпигунів для наступного раунду:</b>\n"
        f"Поточна кількість гравців: <b>{len(room.players)}</b>",
        reply_markup=keyboards.spy_count_kb(room),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("set_spies:"))
async def handle_set_spies(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or not room.is_host(user.id):
        await callback.answer(
            "Тільки хост може змінювати налаштування.", show_alert=True
        )
        return

    count = int(callback.data.split(":")[1])
    if room.set_spy_count(count):
        await callback.answer(f"Встановлено {count} шпигунів!")
    else:
        await callback.answer(
            f"Неприпустима кількість шпигунів (має бути менше ніж {len(room.players)}).",
            show_alert=True,
        )

    bot_info = await bot.get_me()
    bot_username = bot_info.username or settings.bot_username

    await callback.message.edit_text(
        messages.lobby_text(room, bot_username=bot_username),
        reply_markup=keyboards.lobby_kb(room, user.id),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "kick_player_menu")
async def handle_kick_menu(callback: CallbackQuery, room_manager: RoomManager):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or not room.is_host(user.id):
        await callback.answer("Тільки хост може виганяти гравців.", show_alert=True)
        return

    if len(room.players) <= 1:
        await callback.answer("У кімнаті немає інших гравців.", show_alert=True)
        return

    await callback.message.edit_text(
        "👢 <b>Оберіть гравця, якого бажаєте вигнати з кімнати:</b>",
        reply_markup=keyboards.kick_player_kb(room),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("kick:"))
async def handle_kick_player(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or not room.is_host(user.id):
        await callback.answer("Тільки хост може виганяти гравців.", show_alert=True)
        return

    kicked_id = int(callback.data.split(":")[1])
    kicked_player = room.players.get(kicked_id)
    if kicked_player:
        room_manager.leave_room(kicked_id)
        try:
            await bot.send_message(
                kicked_id,
                f"👢 Вас було вигнано з кімнати <code>{room.code}</code>.",
                reply_markup=keyboards.main_menu_kb(),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.debug(f"Failed to notify kicked player {kicked_id}: {e}")

        await callback.answer(f"Гравця {kicked_player.full_name} вигнано.")

    bot_info = await bot.get_me()
    bot_username = bot_info.username or settings.bot_username

    await callback.message.edit_text(
        messages.lobby_text(room, bot_username=bot_username),
        reply_markup=keyboards.lobby_kb(room, user.id),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "back_to_lobby")
async def handle_back_to_lobby(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room:
        await callback.answer("Кімнату не знайдено.")
        await callback.message.edit_text(
            messages.welcome_text(),
            reply_markup=keyboards.main_menu_kb(),
            parse_mode="HTML",
        )
        return

    room.reset_for_next_round()

    bot_info = await bot.get_me()
    bot_username = bot_info.username or settings.bot_username

    await callback.message.edit_text(
        messages.lobby_text(room, bot_username=bot_username),
        reply_markup=keyboards.lobby_kb(room, user.id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "leave_room")
async def handle_leave_room(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    room = room_manager.leave_room(user.id)
    await callback.answer("Ви покинули кімнату.")
    await callback.message.edit_text(
        messages.welcome_text(),
        reply_markup=keyboards.main_menu_kb(),
        parse_mode="HTML",
    )

    if room and room.players:
        for p in room.players.values():
            try:
                await bot.send_message(
                    p.id,
                    f"🚪 Гравець <b>{user.full_name}</b> покинув кімнату.\nЗалишилось гравців: <b>{len(room.players)}</b>",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.debug(f"Failed to notify player {p.id}: {e}")


@router.callback_query(lambda c: c.data == "start_game")
async def handle_start_game(
    callback: CallbackQuery,
    bot: Bot,
    room_manager: RoomManager,
    question_manager: QuestionManager,
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or not room.is_host(user.id):
        await callback.answer("Тільки хост може розпочати гру.", show_alert=True)
        return

    min_required = room.spy_count + 1
    if len(room.players) < min_required:
        await callback.answer(
            f"Недостатньо гравців для старту! Потрібно мінімум {min_required} (зараз {len(room.players)}).",
            show_alert=True,
        )
        return

    success = room.start_round(question_manager)
    if not success:
        await callback.answer(
            "Помилка під час вибору запитань або старту раунду.", show_alert=True
        )
        return

    await callback.answer("🎮 Раунд розпочато!")

    # Send individual questions to all players
    for p in room.players.values():
        try:
            await bot.send_message(
                p.id,
                messages.question_prompt_text(p.question),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(
                f"Failed to send question to player {p.id} ({p.full_name}): {e}"
            )
