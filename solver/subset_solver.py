from game.types import Position
from game.board import Board
from solver.types import Constraint, SolverAction, SolverActionType


def build_constraints(board: Board, frontier: set[Position]) -> list[Constraint]:

    constraints = []

    for position in frontier:
        cell = board.get_cell(position)
        unknown = []
        flagged_count = cell.neighbors_flagged

        for nb in board.neighbors(position):
            nb_cell = board.get_cell(nb)

            if not nb_cell.is_flagged and not nb_cell.is_revealed:
                unknown.append(nb)

        remaining_mines = cell.neighbor_mines - flagged_count

        if not unknown or remaining_mines < 0 or remaining_mines > len(unknown):
            continue

        constraints.append(
            Constraint(
                cells = frozenset(unknown),
                mine_count=remaining_mines
            )
        )
    return constraints


def actions_from_constraint_pair(a: Constraint, b: Constraint) -> list[SolverAction]:
    actions = []

    if not a.cells < b.cells:
        return actions

    diff_cells = b.cells - a.cells
    diff_mines = b.mine_count - a.mine_count

    if diff_mines == 0:
        for pos in diff_cells:
            actions.append(SolverAction(pos, SolverActionType.OPEN))
    if diff_mines == len(diff_cells):
        for pos in diff_cells:
            actions.append(SolverAction(pos, SolverActionType.FLAG))

    return actions


def find_subset_actions(board: Board, frontier: set[Position]) -> list[SolverAction]:
    constraints = build_constraints(board, frontier)
    actions = []

    for a in constraints:
        for b in constraints:
            if a == b:
                continue

            new_actions = actions_from_constraint_pair(a, b)

            for action in new_actions:
                if action not in actions:
                    actions.append(action)
    return actions


