from game.board import Board
from solver.types import SolverAction, SolverUsed, SolverActionType
from solver.solver_engine import find_actions
from solver.frontier import generate_frontier
from game.types import Position

def get_solve_step(board: Board) -> SolverAction:
    current_state = check_correctness_state(board)
    if not current_state[0]:
        return SolverAction(current_state[1], SolverActionType.UNFLAG, None)

    frontier = generate_frontier(board)
    actions = find_actions(board, frontier)

    return actions[0] if actions else SolverAction(None, SolverActionType.NO_MOVE_FOUND, None)

def hint_text(action: SolverAction) -> str:
    if action.solver_type == SolverUsed.BASIC:
        return 'What is the only possibility?'
    if action.solver_type == SolverUsed.SUBSET:
        return 'Use subset reasoning'
    if action.action_type == SolverActionType.UNFLAG:
        return 'This cell is incorrectly flagged'
    return 'No logical hint was found'

def check_correctness_state(board: Board) -> tuple[bool, Position | None]:
    for x in range(board.width):
        for y in range(board.height):
            pos = Position(x, y)
            cell = board.get_cell(pos)
            if cell is None:
                continue
            if cell.is_flagged and not cell.is_mine:
                return False, Position(x, y)
    return True, None