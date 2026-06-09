import random
from collections import deque

from game.cell import Cell
from game.types import Position, RevealResult


class Board:
    def __init__(self, width: int, height: int, mine_count: int):
        if mine_count >= width * height:
            raise ValueError('mine count must be less than width * height')
        self.width: int = width
        self.height: int = height
        self.mine_count: int = mine_count
        self.grid: list[list[Cell]] = [
            [Cell() for _ in range(width)]
            for _ in range(height)
        ]

        self.mines_placed: bool = False

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def get_cell(self, pos: Position) -> Cell:
        if not self.in_bounds(pos):
            raise IndexError(f'Position out of bounds: {pos}')
        return self.grid[pos.y][pos.x]

    def neighbors(self, pos: Position) -> list[Position]:
        result = []

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = Position(pos.x + dx, pos.y + dy)

                if self.in_bounds(neighbor):
                    result.append(neighbor)
        return result

    def place_mines(self, first_click: Position) -> None:
        """
        Places mines after the first click.
        The first click and its neighbors stay safe.
        :param first_click: Position to indicate the first click.
        :return: None
        """
        forbidden = {first_click}
        forbidden.update(self.neighbors(first_click))

        possible_positions: list[Position] = [
            Position(x,y)
            for y in range(self.height)
            for x in range(self.width)
            if Position(x, y) not in forbidden
        ]


        if self.mine_count > len(possible_positions):
            raise ValueError('Too many mines for this board and first click rule')

        mine_position: list[Position] = random.sample(possible_positions, self.mine_count)

        for pos in mine_position:
            self.get_cell(pos).is_mine = True

        self._calculate_neighbor_counts()

        self.mines_placed = True

    def _calculate_neighbor_counts(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                pos = Position(x, y)
                cell = self.get_cell(pos)

                cell.neighbor_mines = sum(
                    1 for new_pos in self.neighbors(pos)
                    if self.get_cell(new_pos).is_mine
                )

    def reveal(self, pos: Position) -> tuple[RevealResult, set[Position]]:
        if not self.in_bounds(pos):
            return RevealResult.IGNORED, set()

        if not self.mines_placed:
            self.place_mines(pos)

        cell = self.get_cell(pos)

        if cell.is_revealed or cell.is_flagged:
            return RevealResult.IGNORED, set()

        if cell.is_mine:
            cell.is_revealed = True
            return RevealResult.HIT_MINE, set()

        revealed_positions = self._flood_reveal(pos)
        return RevealResult.REVEALED, revealed_positions

    def _flood_reveal(self, start: Position) -> set[Position]:
        revealed_positions: set[Position] = set()
        queue: deque[Position] = deque([start])

        while queue:
            pos = queue.popleft()
            cell = self.get_cell(pos)

            if cell.is_revealed or cell.is_flagged:
                continue

            cell.is_revealed = True
            revealed_positions.add(pos)

            if cell.neighbor_mines == 0:
                for neighbor in self.neighbors(pos):
                    neighbor_cell = self.get_cell(neighbor)

                    if not neighbor_cell.is_revealed and not neighbor_cell.is_flagged and not neighbor_cell.is_mine:
                        queue.append(neighbor)
        return revealed_positions

    def toggle_flag(self, pos: Position) -> None:
        if not self.in_bounds(pos):
            return

        cell = self.get_cell(pos)

        if cell.is_revealed:
            return

        cell.is_flagged = not cell.is_flagged
        for neighbor in self.neighbors(pos):
            nb_cell = self.get_cell(neighbor)
            if cell.is_flagged:
                nb_cell.neighbors_flagged += 1
            else:
                nb_cell.neighbors_flagged -= 1

    def generate_hint(self):
        pass

    def toggle_highlight(self, pos: Position) -> None:
        if not self.in_bounds(pos):
            return
        cell = self.get_cell(pos)
        if cell.is_flagged or cell.is_revealed:
            return
        cell.is_highlight = not cell.is_highlight

    def reveal_all_mines(self) -> None:
        for row in self.grid:
            for cell in row:
                if cell.is_mine:
                    cell.is_revealed = True

    def all_safe_cells_revealed(self) -> bool:
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False

        return True

    def flag_count(self) -> int:
        return sum(
            1 for row in self.grid
            for cell in row
            if cell.is_flagged
        )

    def remaining_flags(self) -> int:
        return self.mine_count - self.flag_count()

    def reset(self) -> None:
        self.grid: list[list[Cell]] = [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

