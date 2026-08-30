import logging
from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from bot import keyboards, messages
from game.manager import RoomManager
from game.models import GamePhase
from game.questions import QuestionManager

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("vote:"))
async def handle_cast_vote(
    callback: CallbackQuery, bot: Bot, room_manager: RoomManager
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or room.phase != GamePhase.VOTING:
        await callback.answer("Голосування не активно.", show_alert=True)
        return

    voter_player = room.players.get(user.id)
    if not voter_player or voter_player.is_kicked:
        await callback.answer(
            "Ви вибули з гри і не можете голосувати.", show_alert=True
        )
        return

    target_id = int(callback.data.split(":")[1])
    if target_id == user.id:
        await callback.answer("Ви не можете голосувати проти себе!", show_alert=True)
        return

    target_player = room.players.get(target_id)
    if not target_player:
        await callback.answer("Гравця не знайдено.", show_alert=True)
        return

    if target_player.is_kicked:
        await callback.answer("Цей гравець уже вибув з гри.", show_alert=True)
        return

    success = room.cast_vote(voter_id=user.id, target_id=target_id)
    if not success:
        await callback.answer("Не вдалося проголосувати.", show_alert=True)
        return

    await callback.answer(f"✅ Ваш голос за {target_player.full_name} зараховано!")

    # Update voter's keyboard to display selection
    try:
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.voting_kb(room, user.id)
        )
    except Exception:
        pass

    # If all votes are in, calculate and broadcast results
    if room.all_votes_cast():
        result = room.resolve_votes()

        if result.game_over:
            result_text = messages.game_result_text(result)
            for p in room.players.values():
                try:
                    await bot.send_message(
                        p.id,
                        result_text,
                        reply_markup=keyboards.game_over_kb(room, p.id),
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(f"Failed to send game result to {p.id}: {e}")
        else:
            # A spy was kicked, but more spies remain!
            spy_text = messages.spy_eliminated_text(
                kicked_player=result.kicked_player,
                remaining_spies_count=len(result.remaining_spies),
                vote_counts=result.vote_counts,
                players=room.players,
            )
            for p in room.players.values():
                try:
                    kb = keyboards.voting_kb(room, p.id) if not p.is_kicked else None
                    await bot.send_message(
                        p.id,
                        spy_text,
                        reply_markup=kb,
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send spy elimination prompt to {p.id}: {e}"
                    )


@router.callback_query(lambda c: c.data == "play_again")
async def handle_play_again(
    callback: CallbackQuery,
    bot: Bot,
    room_manager: RoomManager,
    question_manager: QuestionManager,
):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room or not room.is_host(user.id):
        await callback.answer(
            "Тільки хост може розпочати новий раунд.", show_alert=True
        )
        return

    room.reset_for_next_round()
    min_required = room.spy_count + 1
    if len(room.players) < min_required:
        await callback.answer(
            f"Недостатньо гравців для старту! Потрібно мінімум {min_required}.",
            show_alert=True,
        )
        return

    success = room.start_round(question_manager)
    if not success:
        await callback.answer("Помилка старту раунду.", show_alert=True)
        return

    await callback.answer("🔄 Розпочато новий раунд!")

    # Distribute questions to all players
    for p in room.players.values():
        try:
            await bot.send_message(
                p.id,
                messages.question_prompt_text(p.question),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send question to player {p.id}: {e}")


@router.callback_query(lambda c: c.data == "refresh_game_over")
async def handle_refresh_game_over(callback: CallbackQuery, room_manager: RoomManager):
    user = callback.from_user
    room = room_manager.get_player_room(user.id)
    if not room:
        await callback.answer("Кімнату не знайдено.")
        return

    if room.phase == GamePhase.LOBBY:
        await callback.answer("Хост повернувся до лобі. Оновіть меню через /start.")
    else:
        await callback.answer("Очікуємо рішення хоста...")
