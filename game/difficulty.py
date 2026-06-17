from dataclasses import dataclass

@dataclass(frozen=True)
class BoardSize:
    name: str
    width: int
    height: int

@dataclass(frozen=True)
class Difficulty:
    name: str
    density: float

BOARD_SIZES = {
    "small": BoardSize("Small", 8, 5),
    "medium": BoardSize("Medium", 16, 10),
    "large": BoardSize("Large", 24, 15),
    "huge": BoardSize("Huge", 32, 20)
}

DIFFICULTIES = {
    "easy": Difficulty("Easy", 0.10),
    "normal": Difficulty("Normal", 0.15),
    "hard": Difficulty("Hard", 0.20),
    "brutal": Difficulty("Brutal", 0.23),
}

def mine_count_for_difficulty(board_size: BoardSize, difficulty: Difficulty) -> int:
    cells = board_size.width * board_size.height
    mines = round(cells * difficulty.density)

    max_mines = cells - 9

    return min(max_mines, mines)