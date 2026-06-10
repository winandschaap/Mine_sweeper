import pygame
from game.game_state import GameState
from game.types import GameStatus, Position
from win32api import GetSystemMetrics

WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)
# Declare sizes and framerate
CELL_SIZE = HEIGHT//15
TOP_BAR_HEIGHT = HEIGHT//12
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

class PygameUI:
    def __init__(self, width: int = 9, height: int = 9, mine_count: int = 16, no_check: bool = False):
        pygame.display.init()
        pygame.font.init()
        self.no_check = no_check
        self.game = GameState(width, height, mine_count, self.no_check)
        self.screen_width = width * CELL_SIZE
        self.screen_height = height * CELL_SIZE + TOP_BAR_HEIGHT
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

        pygame.display.set_caption("Minesweeper")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, (2*CELL_SIZE) //3)
        self.big_font = pygame.font.SysFont(None, 2 * CELL_SIZE)
        self.background_big_font = pygame.font.SysFont(None, (21 * CELL_SIZE)//10)
        self.running = True


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
                pos = self.screen_to_position(event.pos)

                if pos is None:
                    continue
                if self.game.hint:
                    if self.game.hint.position == pos:
                        self.game.toggle_hint(True)
                if event.button == 1:
                    self.game.reveal_cell(pos)
                elif event.button == 3:
                    self.game.toggle_flag(pos)

    def screen_to_position(self, mouse_pos) -> Position | None:
        mx, my = mouse_pos

        if my < TOP_BAR_HEIGHT:
            return None

        x = mx // CELL_SIZE
        y = (my-TOP_BAR_HEIGHT) // CELL_SIZE

        pos = Position(x, y)

        if self.game.board.in_bounds(pos):
            return pos

        return None

    def draw(self) -> None:
        self.screen.fill(BG)

        self.draw_top_bar()
        self.draw_board()

        pygame.display.flip()

    def draw_top_bar(self) -> None:
        pygame.draw.rect(
            self.screen,
            BG,
            pygame.Rect(0,0, self.screen_width, self.screen_height),
        )

        flags_text = self.font.render(
            f'Flags: {self.game.remaining_flags()}',
            True,
            TEXT
        )
        self.screen.blit(flags_text, (CELL_SIZE//4, flags_text.get_height()//2))

        restart_text = self.font.render("ESC = restart", True, TEXT)
        self.screen.blit(restart_text, (self.screen_width - restart_text.get_width()-CELL_SIZE//4, restart_text.get_height()//2))

        timer_text = self.font.render(f"Time: {self.game.current_time()}", True, TEXT)
        self.screen.blit(timer_text, (CELL_SIZE//4, (timer_text.get_height()+TOP_BAR_HEIGHT)//2))

        hints_text = self.font.render(f"Hints used (h): {self.game.hint_count}", True, TEXT)
        self.screen.blit(hints_text, (self.screen_width - hints_text.get_width()-CELL_SIZE//4,(hints_text.get_height()+TOP_BAR_HEIGHT)//2))


    def draw_board(self) -> None:
        board = self.game.board

        for y in range(board.height):
            for x in range(board.width):
                pos = Position(x, y)
                cell = board.get_cell(pos)

                rect = pygame.Rect(
                    x*CELL_SIZE,
                    TOP_BAR_HEIGHT + y*CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
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
            CELL_SIZE//4,
        )

    def draw_flag(self, rect: pygame.Rect) -> None:
        pole_x = rect.left + CELL_SIZE//3
        pole_top = rect.top + CELL_SIZE//5
        pole_bottom = rect.bottom - CELL_SIZE//5

        pygame.draw.line(
            self.screen,
            RED,
            (pole_x, pole_top),
            (pole_x, pole_bottom),
            3,
        )

        flag_points = [
            (pole_x, pole_top),
            (pole_x+CELL_SIZE//3, pole_top + CELL_SIZE//8),
            (pole_x, pole_top + CELL_SIZE//4),
        ]

        pygame.draw.polygon(self.screen, RED, flag_points)

