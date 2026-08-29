import logging
import random
import time
from game.models import GamePhase, GameResult, Player
from game.questions import QuestionManager

logger = logging.getLogger(__name__)


class Room:
    def __init__(self, code: str, host_id: int):
        self.code = code
        self.host_id = host_id
        self.players: dict[int, Player] = {}
        self.spy_count: int = 1
        self.category: str | None = None
        self.phase: GamePhase = GamePhase.LOBBY
        self.used_question_ids: set[str] = set()
        self.main_question: str = ""
        self.spy_question: str = ""
        self.last_result: GameResult | None = None
        self.created_at: float = time.time()
        self.updated_at: float = time.time()

    def touch(self) -> None:
        self.updated_at = time.time()

    def is_stale(
        self, max_age_seconds: float = 6 * 3600, current_time: float | None = None
    ) -> bool:
        now = current_time if current_time is not None else time.time()
        return (now - self.updated_at) >= max_age_seconds

    def is_host(self, player_id: int) -> bool:
        return self.host_id == player_id

    def add_player(self, player: Player) -> bool:
        if player.id in self.players:
            return False
        if self.phase != GamePhase.LOBBY and self.phase != GamePhase.GAME_OVER:
            return False
        self.players[player.id] = player
        self.touch()
        return True

    def remove_player(self, player_id: int) -> bool:
        if player_id not in self.players:
            return False
        del self.players[player_id]

        # If host leaves and there are other players, elect new host
        if self.host_id == player_id and self.players:
            self.host_id = next(iter(self.players.keys()))

        # Adjust spy count if player count dropped
        if len(self.players) > 1 and self.spy_count >= len(self.players):
            self.spy_count = max(1, len(self.players) - 1)

        self.touch()
        return True

    def set_spy_count(self, count: int) -> bool:
        if count < 1:
            return False
        if len(self.players) > 0 and count >= len(self.players):
            return False
        self.spy_count = count
        self.touch()
        return True

    def set_category(self, category: str | None) -> None:
        self.category = category
        self.touch()

    def start_round(self, question_manager: QuestionManager) -> bool:
        if len(self.players) < 3:
            logger.warning(
                f"Room {self.code} needs at least 3 players to start (has {len(self.players)})."
            )
            # For testing with 2 players we still allow if spy_count < len(players)
            if len(self.players) <= self.spy_count:
                return False

        pair = question_manager.get_random_pair(
            used_ids=self.used_question_ids, category=self.category
        )
        self.used_question_ids.add(pair.id)
        if self.category is None:
            self.category = pair.category
        self.main_question = pair.main_question
        self.spy_question = pair.spy_question

        # Reset player round states
        player_list = list(self.players.values())
        for p in player_list:
            p.is_spy = False
            p.answer = None
            p.voted_for = None
            p.question = ""

        # Select spies
        spy_count = min(self.spy_count, len(player_list) - 1)
        spies = random.sample(player_list, spy_count)
        for spy in spies:
            spy.is_spy = True
            spy.question = self.spy_question

        for p in player_list:
            if not p.is_spy:
                p.question = self.main_question

        self.phase = GamePhase.QUESTIONING
        self.last_result = None
        self.touch()
        return True

    def submit_answer(self, player_id: int, answer: str) -> bool:
        if self.phase != GamePhase.QUESTIONING:
            return False
        if player_id not in self.players:
            return False

        player = self.players[player_id]
        player.answer = answer.strip()
        self.touch()
        return True

    def all_answers_submitted(self) -> bool:
        return len(self.players) > 0 and all(
            p.answer is not None for p in self.players.values()
        )

    def start_voting(self) -> None:
        self.phase = GamePhase.VOTING
        for p in self.players.values():
            p.voted_for = None
        self.touch()

    def cast_vote(self, voter_id: int, target_id: int) -> bool:
        if self.phase != GamePhase.VOTING:
            return False
        if voter_id not in self.players or target_id not in self.players:
            return False
        if voter_id == target_id:
            return False

        self.players[voter_id].voted_for = target_id
        self.touch()
        return True

    def all_votes_cast(self) -> bool:
        return len(self.players) > 0 and all(
            p.voted_for is not None for p in self.players.values()
        )

    def resolve_votes(self) -> GameResult:
        vote_counts: dict[int, int] = {pid: 0 for pid in self.players}
        for voter in self.players.values():
            if voter.voted_for and voter.voted_for in vote_counts:
                vote_counts[voter.voted_for] += 1

        # Find max votes
        max_votes = max(vote_counts.values()) if vote_counts else 0
        top_suspects = [pid for pid, count in vote_counts.items() if count == max_votes]

        spies = [p for p in self.players.values() if p.is_spy]
        innocents = [p for p in self.players.values() if not p.is_spy]

        # If tie for top votes or no votes, spies win due to indecision
        if len(top_suspects) != 1 or max_votes == 0:
            result = GameResult(
                innocents_won=False,
                spies=spies,
                innocents=innocents,
                kicked_player=None,
                vote_counts=vote_counts,
                main_question=self.main_question,
                spy_question=self.spy_question,
                tied=True,
            )
        else:
            kicked_id = top_suspects[0]
            kicked_player = self.players[kicked_id]
            innocents_won = kicked_player.is_spy

            result = GameResult(
                innocents_won=innocents_won,
                spies=spies,
                innocents=innocents,
                kicked_player=kicked_player,
                vote_counts=vote_counts,
                main_question=self.main_question,
                spy_question=self.spy_question,
                tied=False,
            )

        self.last_result = result
        self.phase = GamePhase.GAME_OVER
        self.touch()
        return result

    def reset_for_next_round(self) -> None:
        self.phase = GamePhase.LOBBY
        for p in self.players.values():
            p.is_spy = False
            p.answer = None
            p.voted_for = None
            p.question = ""
        self.main_question = ""
        self.spy_question = ""
        self.last_result = None
        self.touch()
