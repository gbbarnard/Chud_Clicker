import os
import pygame
import settings
from maths import (
    GameState,
    BUILDINGS,
    add_manual_click,
    buy_building,
    get_building_cost,
    refresh_cps,
)

class MenuManager:
    def __init__(self):
        self.game = GameState()

        # Temporary test setup: start with 1 free Poster so passive income is visible right away
        self.game.buildings_owned["poster"] = 1
        refresh_cps(self.game)

        self.font = pygame.font.SysFont("Arial", settings.POST_FONT_SIZE)
        self.small_font = pygame.font.SysFont("Arial", 28)

        self.button_rect = pygame.Rect(
            (settings.SCREEN_WIDTH // 2) - (settings.POST_BUTTON_WIDTH // 2),
            (settings.SCREEN_HEIGHT // 2) - (settings.POST_BUTTON_HEIGHT // 2),
            settings.POST_BUTTON_WIDTH,
            settings.POST_BUTTON_HEIGHT
        )

        self.buy_poster_rect = pygame.Rect(
            settings.SCREEN_WIDTH - 320,
            140,
            240,
            70
        )

        image_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "Reddit Post Button .png"
        )

        self.button_image = pygame.image.load(image_path).convert_alpha()
        self.button_image = pygame.transform.smoothscale(
            self.button_image,
            (settings.POST_BUTTON_WIDTH, settings.POST_BUTTON_HEIGHT)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                add_manual_click(self.game)

            elif self.buy_poster_rect.collidepoint(event.pos):
                buy_building(self.game, "poster")

    def update(self, dt):
        from maths import update_game
        update_game(self.game, dt)

    def draw(self, screen):
        screen.blit(self.button_image, self.button_rect)

        counter_text = self.font.render(
            f"CHUD Total: {self.game.chuds:.1f}",
            True,
            settings.BLACK
        )
        screen.blit(counter_text, (100, 100))

        cps_text = self.font.render(
            f"CHUD/sec: {self.game.total_cps:.1f}",
            True,
            settings.BLACK
        )
        screen.blit(cps_text, (100, 150))

        poster_count = self.game.buildings_owned["poster"]
        poster_info = self.small_font.render(
            f"Poster Owned: {poster_count} | Each Poster: {BUILDINGS['poster']['base_cps']} CHUD/sec",
            True,
            settings.BLACK
        )
        screen.blit(poster_info, (100, 210))

        poster_cost = get_building_cost("poster", poster_count)

        pygame.draw.rect(screen, settings.BLUE, self.buy_poster_rect, border_radius=12)
        buy_text = self.small_font.render("Buy Poster", True, settings.WHITE)
        buy_text_rect = buy_text.get_rect(center=(
            self.buy_poster_rect.centerx,
            self.buy_poster_rect.centery - 12
        ))
        screen.blit(buy_text, buy_text_rect)

        cost_text = self.small_font.render(f"Cost: {poster_cost}", True, settings.WHITE)
        cost_text_rect = cost_text.get_rect(center=(
            self.buy_poster_rect.centerx,
            self.buy_poster_rect.centery + 16
        ))
        screen.blit(cost_text, cost_text_rect)
