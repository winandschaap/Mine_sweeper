from dataclasses import dataclass

@dataclass
class Cell:
    is_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    is_highlight: bool = False
    neighbor_mines: int = 0
    neighbor_revealed: int = 0
    neighbors_flagged: int = 0