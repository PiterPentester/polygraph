import pytest
from game.models import GamePhase, Player
from game.questions import QuestionPair
from game.room import Room


@pytest.fixture
def mock_question_manager():
    class MockQM:
        def __init__(self):
            self.pairs = [
                QuestionPair(
                    id="q:1",
                    main_question="Main Q1",
                    spy_question="Spy Q1",
                    category="Test",
                ),
                QuestionPair(
                    id="q:2",
                    main_question="Main Q2",
                    spy_question="Spy Q2",
                    category="Test",
                ),
            ]
            self.idx = 0

        def get_random_pair(self, used_ids=None, category=None):
            pair = self.pairs[self.idx % len(self.pairs)]
            self.idx += 1
            return pair

    return MockQM()


def test_room_creation_and_players():
    room = Room(code="TEST01", host_id=100)
    host = Player(id=100, full_name="Host User", username="host")

    assert room.add_player(host) is True
    assert len(room.players) == 1
    assert room.is_host(100) is True

    p2 = Player(id=200, full_name="Player Two", username="p2")
    p3 = Player(id=300, full_name="Player Three", username="p3")
    assert room.add_player(p2) is True
    assert room.add_player(p3) is True
    assert len(room.players) == 3

    # Duplicate add
    assert room.add_player(p2) is False

    # Remove player
    assert room.remove_player(300) is True
    assert len(room.players) == 2


def test_spy_count_configuration():
    room = Room(code="TEST01", host_id=100)
    for uid in [100, 200, 300, 400]:
        room.add_player(Player(id=uid, full_name=f"Player {uid}"))

    assert room.set_spy_count(1) is True
    assert room.spy_count == 1

    assert room.set_spy_count(2) is True
    assert room.spy_count == 2

    # Cannot have spies >= player count or <= 0
    assert room.set_spy_count(4) is False
    assert room.set_spy_count(0) is False
    assert room.spy_count == 2


def test_gameplay_lifecycle_innocents_win(mock_question_manager):
    room = Room(code="TEST01", host_id=100)
    for uid in [100, 200, 300]:
        room.add_player(Player(id=uid, full_name=f"Player {uid}"))

    # Start round
    assert room.start_round(mock_question_manager) is True
    assert room.phase == GamePhase.QUESTIONING
    assert "q:1" in room.used_question_ids

    # Verify exactly 1 spy was chosen
    spies = [p for p in room.players.values() if p.is_spy]
    innocents = [p for p in room.players.values() if not p.is_spy]
    assert len(spies) == 1
    assert len(innocents) == 2

    spy = spies[0]
    assert spy.question == "Spy Q1"
    for inc in innocents:
        assert inc.question == "Main Q1"

    # Submit answers
    assert room.submit_answer(100, "Answer 100") is True
    assert room.all_answers_submitted() is False
    assert room.submit_answer(200, "Answer 200") is True
    assert room.submit_answer(300, "Answer 300") is True
    assert room.all_answers_submitted() is True

    # Transition to voting
    room.start_voting()
    assert room.phase == GamePhase.VOTING

    # Innocents vote for the spy, spy votes for an innocent
    for inc in innocents:
        assert room.cast_vote(voter_id=inc.id, target_id=spy.id) is True
    assert room.cast_vote(voter_id=spy.id, target_id=innocents[0].id) is True

    assert room.all_votes_cast() is True

    result = room.resolve_votes()
    assert result.innocents_won is True
    assert result.kicked_player.id == spy.id
    assert room.phase == GamePhase.GAME_OVER

    # Reset for next round
    room.reset_for_next_round()
    assert room.phase == GamePhase.LOBBY
    assert len(room.players) == 3
    # Used questions preserved
    assert "q:1" in room.used_question_ids


def test_gameplay_lifecycle_spy_wins_on_wrong_vote(mock_question_manager):
    room = Room(code="TEST02", host_id=100)
    for uid in [100, 200, 300]:
        room.add_player(Player(id=uid, full_name=f"Player {uid}"))

    room.start_round(mock_question_manager)
    spies = [p for p in room.players.values() if p.is_spy]
    innocents = [p for p in room.players.values() if not p.is_spy]
    innocent_target = innocents[0]
    other_players = [p for p in room.players.values() if p.id != innocent_target.id]

    for uid in [100, 200, 300]:
        room.submit_answer(uid, f"Ans {uid}")

    room.start_voting()

    # Other players mistakenly vote for innocent_target
    for p in other_players:
        assert room.cast_vote(voter_id=p.id, target_id=innocent_target.id) is True
    # innocent_target votes for the spy or someone else
    assert room.cast_vote(voter_id=innocent_target.id, target_id=spies[0].id) is True

    result = room.resolve_votes()
    assert result.innocents_won is False
    assert result.kicked_player.id == innocent_target.id


def test_prevent_self_vote():
    room = Room(code="TEST03", host_id=100)
    for uid in [100, 200, 300]:
        room.add_player(Player(id=uid, full_name=f"Player {uid}"))

    room.start_voting()
    # Cannot vote for self
    assert room.cast_vote(voter_id=100, target_id=100) is False
    # Can vote for another player
    assert room.cast_vote(voter_id=100, target_id=200) is True


def test_room_category_selection(mock_question_manager):
    room = Room(code="TEST04", host_id=100)
    for uid in [100, 200, 300]:
        room.add_player(Player(id=uid, full_name=f"Player {uid}"))

    assert room.category is None
    room.set_category("Test")
    assert room.category == "Test"

    room.start_round(mock_question_manager)
    assert room.category == "Test"


def test_room_timestamp_and_staleness():
    room = Room(code="STALE1", host_id=100)
    assert hasattr(room, "created_at")
    assert hasattr(room, "updated_at")
    assert room.created_at > 0
    assert room.updated_at >= room.created_at

    # Check is_stale
    assert room.is_stale(max_age_seconds=6 * 3600) is False

    # Simulate 6 hours + 1 second passing
    room.updated_at = room.created_at - (6 * 3600 + 1)
    assert room.is_stale(max_age_seconds=6 * 3600) is True

    # Calling touch should refresh updated_at
    room.touch()
    assert room.is_stale(max_age_seconds=6 * 3600) is False
