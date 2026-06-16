from game.board import Board
from game.rules import is_win
from game.types import GameStatus, Position, RevealResult
from generator.random_generator import generate_board
import time

from solver.hints import get_solve_step


class GameState:
    def __init__(self, width: int, height: int, mine_count: int, no_check: bool):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.no_check = no_check

        self.board = Board(width, height, mine_count)
        self.status = GameStatus.NOT_STARTED
        self.start_time = None
        self.end_time = None
        self.hint = None
        self.hint_count = 0

    def reveal_cell(self, pos: Position) -> RevealResult:
        if self.status == GameStatus.NOT_STARTED:
            self.board = generate_board(self.width, self.height, self.mine_count, pos, self.no_check)
            self.start_time = time.time()

        if self.status in {GameStatus.WON, GameStatus.LOST}:
            return RevealResult.IGNORED

        self.status = GameStatus.RUNNING

        result, revealed = self.board.reveal(pos)

        if result == RevealResult.HIT_MINE:
            self.status = GameStatus.LOST
            self.board.reveal_all_mines()
            return RevealResult.HIT_MINE

        if is_win(self.board):
            self.status = GameStatus.WON
            return RevealResult.WON

        return result

    def toggle_hint(self, reset : bool = False) -> None:
        if self.status in {GameStatus.WON, GameStatus.LOST, GameStatus.NOT_STARTED}:
            return
        if self.hint:
            if reset:
                self.toggle_highlight(self.hint.position)
                self.hint = None
            return
        self.hint_count += 1
        self.hint = get_solve_step(board=self.board)
        self.toggle_highlight(self.hint.position)


    def toggle_highlight(self, pos: Position|None) -> None:
        if self.status in {GameStatus.WON, GameStatus.LOST} or not pos:
            return
        cell = self.board.get_cell(pos)
        if cell.is_flagged or cell.is_revealed:
            cell.is_hidden = False
        cell.is_highlight = not cell.is_highlight

    def toggle_flag(self, pos: Position) -> None:
        if self.status in {GameStatus.WON, GameStatus.LOST} or self.board.remaining_flags() == 0 and not self.board.get_cell(pos).is_flagged:
            return
        self.board.toggle_flag(pos)

    def reset(self) -> None:
        self.board = Board(self.width, self.height, self.mine_count)
        self.status = GameStatus.NOT_STARTED
        self.start_time = None
        self.end_time = None
        self.hint = None
        self.hint_count = 0

    def current_time(self) -> str:
        if not self.start_time:
            return "00:00"
        time_spent = time.time() - self.start_time
        minutes, seconds = divmod(time_spent, 60)
        time_spent_after_first_click = f"{int(minutes):02d}:{int(seconds):02d}"
        if self.status in {GameStatus.WON, GameStatus.LOST}:
            if not self.end_time:
                self.end_time = time_spent_after_first_click

            return self.end_time if self.status == GameStatus.WON else f"DNF: It took {self.end_time} to lose."

        return f"{int(minutes):02d}:{int(seconds):02d}"

    def check_hint_status(self) -> None:
        if self.status in {GameStatus.WON, GameStatus.LOST}:
            return
        if self.hint:
            hint_cell = self.board.get_cell(self.hint.position)
            if hint_cell.is_flagged or hint_cell.is_revealed:
                self.toggle_hint(True)
