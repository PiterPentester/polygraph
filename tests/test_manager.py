from game.manager import RoomManager
from game.models import Player


def test_room_manager_create_and_find():
    manager = RoomManager()
    host = Player(id=12345, full_name="Alice")

    room = manager.create_room(host=host)
    assert room is not None
    assert len(room.code) == 6
    assert room.host_id == 12345
    assert 12345 in room.players

    # Lookup by code
    found = manager.get_room(room.code)
    assert found == room

    # Lookup by player id
    player_room = manager.get_player_room(12345)
    assert player_room == room

    # Join another player
    p2 = Player(id=67890, full_name="Bob")
    assert manager.join_room(room.code, p2) is True
    assert manager.get_player_room(67890) == room

    # Leave room
    manager.leave_room(67890)
    assert manager.get_player_room(67890) is None
    assert len(room.players) == 1

    # Close room
    manager.close_room(room.code)
    assert manager.get_room(room.code) is None
    assert manager.get_player_room(12345) is None


def test_room_manager_cleanup_stale_rooms():
    manager = RoomManager()
    host1 = Player(id=1, full_name="User 1")
    host2 = Player(id=2, full_name="User 2")
    host3 = Player(id=3, full_name="User 3")

    room1 = manager.create_room(host1)
    room2 = manager.create_room(host2)
    room3 = manager.create_room(host3)

    # Join player 4 to room 1
    p4 = Player(id=4, full_name="User 4")
    manager.join_room(room1.code, p4)

    # Make room1 and room2 stale (> 6 hours)
    room1.updated_at = room1.created_at - (6 * 3600 + 10)
    room2.updated_at = room2.created_at - (6 * 3600 + 10)

    # room3 remains fresh
    room3.touch()

    # Add an orphaned entry to player_to_room for testing memory leak prevention
    manager.player_to_room[999] = "NONEXISTENT"

    # Run cleanup
    cleaned = manager.cleanup_stale_rooms(max_age_seconds=6 * 3600)

    assert set(cleaned) == {room1.code, room2.code}
    assert manager.get_room(room1.code) is None
    assert manager.get_room(room2.code) is None
    assert manager.get_room(room3.code) == room3

    # Ensure player_to_room mapping is cleaned
    assert manager.get_player_room(1) is None
    assert manager.get_player_room(2) is None
    assert manager.get_player_room(4) is None
    assert manager.get_player_room(3) == room3
    assert 999 not in manager.player_to_room
