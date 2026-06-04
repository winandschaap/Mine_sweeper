from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    x: int
    y: int

class GameStatus(Enum):
    NOT_STARTED = 'not_started'
    RUNNING = 'running'
    WON = 'won'
    LOST = 'lost'

class RevealResult(Enum):
    IGNORED = 'ignored'
    REVEALED = 'revealed'
    HIT_MINE = 'hit mine'
    WON = 'won'
