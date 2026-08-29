import logging
from aiogram import Bot, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from bot import keyboards, messages
from config import settings
from game.manager import RoomManager
from game.models import Player

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, room_manager: RoomManager):
    user = message.from_user
    if not user:
        return

    player = Player(id=user.id, full_name=user.full_name, username=user.username)
    text_parts = message.text.split(maxsplit=1) if message.text else []

    # Check if there is a deep link room code
    if len(text_parts) > 1:
        raw_code = text_parts[1].strip()
        code = raw_code.replace("room_", "").upper()
        room = room_manager.get_room(code)

        if not room:
            await message.answer(
                f"❌ Кімнату з кодом <code>{code}</code> не знайдено або гру вже завершено.",
                reply_markup=keyboards.main_menu_kb(),
                parse_mode="HTML",
            )
            return

        success = room_manager.join_room(code, player)
        if not success:
            await message.answer(
                "❌ Не вдалося приєднатися до кімнати (можливо, раунд вже триває).",
                reply_markup=keyboards.main_menu_kb(),
                parse_mode="HTML",
            )
            return

        bot_info = await bot.get_me()
        bot_username = bot_info.username or settings.bot_username

        # Notify joining player
        await message.answer(
            f"🎉 Ви успішно приєдналися до кімнати <code>{room.code}</code>!\n\n"
            + messages.lobby_text(room, bot_username=bot_username),
            reply_markup=keyboards.lobby_kb(room, user.id),
            parse_mode="HTML",
        )

        # Notify other players in the room
        for p in room.players.values():
            if p.id != user.id:
                try:
                    await bot.send_message(
                        p.id,
                        f"👋 Гравець <b>{player.full_name}</b> приєднався до кімнати!\n"
                        f"Всього гравців: <b>{len(room.players)}</b>",
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.debug(f"Failed to notify player {p.id}: {e}")
        return

    # Plain /start command
    await message.answer(
        messages.welcome_text(),
        reply_markup=keyboards.main_menu_kb(),
        parse_mode="HTML",
    )


@router.message(Command("rules"))
@router.callback_query(lambda c: c.data == "show_rules")
async def handle_rules(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        await event.answer()
        await event.message.answer(messages.rules_text(), parse_mode="HTML")
    else:
        await event.answer(messages.rules_text(), parse_mode="HTML")
