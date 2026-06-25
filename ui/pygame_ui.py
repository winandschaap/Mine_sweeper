import pygame
import ctypes
import ctypes.wintypes
from game.game_state import GameState
from game.types import GameStatus, Position
from ui.buttons import create_restart_button, create_hint_button
from ui.layout import create_layout, create_layout_for_window, Layout

FPS = 60
FULLSCREEN_TOGGLE_DEBOUNCE_MS = 750
RESIZE_SUPPRESS_AFTER_TOGGLE_MS = 750
WINDOW_POSITION_RESTORE_MS = 500
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004

USER32 = ctypes.WinDLL("user32", use_last_error=True)
GET_WINDOW_RECT = getattr(USER32, "GetWindowRect")
GET_WINDOW_RECT.argtypes = [
    ctypes.wintypes.HWND,
    ctypes.POINTER(ctypes.wintypes.RECT),
]
GET_WINDOW_RECT.restype = ctypes.wintypes.BOOL

SET_WINDOW_POS = getattr(USER32, "SetWindowPos")
SET_WINDOW_POS.argtypes = [
    ctypes.wintypes.HWND,
    ctypes.wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.wintypes.UINT,
]
SET_WINDOW_POS.restype = ctypes.wintypes.BOOL

# Give RGB values for needed values
BG = (30, 30, 35)
TEXT = (240, 240, 240)
BLACK = (20, 20, 20)
RED = (220, 60, 60)
GREEN = (70, 180, 90)
BLUE = (70, 120, 220)
YELLOW = (230, 190, 60)
CELL_HIDDEN = (90, 90, 100)
CELL_REVEALED = (185, 185, 190)
CELL_BORDER = (45, 45, 50)
CELL_HINT = (200,0,100)


def get_display_size() -> tuple[int, int]:
    if not pygame.display.get_init():
        pygame.display.init()

    display_info = pygame.display.Info()
    return display_info.current_w, display_info.current_h


def get_desktop_size() -> tuple[int, int]:
    if not pygame.display.get_init():
        pygame.display.init()

    desktop_sizes = pygame.display.get_desktop_sizes()
    if desktop_sizes:
        return desktop_sizes[0]

    return get_display_size()


def get_display_window_position() -> tuple[int, int] | None:
    hwnd = pygame.display.get_wm_info().get("window")
    if not hwnd:
        return None

    rect = ctypes.wintypes.RECT()
    if not GET_WINDOW_RECT(hwnd, ctypes.byref(rect)):
        return None

    return rect.left, rect.top


def clamp_window_position(
        position: tuple[int, int],
        window_size: tuple[int, int],
) -> tuple[int, int]:
    desktop_width, desktop_height = get_desktop_size()
    window_width, window_height = window_size
    max_x = max(0, desktop_width - window_width)
    max_y = max(0, desktop_height - window_height)
    x, y = position

    return (
        max(0, min(x, max_x)),
        max(0, min(y, max_y)),
    )


def move_display_window(position: tuple[int, int]) -> None:
    hwnd = pygame.display.get_wm_info().get("window")
    if not hwnd:
        return

    x, y = position
    SET_WINDOW_POS(
        hwnd,
        None,
        x,
        y,
        0,
        0,
        SWP_NOSIZE | SWP_NOZORDER,
    )


