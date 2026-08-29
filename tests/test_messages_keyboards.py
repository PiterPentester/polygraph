from bot import keyboards, messages
from game.models import GameResult, Player
from game.room import Room


def test_message_formatting():
    room = Room(code="AB12CD", host_id=1)
    p1 = Player(id=1, full_name="Host User", username="host")
    p2 = Player(id=2, full_name="Spy Player", username="spy")
    p3 = Player(id=3, full_name="Innocent Player")
    room.add_player(p1)
    room.add_player(p2)
    room.add_player(p3)

    lobby_msg = messages.lobby_text(room, bot_username="spy_game_bot")
    assert "AB12CD" in lobby_msg
    assert "@host" in lobby_msg
    assert "👑 (Хост)" in lobby_msg
    assert "t.me/spy_game_bot?start=AB12CD" in lobby_msg

    room.main_question = "Яка твоя улюблена страва?"
    p1.answer = "Піца"
    p2.answer = "Чай"
    p3.answer = "Паста"

    reveal_msg = messages.answers_reveal_text(room)
    assert "Яка твоя улюблена страва?" in reveal_msg
    assert "Піца" in reveal_msg
    assert "Чай" in reveal_msg
    assert "Паста" in reveal_msg

    # Result message formatting
    result = GameResult(
        innocents_won=True,
        spies=[p2],
        innocents=[p1, p3],
        kicked_player=p2,
        vote_counts={2: 2, 1: 1},
        main_question="Яка твоя улюблена страва?",
        spy_question="Який твій улюблений напій?",
    )
    res_msg = messages.game_result_text(result)
    assert "Перемога мирних жителів!" in res_msg
    assert "Spy Player" in res_msg
    assert "Який твій улюблений напій?" in res_msg


def test_keyboard_generation():
    room = Room(code="AB12CD", host_id=1)
    p1 = Player(id=1, full_name="Host User", username="host")
    p2 = Player(id=2, full_name="Player Two")
    p3 = Player(id=3, full_name="Player Three")
    room.add_player(p1)
    room.add_player(p2)
    room.add_player(p3)

    # Host lobby keyboard has start and config buttons
    host_kb = keyboards.lobby_kb(room, user_id=1)
    callback_datas = [
        btn.callback_data for row in host_kb.inline_keyboard for btn in row
    ]
    assert "start_game" in callback_datas
    assert "change_spies" in callback_datas
    assert "change_category" in callback_datas
    assert "kick_player_menu" in callback_datas
    assert "leave_room" in callback_datas

    # Non-host lobby keyboard has no start button
    guest_kb = keyboards.lobby_kb(room, user_id=2)
    guest_datas = [btn.callback_data for row in guest_kb.inline_keyboard for btn in row]
    assert "start_game" not in guest_datas
    assert "leave_room" in guest_datas

    # Spy count keyboard
    spy_kb = keyboards.spy_count_kb(room)
    spy_datas = [btn.callback_data for row in spy_kb.inline_keyboard for btn in row]
    assert "set_spies:1" in spy_datas
    assert "set_spies:2" in spy_datas

    # Voting keyboard - voter 1 cannot vote for voter 1
    vote_kb = keyboards.voting_kb(room, voter_id=1)
    vote_datas = [btn.callback_data for row in vote_kb.inline_keyboard for btn in row]
    assert "vote:1" not in vote_datas
    assert "vote:2" in vote_datas
    assert "vote:3" in vote_datas

    # Game over keyboard
    game_over_host = keyboards.game_over_kb(room, user_id=1)
    go_datas = [
        btn.callback_data for row in game_over_host.inline_keyboard for btn in row
    ]
    assert "play_again" in go_datas


def test_category_keyboard():
    categories = ["Food", "Hobbies", "Movies"]
    cat_kb = keyboards.category_kb(categories, current_category="Hobbies")
    cat_datas = [btn.callback_data for row in cat_kb.inline_keyboard for btn in row]
    assert "set_category:__random__" in cat_datas
    assert "set_category:Food" in cat_datas
    assert "set_category:Hobbies" in cat_datas
    assert "set_category:Movies" in cat_datas
    assert "back_to_lobby" in cat_datas
