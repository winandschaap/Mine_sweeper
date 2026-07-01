from typing import Callable

import pygame

from ui.button import Button


MIN_BUTTON_FONT_SIZE = 10


def _create_fitted_font(
        text: str,
        max_width: int,
        max_height: int,
        starting_size: int,
) -> pygame.font.Font:
    for font_size in range(starting_size, MIN_BUTTON_FONT_SIZE - 1, -1):
        font = pygame.font.SysFont(None, font_size)
        text_width, text_height = font.size(text)
        if text_width <= max_width and text_height <= max_height:
            return font

    return pygame.font.SysFont(None, MIN_BUTTON_FONT_SIZE)


def _create_topbar_button(
        text: str,
        screen_width: int,
        top_bar_height: int,
        row: int,
        on_click: Callable[[], None],
) -> Button:
    margin = max(4, top_bar_height // 10)
    gap = max(2, top_bar_height // 16)
    button_height = max(12, (top_bar_height - 2 * margin - gap) // 2)
    button_width = min(
        max(1, screen_width - 2 * margin),
        max(48, min(screen_width // 3, (11 * top_bar_height) // 5)),
    )

    x = screen_width - margin - button_width
    y = margin + row * (button_height + gap)

    padding_x = max(4, button_width // 10)
    padding_y = max(2, button_height // 6)
    font = _create_fitted_font(
        text,
        max(1, button_width - 2 * padding_x),
        max(1, button_height - 2 * padding_y),
        max(MIN_BUTTON_FONT_SIZE, (3 * button_height) // 4),
    )

    return Button(
        rect = pygame.Rect(x, y, button_width, button_height),
        text = text,
        font = font,
        on_click = on_click
    )


def create_restart_button(
        screen_width: int,
        top_bar_height: int,
        on_click: Callable[[], None]
) -> Button:
    return _create_topbar_button(
        text = "Restart",
        screen_width = screen_width,
        top_bar_height = top_bar_height,
        row = 0,
        on_click = on_click
    )


def create_hint_button(
        screen_width: int,
        top_bar_height: int,
        on_click: Callable[[], None]
) -> Button:
    return _create_topbar_button(
        text = "Hint",
        screen_width = screen_width,
        top_bar_height = top_bar_height,
        row = 1,
        on_click = on_click
    )

if __name__ == "__main__":
    print(pygame.font.get_fonts())