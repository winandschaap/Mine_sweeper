from dataclasses import dataclass

WINDOW_SCALE:float = 0.75
TOP_BAR_RATIO = 1/9

@dataclass(frozen=True)
class Layout:
    screen_width: int
    screen_height: int
    window_width: int
    window_height: int
    top_bar_height: int
    board_area_width: int
    board_area_height: int
    cell_size: int
    board_pixel_width: int
    board_pixel_height: int
    board_offset_x: int
    board_offset_y: int

def create_layout(
        screen_width: int,
        screen_height: int,
        board_width: int,
        board_height: int,
        fullscreen: bool = False,
        window_scale: float = WINDOW_SCALE
)-> Layout:

    if fullscreen:
        window_width = screen_width
        window_height = screen_height
    else:
        window_width = int(screen_width*window_scale)
        window_height = int(screen_height*window_scale)

    return create_layout_for_window(
        window_width,
        window_height,
        board_width,
        board_height,
    )


def create_layout_for_window(
        window_width: int,
        window_height: int,
        board_width: int,
        board_height: int,
) -> Layout:
    top_bar_height = window_height // 9

    board_area_width = window_width
    board_area_height = window_height - top_bar_height

    cell_size = max(1, min(
        board_area_width // board_width,
        board_area_height // board_height
    ))

    board_pixel_width = board_width * cell_size
    board_pixel_height = board_height * cell_size
    board_offset_x = (window_width - board_pixel_width)//2
    board_offset_y = top_bar_height + (board_area_height - board_pixel_height)//2

    return Layout(
        screen_width = window_width,
        screen_height = window_height,
        window_width = window_width,
        window_height = window_height,
        top_bar_height = top_bar_height,
        board_area_width = board_area_width,
        board_area_height = board_area_height,
        cell_size = cell_size,
        board_pixel_width = board_pixel_width,
        board_pixel_height = board_pixel_height,
        board_offset_x = board_offset_x,
        board_offset_y = board_offset_y
    )

