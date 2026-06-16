from typing import Callable

import pygame

from ui.button import Button

def create_restart_button(
        screen_width: int,
        top_bar_height: int,
        font: pygame.font.Font,
        on_click: Callable[[], None]
) -> Button:
    text = "Restart"
    padding_x = 20
    padding_y = 10

    text_width, text_height = font.size(text)

    return Button(
        rect = pygame.Rect(
            screen_width - text_width - 3*padding_x,
            padding_y,
            text_width + 2*padding_x,
            (9 *top_bar_height) // 20
        ),
        text = "Restart",
        font = font,
        on_click = on_click
    )

def create_hint_button(
        screen_width: int,
        top_bar_height: int,
        font: pygame.font.Font,
        on_click: Callable[[], None]
) -> Button:
    text = "Hint"
    padding_x = 20
    padding_y = 10

    text_width, text_height = font.size(text)

    return Button(
        rect = pygame.Rect(
            screen_width - text_width - 3*padding_x,
            top_bar_height - text_height - 1*padding_y,
            text_width + 2*padding_x,
            (9 *top_bar_height) // 20
        ),
        text = "Hint",
        font = font,
        on_click = on_click
    )
