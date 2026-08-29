import asyncio
import pytest
from game.manager import RoomManager
from game.models import Player
from main import cleanup_stale_rooms_loop


@pytest.mark.asyncio
async def test_cleanup_stale_rooms_loop():
    manager = RoomManager()
    host = Player(id=10, full_name="Test Host")
    room = manager.create_room(host)

    # Set room to be stale
    room.updated_at = room.created_at - 100

    # Start loop with very short interval (0.05s) and ttl 10s
    task = asyncio.create_task(
        cleanup_stale_rooms_loop(manager, interval_seconds=0.05, ttl_seconds=10)
    )

    # Allow task to run at least one cycle
    await asyncio.sleep(0.12)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert manager.get_room(room.code) is None
    assert manager.get_player_room(10) is None
