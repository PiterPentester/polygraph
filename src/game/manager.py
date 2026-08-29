import logging
import random
import string
from game.models import Player
from game.room import Room

logger = logging.getLogger(__name__)


class RoomManager:
    def __init__(self):
        self.rooms: dict[str, Room] = {}
        self.player_to_room: dict[int, str] = {}

    def _generate_code(self, length: int = 6) -> str:
        characters = string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(characters, k=length))
            if code not in self.rooms:
                return code

    def create_room(self, host: Player) -> Room:
        # If host is already in a room, leave old room
        if host.id in self.player_to_room:
            self.leave_room(host.id)

        code = self._generate_code()
        room = Room(code=code, host_id=host.id)
        room.add_player(host)

        self.rooms[code] = room
        self.player_to_room[host.id] = code
        logger.info(f"Created room {code} with host {host.full_name} ({host.id})")
        return room

    def get_room(self, code: str) -> Room | None:
        return self.rooms.get(code.upper().strip())

    def get_player_room(self, player_id: int) -> Room | None:
        code = self.player_to_room.get(player_id)
        if code:
            return self.rooms.get(code)
        return None

    def join_room(self, code: str, player: Player) -> bool:
        room = self.get_room(code)
        if not room:
            return False

        if player.id in self.player_to_room:
            old_code = self.player_to_room[player.id]
            if old_code == room.code:
                # Already in this room, update info
                room.players[player.id] = player
                return True
            self.leave_room(player.id)

        success = room.add_player(player)
        if success:
            self.player_to_room[player.id] = room.code
        return success

    def leave_room(self, player_id: int) -> Room | None:
        code = self.player_to_room.pop(player_id, None)
        if not code or code not in self.rooms:
            return None

        room = self.rooms[code]
        room.remove_player(player_id)

        if len(room.players) == 0:
            self.close_room(code)
            return None

        return room

    def close_room(self, code: str) -> None:
        code = code.upper().strip()
        room = self.rooms.pop(code, None)
        if room:
            for pid in list(room.players.keys()):
                self.player_to_room.pop(pid, None)
            logger.info(f"Closed room {code}")

    def cleanup_stale_rooms(self, max_age_seconds: float = 6 * 3600) -> list[str]:
        stale_codes = [
            code
            for code, room in list(self.rooms.items())
            if room.is_stale(max_age_seconds)
        ]
        for code in stale_codes:
            logger.info(
                f"Cleaning up stale room {code} (inactive for > {max_age_seconds}s)"
            )
            self.close_room(code)

        # Cleanup any orphaned player_to_room references
        orphaned_ids = [
            pid
            for pid, rcode in list(self.player_to_room.items())
            if rcode not in self.rooms
        ]
        for pid in orphaned_ids:
            self.player_to_room.pop(pid, None)

        return stale_codes
