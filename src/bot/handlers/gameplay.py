import logging
from aiogram import Bot, Router
from aiogram.types import Message
from bot import keyboards, messages
from game.manager import RoomManager
from game.models import GamePhase

logger = logging.getLogger(__name__)
router = Router()


@router.message(lambda m: m.text and not m.text.startswith("/"))
async def handle_player_answer(message: Message, bot: Bot, room_manager: RoomManager):
    user = message.from_user
    if not user or not message.text:
        return

    room = room_manager.get_player_room(user.id)
    if not room or room.phase != GamePhase.QUESTIONING:
        # User sent a regular text message outside active questioning phase
        return

    # Submit answer
    success = room.submit_answer(user.id, message.text)
    if not success:
        await message.answer("❌ Не вдалося зберегти відповідь.")
        return

    answered_count = sum(1 for p in room.players.values() if p.answer is not None)
    total_count = len(room.players)

    await message.answer(
        messages.answer_received_text(
            answer=message.text,
            answered_count=answered_count,
            total_count=total_count,
        ),
        parse_mode="HTML",
    )

    # If all answers are received, reveal and start voting
    if room.all_answers_submitted():
        room.start_voting()
        reveal_msg = messages.answers_reveal_text(room)

        for p in room.players.values():
            try:
                await bot.send_message(
                    p.id,
                    reveal_msg,
                    reply_markup=keyboards.voting_kb(room, p.id),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.error(f"Failed to send voting prompt to {p.id}: {e}")