class PygameUI:
    def __init__(
        self,
        width: int = 16,
        height: int = 10,
        mine_count: int = 32,
        no_check: bool = False,
        fullscreen: bool = False,
        window_scale: float = 0.75,
        resizable: bool = True,
    ):
        pygame.display.init()
        pygame.font.init()

        screen_width, screen_height = get_display_size()

        requested_layout = create_layout(
            screen_width,
            screen_height,
            width,
            height,
            fullscreen = fullscreen,
            window_scale = window_scale
        )

        self.board_width = width
        self.board_height = height
        self.fullscreen = fullscreen
        self.resizable = resizable
        self.windowed_size = (
            requested_layout.window_width,
            requested_layout.window_height,
        )
        self.windowed_position: tuple[int, int] | None = None
        self.no_check = no_check
        self.game = GameState(width, height, mine_count, self.no_check)

        # Declare the variables, to be overwritten py self.apply_layout()
        self.layout: Layout = Layout(1,1,1,1,1,1,1,1,1,1,1,1)
        self.cell_size: int = 1
        self.top_bar_height: int = 1
        self.screen_width: int = 1
        self.screen_height: int = 1

        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        self.background_big_font = pygame.font.SysFont(None, 48)
        self.buttons = []

        self.screen = self.create_display_surface()
        self.apply_layout()

        pygame.display.set_caption("Minesweeper")

        self.clock = pygame.time.Clock()
        self.running = True
        self.last_fullscreen_toggle_ms = 0
        self.ignore_resize_until_ms = 0
        self.f11_is_down = False
        self.restore_window_position: tuple[int, int] | None = None
        self.restore_window_position_until_ms = 0

    def create_display_surface(self) -> pygame.Surface:
        def set_mode(size: tuple[int, int], flags: int) -> pygame.Surface:
            try:
                return pygame.display.set_mode(size, flags, vsync=1)
            except TypeError:
                return pygame.display.set_mode(size, flags)

        if self.fullscreen:
            return set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)

        display_flags = pygame.DOUBLEBUF
        if self.resizable:
            display_flags |= pygame.RESIZABLE

        return set_mode(self.windowed_size, display_flags)

    def apply_layout(self) -> None:
        actual_width, actual_height = self.screen.get_size()

        self.layout = create_layout_for_window(
            actual_width,
            actual_height,
            self.board_width,
            self.board_height,
        )
        self.cell_size = self.layout.cell_size
        self.top_bar_height = self.layout.top_bar_height
        self.screen_width = self.layout.window_width
        self.screen_height = self.layout.window_height

        self.font = pygame.font.SysFont(None, max(12, (2*self.cell_size) //3))
        self.big_font = pygame.font.SysFont(None, max(24, 2 * self.cell_size))
        self.background_big_font = pygame.font.SysFont(None, max(24, (21 * self.cell_size)//10))
        self.rebuild_buttons()

    def rebuild_buttons(self) -> None:
        self.buttons = [
            create_restart_button(
                self.screen_width,
                self.top_bar_height,
                self.font,
                self.game.reset
            ),
            create_hint_button(
                self.screen_width,
                self.top_bar_height,
                self.font,
                self.game.toggle_hint
            )
        ]

    def toggle_fullscreen(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_fullscreen_toggle_ms < FULLSCREEN_TOGGLE_DEBOUNCE_MS:
            return

        if self.restore_window_position is not None:
            return

        self.last_fullscreen_toggle_ms = now
        self.ignore_resize_until_ms = now + RESIZE_SUPPRESS_AFTER_TOGGLE_MS
        previous_fullscreen = self.fullscreen
        previous_windowed_size = self.windowed_size
        previous_windowed_position = self.windowed_position
        previous_screen = self.screen

        try:
            if self.fullscreen:
                self.fullscreen = False
                self.screen = self.create_display_surface()
                if self.windowed_position is not None:
                    restored_position = clamp_window_position(
                        self.windowed_position,
                        self.windowed_size,
                    )
                    self.windowed_position = restored_position
                    move_display_window(restored_position)
                    self.restore_window_position = restored_position
                    self.restore_window_position_until_ms = (
                        now + WINDOW_POSITION_RESTORE_MS
                    )
            else:
                self.windowed_size = self.screen.get_size()
                windowed_position = get_display_window_position()
                if windowed_position is not None:
                    self.windowed_position = clamp_window_position(
                        windowed_position,
                        self.windowed_size,
                    )
                self.fullscreen = True
                self.screen = self.create_display_surface()

            self.apply_layout()
        except (pygame.error, RuntimeError):
            self.fullscreen = previous_fullscreen
            self.windowed_size = previous_windowed_size
            self.windowed_position = previous_windowed_position
            self.screen = previous_screen
            self.apply_layout()

    def resize_window(self, size: tuple[int, int]) -> None:
        if self.fullscreen:
            return

        if pygame.time.get_ticks() < self.ignore_resize_until_ms:
            return

        previous_windowed_size = self.windowed_size
        previous_windowed_position = self.windowed_position

        try:
            actual_size = self.screen.get_size()
            self.windowed_size = actual_size if actual_size != (0, 0) else size
            self.windowed_position = get_display_window_position()
            self.apply_layout()
        except (pygame.error, RuntimeError):
            self.windowed_size = previous_windowed_size
            self.windowed_position = previous_windowed_position

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.restore_pending_window_position()
            self.draw()

        pygame.quit()

    def restore_pending_window_position(self) -> None:
        if self.restore_window_position is None:
            return

        now = pygame.time.get_ticks()
        if now > self.restore_window_position_until_ms:
            self.restore_window_position = None
            return

        move_display_window(self.restore_window_position)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.reset()
                elif event.key == pygame.K_F11:
                    if not self.f11_is_down:
                        self.f11_is_down = True
                        self.toggle_fullscreen()
                elif event.key == pygame.K_h:
                    if self.game.status == GameStatus.RUNNING:
                        self.game.toggle_hint()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_F11:
                    self.f11_is_down = False

            elif event.type == pygame.VIDEORESIZE:
                if self.resizable:
                    self.resize_window(event.size)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                button_was_clicked = False
                for button in self.buttons:
                    if button.handle_event(event):
                        button_was_clicked = True
                        break

                if button_was_clicked:
                    continue

                pos = self.screen_to_position(event.pos)

                if pos is None:
                    continue

                if event.button == 1:
                    self.game.reveal_cell(pos)
                elif event.button == 3:
                    self.game.toggle_flag(pos)
                self.game.check_hint_status()

    def screen_to_position(self, mouse_pos) -> Position | None:
        mx, my = mouse_pos

        board_left = self.layout.board_offset_x
        board_top = self.layout.board_offset_y
        board_right = board_left + self.layout.board_pixel_width
        board_bottom = board_top + self.layout.board_pixel_height

        if not (board_left <= mx < board_right and board_top <= my < board_bottom):
            return None

        x = (mx - board_left) // self.cell_size
        y = (my-board_top) // self.cell_size

        pos = Position(x, y)

        if self.game.board.in_bounds(pos):
            return pos

        return None

    def draw(self) -> None:
        self.screen.fill(BG)
        self.draw_top_bar()
        self.draw_board()
        self.draw_buttons()

        pygame.display.flip()

    def draw_top_bar(self) -> None:
        pygame.draw.rect(
            self.screen,
            BG,
            pygame.Rect(0, 0, self.screen_width, self.top_bar_height),
        )

        flags_text = self.font.render(
            f'Flags: {self.game.board.remaining_flags()}',
            True,
            TEXT
        )
        self.screen.blit(flags_text, (self.cell_size//4, flags_text.get_height()//2))

#        restart_text = self.font.render("ESC = restart", True, TEXT)
#        self.screen.blit(restart_text, (self.screen_width - restart_text.get_width()-self.cell_size//4, restart_text.get_height()//2))

        timer_text = self.font.render(f"Time: {self.game.current_time()}", True, TEXT)
        self.screen.blit(timer_text, (self.cell_size//4, (timer_text.get_height()+self.top_bar_height)//2))

#        hints_text = self.font.render(f"Hints used (h): {self.game.hint_count}", True, TEXT)
#        self.screen.blit(hints_text, (self.screen_width - hints_text.get_width()-self.cell_size//4,(hints_text.get_height()+self.top_bar_height)//2))


    def draw_board(self) -> None:
        board = self.game.board

        for y in range(board.height):
            for x in range(board.width):
                pos = Position(x, y)
                cell = board.get_cell(pos)

                rect = pygame.Rect(
                    self.layout.board_offset_x + x * self.cell_size,
                    self.layout.board_offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                if cell.is_revealed:
                    pygame.draw.rect(self.screen, CELL_REVEALED, rect)
                elif cell.is_highlight:
                    pygame.draw.rect(self.screen, CELL_HINT, rect)
                else:
                    pygame.draw.rect(self.screen, CELL_HIDDEN, rect)

                pygame.draw.rect(self.screen, CELL_BORDER, rect, 2)

                if cell.is_revealed:
                    if cell.is_mine:
                        self.draw_mine(rect)
                    elif cell.neighbor_mines>0:
                        self.draw_number(rect, cell.neighbor_mines)
                elif cell.is_flagged:
                    self.draw_flag(rect)


        if self.game.status == GameStatus.LOST:
            msg_background = self.big_font.render("Game Over", True, BLACK)
            self.screen.blit(
                msg_background,
                (self.screen_width // 2 - msg_background.get_width() // 2 + 5,
                 self.screen_height// 2 - msg_background.get_height() // 2 + 5)
            )
            msg = self.big_font.render("Game Over", True, RED)
            self.screen.blit(msg, (self.screen_width // 2 - msg.get_width() // 2, self.screen_height // 2 - msg.get_height() // 2))
        elif self.game.status == GameStatus.WON:
            msg_background = self.big_font.render(
                "You Won!",
                True,
                BLACK
            )
            self.screen.blit(
                msg_background,
                (self.screen_width // 2 - msg_background.get_width() // 2 + 5, self.screen_height // 2 - msg_background.get_height() // 2 + 5)
            )
            msg = self.big_font.render(
                "You Won!",
                True, GREEN
            )
            self.screen.blit(msg, (self.screen_width // 2 - msg.get_width() // 2, self.screen_height // 2 - msg.get_height() // 2))

    def draw_number(self, rect: pygame.Rect, number: int) -> None:
        number_colors = {
            1: BLUE,
            2: GREEN,
            3: RED,
            4: (80, 80, 160),
            5: (150, 60, 60),
            6: (60, 150, 150),
            7: BLACK,
            8: (100, 100, 100),

        }
        surface = self.font.render(
            str(number),
            True,
            number_colors.get(number, BLACK)
        )
        text_rect = surface.get_rect(center=rect.center)
        self.screen.blit(surface, text_rect)

    def draw_mine(self, rect: pygame.Rect) -> None:
        pygame.draw.circle(
            self.screen,
            BLACK,
            rect.center,
            self.cell_size//4,
        )

    def draw_flag(self, rect: pygame.Rect) -> None:

        # Setting parameters for the drawings
        pole_top_x, pole_top_y = rect.left + (4*self.cell_size)//9 , rect.top + (2 * self.cell_size)//9
        layer1_x, layer1_y = rect.left + (2*self.cell_size)//9, rect.top + (7*self.cell_size)//9
        layer2_x, layer2_y = rect.left + (3*self.cell_size)//9, rect.top + (6*self.cell_size)//9

        pole_width, pole_height = self.cell_size // 9, (6 * self.cell_size) // 9
        layer_height = self.cell_size // 9 + 1
        layer1_width = (5 * self.cell_size) // 9
        layer2_width = (3 * self.cell_size) // 9

        # Creating the rectangular objects
        pole = pygame.Rect(pole_top_x, pole_top_y, pole_width, pole_height-1)
        layer_1 = pygame.Rect(layer1_x, layer1_y, layer1_width, layer_height)
        layer_2 = pygame.Rect(layer2_x, layer2_y, layer2_width, layer_height)

        pole_parts = [pole, layer_1, layer_2]

        # Draw the pole with base
        for part in pole_parts:
            pygame.draw.rect(
                self.screen,
                BLACK,
                part
            )

        # Flag drawing
        flag_points = [
            (pole_top_x, pole_top_y - self.cell_size//9),
            (rect.left + (8*self.cell_size)//9, rect.top + (3*self.cell_size)//9),
            (pole_top_x, pole_top_y + (3*self.cell_size)//9),
        ]

        pygame.draw.polygon(self.screen, RED, flag_points)

    def draw_buttons(self) -> None:
        for button in self.buttons:
            button.draw(self.screen)
