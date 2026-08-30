from game.models import GameResult, Player
from game.room import Room


def welcome_text() -> str:
    return (
        "🕵️‍♂️ <b>Ласкаво просимо до гри «Шпигун» (Polygraph)!</b>\n\n"
        "<b>Правила гри:</b>\n"
        "1. Кожен гравець отримує запитання, на яке відповідає текстом.\n"
        "2. Шпигун(и) отримує <i>інше</i>, схоже запитання (і не знає, що він шпигун!).\n"
        "3. Після того, як усі дали відповіді, головне запитання та відповіді всіх відкриваються.\n"
        "4. Гравці голосують, кого вважають шпигуном. Якщо шпигунів декілька — мирні мають знайти їх усіх. Помилитеся або нічия — перемагають шпигуни!\n\n"
        "Натисніть кнопку нижче, щоб створити кімнату або приєднатися за кодом."
    )


def rules_text() -> str:
    return (
        "📖 <b>Детальні правила:</b>\n\n"
        "• <b>Лобі:</b> Хост створює кімнату та ділиться посиланням із друзями.\n"
        "• <b>Шпигуни:</b> Хост може встановити кількість шпигунів (від 1 до N-1).\n"
        "• <b>Раунд:</b> Усім надсилаються приватні запитання. Мирні отримують запитання А, шпигуни — запитання Б.\n"
        "• <b>Відповіді:</b> Напишіть коротку та правдоподібну відповідь боту в чат.\n"
        "• <b>Розкриття:</b> Бот публікує головне запитання та всі отримані відповіді.\n"
        "• <b>Голосування:</b> Знайдіть усіх шпигунів! Якщо вигнано шпигуна, а інші ще залишилися — голосування триває. Якщо вигнано мирного або нічия — перемагають шпигуни!"
    )


def lobby_text(room: Room, bot_username: str = "") -> str:
    lines = []
    for idx, p in enumerate(room.players.values(), 1):
        uname = f" (@{p.username})" if p.username else ""
        host_tag = " 👑 (Хост)" if room.is_host(p.id) else ""
        lines.append(f"  {idx}. {p.full_name}{uname}{host_tag}")
    players_list = "\n".join(lines)

    invite_link = (
        f"https://t.me/{bot_username}?start={room.code}"
        if bot_username
        else f"<code>{room.code}</code>"
    )

    category_str = room.category if room.category else "🎲 Випадкова (при старті)"

    return (
        f"🏠 <b>Кімната:</b> <code>{room.code}</code>\n"
        f"🔗 <b>Посилання для запрошення:</b>\n{invite_link}\n\n"
        f"👥 <b>Гравці ({len(room.players)}):</b>\n{players_list}\n\n"
        f"📂 <b>Категорія:</b> {category_str}\n"
        f"🕵️ <b>Кількість шпигунів:</b> {room.spy_count}\n"
        f"📦 <b>Зіграно запитань:</b> {len(room.used_question_ids)}\n\n"
        f"<i>Для старту потрібно щонайменше {room.spy_count + 1} гравців.</i>"
    )


def question_prompt_text(question: str) -> str:
    return (
        f"❓ <b>Ваше запитання:</b>\n\n"
        f"👉 <b>{question}</b>\n\n"
        f"✍️ <i>Будь ласка, напишіть вашу відповідь звичайним повідомленням сюди в чат:</i>"
    )


def answer_received_text(answer: str, answered_count: int, total_count: int) -> str:
    return (
        f"✅ <b>Вашу відповідь прийнято:</b>\n"
        f"«<i>{answer}</i>»\n\n"
        f"⏳ Очікуємо на інших гравців: <b>{answered_count}/{total_count}</b>..."
    )


def answers_reveal_text(room: Room) -> str:
    answers_formatted = "\n".join(
        [f"👤 <b>{p.full_name}</b>: «{p.answer}»" for p in room.players.values()]
    )

    return (
        f"📢 <b>Усі гравці надали відповіді!</b>\n\n"
        f"🎯 <b>Головне запитання раунду:</b>\n"
        f"👉 <b>{room.main_question}</b>\n\n"
        f"📝 <b>Відповіді гравців:</b>\n"
        f"{answers_formatted}\n\n"
        f"🗳️ <b>Час голосувати!</b> Хто із гравців відповів не на те запитання і є шпигуном?"
    )


def spy_eliminated_text(
    kicked_player: Player,
    remaining_spies_count: int,
    vote_counts: dict[int, int],
    players: dict[int, Player],
) -> str:
    votes_summary = "\n".join(
        [
            f"• {p.full_name}: {vote_counts.get(p.id, 0)} голос(ів)"
            for p in players.values()
            if not p.is_kicked or p.id == kicked_player.id
        ]
    )

    return (
        f"🎯 <b>Викрито шпигуна!</b>\n\n"
        f"Гравця <b>{kicked_player.full_name}</b> було вигнано більшістю голосів, і він виявився <b>шпигуном</b>! 🕵️\n\n"
        f"⚠️ <b>У грі ще залишається {remaining_spies_count} шпигун(ів)!</b>\n"
        f"Голосування продовжується серед гравців, що залишилися. Знайдіть решту шпигунів!\n\n"
        f"📊 <b>Результати голосування:</b>\n{votes_summary}"
    )


def game_result_text(result: GameResult) -> str:
    spy_names = ", ".join([s.full_name for s in result.spies])

    if result.tied:
        outcome = "🤝 <b>Нічия / голоси розділилися!</b> Шпигуни уникнули покарання."
    elif result.innocents_won:
        if len(result.spies) > 1:
            outcome = f"🏆 <b>Перемога мирних жителів!</b>\nУсіх шпигунів ({spy_names}) було успішно викрито!"
        else:
            outcome = f"🏆 <b>Перемога мирних жителів!</b>\nШпигуна <b>{result.kicked_player.full_name}</b> було успішно викрито!"
    else:
        kicked_name = (
            result.kicked_player.full_name if result.kicked_player else "невідомого"
        )
        outcome = f"💀 <b>Шпигуни перемогли!</b>\nБуло помилково вигнано мирного гравця: <b>{kicked_name}</b>."

    votes_summary = "\n".join(
        [
            f"• {p.full_name}: {result.vote_counts.get(p.id, 0)} голос(ів)"
            for p in (result.innocents + result.spies)
        ]
    )

    return (
        f"🏁 <b>Результати раунду:</b>\n\n"
        f"{outcome}\n\n"
        f"🕵️ <b>Шпигун(и):</b> {spy_names}\n"
        f"❓ <b>Запитання шпигуна було:</b>\n«<i>{result.spy_question}</i>»\n\n"
        f"🎯 <b>Головне запитання було:</b>\n«<i>{result.main_question}</i>»\n\n"
        f"📊 <b>Підсумок голосування:</b>\n{votes_summary}"
    )
