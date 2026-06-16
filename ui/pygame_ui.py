import pygame
from game.game_state import GameState
from game.types import GameStatus, Position
from ui.buttons import create_restart_button, create_hint_button

FPS = 60

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


def get_ui_sizes() -> tuple[int, int]:
    _, screen_height = get_display_size()
    return screen_height // 15, screen_height // 12


class PygameUI:
    def __init__(
        self,
        width: int = 9,
        height: int = 9,
        mine_count: int = 16,
        no_check: bool = False,
        cell_size: int | None = None,
        top_bar_height: int | None = None,
    ):
        pygame.display.init()
        pygame.font.init()

        if cell_size is None or top_bar_height is None:
            default_cell_size, default_top_bar_height = get_ui_sizes()
            cell_size = cell_size or default_cell_size
            top_bar_height = top_bar_height or default_top_bar_height

        self.cell_size = cell_size
        self.top_bar_height = top_bar_height
        self.no_check = no_check
        self.game = GameState(width, height, mine_count, self.no_check)
        self.screen_width = width * self.cell_size
        self.screen_height = height * self.cell_size + self.top_bar_height
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

        pygame.display.set_caption("Minesweeper")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, (2*self.cell_size) //3)
        self.big_font = pygame.font.SysFont(None, 2 * self.cell_size)
        self.background_big_font = pygame.font.SysFont(None, (21 * self.cell_size)//10)
        self.running = True

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

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()

        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.reset()
                elif event.key == pygame.K_h:
                    if self.game.status == GameStatus.RUNNING:
                        self.game.toggle_hint()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.handle_event(event):
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

        if my < self.top_bar_height:
            return None

        x = mx // self.cell_size
        y = (my-self.top_bar_height) // self.cell_size

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
            pygame.Rect(0,0, self.screen_width, self.screen_height),
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

        hints_text = self.font.render(f"Hints used (h): {self.game.hint_count}", True, TEXT)
        self.screen.blit(hints_text, (self.screen_width - hints_text.get_width()-self.cell_size//4,(hints_text.get_height()+self.top_bar_height)//2))


    def draw_board(self) -> None:
        board = self.game.board

        for y in range(board.height):
            for x in range(board.width):
                pos = Position(x, y)
                cell = board.get_cell(pos)

                rect = pygame.Rect(
                    x*self.cell_size,
                    self.top_bar_height + y*self.cell_size,
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
        layer_height = self.cell_size // 9
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
