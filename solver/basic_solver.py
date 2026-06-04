from game.board import Board
from game.types import Position
from solver.types import SolverAction
from solver.types import SolverActionType

def find_basic_actions(board: Board, frontier: set[Position]) -> list[SolverAction]:
    actions = []

    for pos in frontier:
        cell = board.get_cell(pos)

        if not cell.is_revealed:
            continue

        for action in actions_from_number_cell(board, pos):
            if action not in actions:
                actions.append(action)
    return actions

def actions_from_number_cell(board: Board, pos: Position) -> list[SolverAction]:
    cell = board.get_cell(pos)
    if not cell.is_revealed:
        return []

    neighbors = board.neighbors(pos)


    unknown_neighbors = [
        nb for nb in neighbors
        if not board.get_cell(nb).is_revealed
        and not board.get_cell(nb).is_flagged
    ]

    actions = []

    if len(unknown_neighbors) == cell.neighbor_mines - cell.neighbors_flagged:
        for nb in unknown_neighbors:
            actions.append(SolverAction(nb, SolverActionType.FLAG))

    if cell.neighbors_flagged == cell.neighbor_mines:
        for nb in unknown_neighbors:
            actions.append(SolverAction(nb, SolverActionType.OPEN))
    return actions