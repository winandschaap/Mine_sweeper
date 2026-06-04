from game.types import Position
from game.board import Board
from solver.solver_engine import is_solvable_by_basic_rules
import time

def generate_board(width: int, height: int, mine_count: int, initial_pos: Position, no_check: bool = False) -> Board:
    start = time.time()
    c = 0
    while True:
        c += 1
        board = Board(width, height, mine_count)
        board.reveal(initial_pos)
        if no_check:
            return board

        if is_solvable_by_basic_rules(board):
            print(f'Generation took {time.time()-start:.3f} seconds and {c} attempts.')
            return board