from dataclasses import dataclass
from enum import Enum


class GamePhase(str, Enum):
    LOBBY = "lobby"
    QUESTIONING = "questioning"
    VOTING = "voting"
    GAME_OVER = "game_over"


@dataclass
class QuestionPair:
    id: str
    main_question: str
    spy_question: str
    category: str = "General"


@dataclass
class Player:
    id: int
    full_name: str
    username: str | None = None
    is_spy: bool = False
    question: str = ""
    answer: str | None = None
    voted_for: int | None = None

    @property
    def display_name(self) -> str:
        if self.username:
            return f"@{self.username}"
        return self.full_name


@dataclass
class GameResult:
    innocents_won: bool
    spies: list[Player]
    innocents: list[Player]
    kicked_player: Player | None
    vote_counts: dict[int, int]
    main_question: str
    spy_question: str
    tied: bool = False
