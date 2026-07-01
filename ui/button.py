import pygame


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        on_click,
        bg = (70, 70, 80),
        hover_bg = (95, 95 ,110),
        text_color = (240, 240, 240)
    ):
        self.rect = rect
        self.text = text
        self.font = font
        self.on_click = on_click
        self.bg = bg
        self.hover_bg = hover_bg
        self.text_color = text_color

    def draw(self, screen: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_bg if self.rect.collidepoint(mouse_pos) else self.bg
        border_radius = max(2, min(self.rect.width, self.rect.height) // 6)
        border_width = max(1, min(self.rect.width, self.rect.height) // 18)

        pygame.draw.rect(screen, color, self.rect, border_radius=border_radius)
        pygame.draw.rect(
            screen,
            self.text_color,
            self.rect,
            border_width,
            border_radius=border_radius
        )

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        if event.button != 1:
            return False
        if not self.rect.collidepoint(event.pos):
            return False

        self.on_click()
        return True
