from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from game.room import Room


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Створити кімнату", callback_data="create_room"
                )
            ],
            [InlineKeyboardButton(text="📖 Правила гри", callback_data="show_rules")],
        ]
    )


def lobby_kb(room: Room, user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    is_host = room.is_host(user_id)

    if is_host:
        buttons.append(
            [InlineKeyboardButton(text="▶️ Почати гру", callback_data="start_game")]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🕵️ К-сть шпигунів", callback_data="change_spies"
                ),
                InlineKeyboardButton(
                    text="📂 Категорія", callback_data="change_category"
                ),
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="👢 Вигнати гравця", callback_data="kick_player_menu"
                ),
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(text="🔄 Оновити", callback_data="refresh_lobby"),
            InlineKeyboardButton(text="🚪 Вийти", callback_data="leave_room"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def spy_count_kb(room: Room) -> InlineKeyboardMarkup:
    max_spies = max(1, len(room.players) - 1)
    buttons = []
    row = []
    for count in range(1, max_spies + 1):
        label = f"🕵️ {count}" + (" ✅" if count == room.spy_count else "")
        row.append(InlineKeyboardButton(text=label, callback_data=f"set_spies:{count}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад до лобі", callback_data="back_to_lobby")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def category_kb(
    categories: list[str], current_category: str | None
) -> InlineKeyboardMarkup:
    buttons = []
    random_label = "🎲 Випадкова" + (" ✅" if current_category is None else "")
    buttons.append(
        [
            InlineKeyboardButton(
                text=random_label, callback_data="set_category:__random__"
            )
        ]
    )

    row = []
    for cat in categories:
        label = f"📁 {cat}" + (" ✅" if current_category == cat else "")
        row.append(
            InlineKeyboardButton(text=label, callback_data=f"set_category:{cat}")
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад до лобі", callback_data="back_to_lobby")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kick_player_kb(room: Room) -> InlineKeyboardMarkup:
    buttons = []
    for p in room.players.values():
        if not room.is_host(p.id):
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"👢 {p.full_name}", callback_data=f"kick:{p.id}"
                    )
                ]
            )
    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад до лобі", callback_data="back_to_lobby")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def voting_kb(room: Room, voter_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for p in room.players.values():
        # Prevent self-voting and voting for kicked players
        if p.id == voter_id or p.is_kicked:
            continue
        status = (
            " (Ваш вибір)"
            if room.players.get(voter_id) and room.players[voter_id].voted_for == p.id
            else ""
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🗳️ {p.full_name}{status}", callback_data=f"vote:{p.id}"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def game_over_kb(room: Room, user_id: int) -> InlineKeyboardMarkup:
    buttons = []
    if room.is_host(user_id):
        buttons.append(
            [InlineKeyboardButton(text="🔄 Зіграти ще раз", callback_data="play_again")]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="⚙️ Налаштування лобі", callback_data="back_to_lobby"
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="⏳ Очікування хоста...", callback_data="refresh_game_over"
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="🚪 Вийти з кімнати", callback_data="leave_room")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
