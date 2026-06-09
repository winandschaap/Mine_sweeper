from game.board import Board
from solver.types import SolverAction, SolverUsed
from solver.solver_engine import find_actions
from solver.frontier import generate_frontier

def get_solve_step(board: Board) -> SolverAction:
    frontier = generate_frontier(board)
    actions = find_actions(board, frontier)
    return actions[0]

def hint_text(action: SolverAction) -> str:
    if action.solver_type == SolverUsed.BASIC:
        return 'What is the only possibility?'
    if action.solver_type == SolverUsed.SUBSET:
        return 'Use subset reasoning'
    return 'None'

