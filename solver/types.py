from enum import Enum
from dataclasses import dataclass
from game.types import Position


class SolverActionType(Enum):
    OPEN = 'open'
    FLAG = 'flag'
    NO_MOVE_FOUND = 'no_move_found'

@dataclass(frozen=True)
class SolverAction:
    position : Position
    action_type : SolverActionType

@dataclass(frozen=True)
class Constraint:
    cells: frozenset[Position]
    mine_count: int