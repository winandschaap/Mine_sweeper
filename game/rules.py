from game.board import Board
from game.types import Position

def is_win(board: Board) -> bool:
    return board.all_safe_cells_revealed()

def closed_neighbors(board: Board, pos: Position) -> list[Position]:
    return [
        new_pos for new_pos in board.neighbors(pos)
        if not board.get_cell(new_pos).is_revealed
    ]

def flagged_neighbors(board: Board, pos: Position) -> list[Position]:
    return [
        new_pos for new_pos in board.neighbors(pos)
        if board.get_cell(new_pos).is_flagged
    ]

def hidden_unflagged_neighbors(board: Board, pos: Position) -> list[Position]:
    return [
        new_pos for new_pos in board.neighbors(pos)
        if not board.get_cell(new_pos).is_revealed
        and not board.get_cell(new_pos).is_flagged
    ]

