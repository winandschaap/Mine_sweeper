from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Callable
from functools import partial

import pygame

from game.difficulty import BoardSize, Difficulty
from ui.button import Button


@dataclass
class MenuOption:
    label: str
    value: BoardSize | Difficulty

class ScreenState(Enum):
    BOARD_SIZE = auto()
    DIFFICULTY = auto()
    GAME = auto()

BOARD_SIZES = {
    "small": BoardSize("Small", 8, 5),
    "medium": BoardSize("Medium", 16, 9),
    "large": BoardSize("Large", 24, 15),
    "huge": BoardSize("Huge", 32, 18)
}

DIFFICULTIES = {
    "easy": Difficulty("Easy", 0.10),
    "normal": Difficulty("Normal", 0.15),
    "hard": Difficulty("Hard", 0.20),
    "brutal": Difficulty("Brutal", 0.23),
}

def create_menu_options() -> list[MenuOption]:
    options_list = []
    for key, value in BOARD_SIZES.items():
        options_list.append(MenuOption(key, value))
    for key,value in DIFFICULTIES.items():
        options_list.append(MenuOption(key, value))
    return options_list


def create_menu_buttons(
        options: List[MenuOption],
        screen_width: int,
        screen_height: int,
        font: pygame.font.Font,
        on_select: Callable[[object], None]
) -> list[Button]:
    buttons: list[Button] = []

    number_buttons: int = len(options)

    if not number_buttons:
        return buttons

    button_rects: list[pygame.Rect] = _get_button_rects(number_buttons, screen_width, screen_height)

    for rect, option in zip(button_rects, options):
        buttons.append(
            Button(
                rect,
                option.label,
                font,
                partial(on_select, option)
            )
        )

    return buttons

def _get_button_rects(
        number_buttons: int,
        screen_width: int,
        screen_height: int
) -> list[pygame.Rect]:
    if not number_buttons:
        return []
    button_height, button_width = _get_button_dimensions(number_buttons, screen_width, screen_height)

    rects: List[pygame.Rect] = []

    for i in range(number_buttons):
        rects.append(pygame.Rect((screen_width - button_width)//2, (2+ i*1.5)*button_height, button_width, button_height))

    return rects

def _get_button_dimensions(
        number_buttons: int,
        screen_width: int,
        screen_height: int
) -> tuple[int, int]:
    return screen_height // int(2+ number_buttons * 1.5 + 1), (2*screen_width) // 9

