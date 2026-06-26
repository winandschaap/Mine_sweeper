from enum import Enum
from dataclasses import dataclass
from game.types import Position


class SolverActionType(Enum):
    OPEN = 'open'
    FLAG = 'flag'
    NO_MOVE_FOUND = 'no_move_found'
    UNFLAG = 'unflag'

class SolverUsed(Enum):
    BASIC = 'basic'
    SUBSET = 'subset'

@dataclass(frozen=True)
class SolverAction:
    position : Position | None
    action_type : SolverActionType
    solver_type : SolverUsed | None = SolverUsed.BASIC

@dataclass(frozen=True)
class Constraint:
    cells: frozenset[Position]
    mine_count: int