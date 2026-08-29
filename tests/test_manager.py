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
