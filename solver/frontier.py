from game.board import Board
from game.types import Position


def is_frontier_cell(board: Board, pos: Position) -> bool:

    cell = board.get_cell(pos)

    if not cell.is_revealed:
        return False

    if cell.neighbor_mines == 0:
        return False

    return any(
        not board.get_cell(nb).is_revealed
        and not board.get_cell(nb).is_flagged
        for nb in board.neighbors(pos)
    )

def refresh_frontier_position(board: Board, pos: Position, frontier: set[Position]) -> None:
    if is_frontier_cell(board, pos):
        frontier.add(pos)
    else:
        frontier.discard(pos)

