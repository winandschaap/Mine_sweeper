from game.board import Board
from game.types import RevealResult
from game.types import Position
from solver.basic_solver import find_basic_actions
from game.rules import is_win
from solver.frontier import refresh_frontier_position, generate_frontier
from solver.subset_solver import find_subset_actions
from solver.types import SolverActionType, SolverAction
from copy import deepcopy

subset_counter = 0
def apply_action(action: SolverAction, board: Board, frontier: set[Position]) -> bool:
    cell = board.get_cell(action.position)
    if action.action_type == SolverActionType.FLAG:
        if cell.is_revealed:
#            print(f'BAD FLAG ACTION: Cell is revealed {action.position}')
            return False
        if cell.is_flagged:
#            print(f'USELESS FLAG ACTION: cell already flagged {action.position}')
            return True

        board.toggle_flag(action.position)

        for nb in board.neighbors(action.position):
            refresh_frontier_position(board, nb, frontier)

        return True


    if action.action_type == SolverActionType.OPEN:
        if cell.is_revealed:
#            print(f'BAD OPEN ACTION: cell already opened {action.position}')
            return True

        if cell.is_flagged:
#            print(f'BAD OPEN ACTION: cell is flagged {action.position}')
            return False

        result, revealed_positions = board.reveal(action.position)

        if result == RevealResult.HIT_MINE:
            return False

        for revealed_position in revealed_positions:
            refresh_frontier_position(board, revealed_position, frontier)

            for nb in board.neighbors(revealed_position):
                refresh_frontier_position(board, nb, frontier)

        return True

    raise ValueError(f"Unknown action type: {action.action_type}")

def find_actions(board: Board, frontier: set[Position]) -> list[SolverAction]:
    actions = find_basic_actions(board, frontier)
    if actions:
        return actions
#    print(f'Subset_finder_used')
    global subset_counter
    subset_counter += 1
    return find_subset_actions(board, frontier)


def is_solvable_by_basic_rules(possible_board: Board) -> bool:
    board = deepcopy(possible_board)
    frontier = generate_frontier(possible_board)
    counter = 0
    global subset_counter
    subset_counter = 0
    while not is_win(board):
        counter += 1
#        before = board_progress(board)
        actions = find_actions(board, frontier)
#        print(f'{counter}, progress: {before}')
        if not actions:
#            print(f'Failure took {counter} iterations of basic rules')
            return False

        for action in actions:
            if not apply_action(action, board, frontier):
                return False

    print(f'Generation took {counter} iterations of basic rules.\nSubset finder was used {subset_counter} times.')
    return True
#        after = board_progress(board)

#        if after == before:
#            print('Solver found actions, but none changed the board')
#            return False


def board_progress(board: Board) -> tuple[int, int]:
    revealed = 0
    flagged = 0

    for y in range(board.height):
        for x in range(board.width):
            cell = board.get_cell(Position(x, y))

            if cell.is_revealed:
                revealed += 1

            if cell.is_flagged:
                flagged += 1

    return revealed, flagged





