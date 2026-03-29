import os
import pygame
import settings
from maths import (
    BUILDINGS,
    UPGRADES,
    GameState,
    add_manual_click,
    buy_building,
    buy_upgrade,
    get_building_cost,
    update_game,
)


class MenuManager:
    def __init__(self):
        self.game = GameState()
        self.building_order = ["poster", "bot", "factory"]
        self.upgrade_order = ["double_click", "poster_double", "bot_double", "global_boost"]

        self.title_font = pygame.font.SysFont("Arial", 34)
        self.section_font = pygame.font.SysFont("Arial", 30)
        self.body_font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.button_font = pygame.font.SysFont("Arial", 20)

        self._load_assets()
        self._build_layout()

    def _load_assets(self):
        image_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "Reddit Post Button .png",
        )

        self.button_image = None
        if os.path.exists(image_path):
            image = pygame.image.load(image_path).convert_alpha()
            self.button_image = pygame.transform.smoothscale(
                image,
                (settings.POST_BUTTON_WIDTH, settings.POST_BUTTON_HEIGHT),
            )

    def _build_layout(self):
        m = settings.OUTER_MARGIN
        g = settings.PANEL_GAP
        left_w = settings.LEFT_PANEL_WIDTH
        right_w = settings.RIGHT_PANEL_WIDTH

        content_h = settings.SCREEN_HEIGHT - (m * 2)
        center_w = settings.SCREEN_WIDTH - (m * 2) - left_w - right_w - (g * 2)

        self.left_panel = pygame.Rect(m, m, left_w, content_h)
        self.center_panel = pygame.Rect(self.left_panel.right + g, m, center_w, content_h)
        self.right_panel_top = pygame.Rect(self.center_panel.right + g, m, right_w, settings.RIGHT_TOP_HEIGHT)
        self.right_panel_bottom = pygame.Rect(
            self.center_panel.right + g,
            self.right_panel_top.bottom,
            right_w,
            content_h - settings.RIGHT_TOP_HEIGHT,
        )

        self.building_cards = {}
        self.building_buy_buttons = {}

        card_x = self.left_panel.x
        card_y = self.left_panel.y
        card_w = self.left_panel.width
        card_h = settings.SIDEBAR_CARD_HEIGHT

        for idx, building_id in enumerate(self.building_order):
            rect = pygame.Rect(card_x, card_y + idx * (card_h + settings.CARD_GAP), card_w, card_h)
            self.building_cards[building_id] = rect
            self.building_buy_buttons[building_id] = pygame.Rect(rect.right - 96, rect.bottom - 44, 82, 30)

        self.empty_building_card = pygame.Rect(
            card_x,
            card_y + len(self.building_order) * (card_h + settings.CARD_GAP),
            card_w,
            card_h,
        )

        center_click_w = settings.POST_BUTTON_WIDTH + 100
        center_click_h = settings.POST_BUTTON_HEIGHT + 120
        self.click_area = pygame.Rect(0, 0, center_click_w, center_click_h)
        self.click_area.center = self.center_panel.center

        self.click_button_rect = pygame.Rect(0, 0, settings.POST_BUTTON_WIDTH, settings.POST_BUTTON_HEIGHT)
        self.click_button_rect.centerx = self.click_area.centerx
        self.click_button_rect.y = self.click_area.y + 70

        self.upgrade_cards = {}
        self.upgrade_buy_buttons = {}
        upgrade_x = self.right_panel_top.x + 12
        upgrade_y = self.right_panel_top.y + 56
        upgrade_w = self.right_panel_top.width - 24

        for idx, upgrade_id in enumerate(self.upgrade_order):
            rect = pygame.Rect(
                upgrade_x,
                upgrade_y + idx * (settings.UPGRADE_CARD_HEIGHT + 10),
                upgrade_w,
                settings.UPGRADE_CARD_HEIGHT,
            )
            self.upgrade_cards[upgrade_id] = rect
            self.upgrade_buy_buttons[upgrade_id] = pygame.Rect(rect.right - 68, rect.centery - 14, 56, 28)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.click_button_rect.collidepoint(event.pos):
                add_manual_click(self.game)
                return

            for building_id, rect in self.building_buy_buttons.items():
                if rect.collidepoint(event.pos):
                    buy_building(self.game, building_id)
                    return

            for upgrade_id, rect in self.upgrade_buy_buttons.items():
                if rect.collidepoint(event.pos):
                    buy_upgrade(self.game, upgrade_id)
                    return

    def update(self, dt):
        update_game(self.game, dt)

    def draw(self, screen):
        self._draw_panels(screen)
        self._draw_building_sidebar(screen)
        self._draw_center_game_panel(screen)
        self._draw_upgrade_panel(screen)
        self._draw_minigame_panel(screen)

    def _draw_panels(self, screen):
        screen.fill(settings.GRAY)
        pygame.draw.rect(screen, settings.LEFT_PANEL_BG, self.left_panel)
        pygame.draw.rect(screen, settings.CENTER_PANEL_BG, self.center_panel)
        pygame.draw.rect(screen, settings.RIGHT_PANEL_BG, self.right_panel_top)
        pygame.draw.rect(screen, settings.RIGHT_PANEL_BG, self.right_panel_bottom)

        for rect in [self.left_panel, self.center_panel, self.right_panel_top, self.right_panel_bottom]:
            pygame.draw.rect(screen, settings.PANEL_BORDER, rect, 1)

    def _draw_building_sidebar(self, screen):
        for building_id in self.building_order:
            rect = self.building_cards[building_id]
            buy_rect = self.building_buy_buttons[building_id]
            building = BUILDINGS[building_id]
            owned = self.game.buildings_owned[building_id]
            cost = get_building_cost(building_id, owned)

            pygame.draw.rect(screen, settings.LEFT_PANEL_BG, rect)
            pygame.draw.rect(screen, settings.PANEL_BORDER, rect, 1)

            title = self.section_font.render(building["name"], True, settings.BLACK)
            owned_text = self.body_font.render(f"Owned: {owned}", True, settings.BLACK)
            cps_text = self.small_font.render(f"+{building['base_cps']} CHUD/sec each", True, settings.BLACK)
            cost_text = self.small_font.render(f"Next cost: {cost}", True, settings.BLACK)

            screen.blit(title, (rect.x + 14, rect.y + 14))
            screen.blit(owned_text, (rect.x + 14, rect.y + 56))
            screen.blit(cps_text, (rect.x + 14, rect.y + 86))
            screen.blit(cost_text, (rect.x + 14, rect.y + 108))

            self._draw_button(
                screen,
                buy_rect,
                "Buy",
                self.game.chuds >= cost,
            )

        pygame.draw.rect(screen, settings.LEFT_PANEL_BG, self.empty_building_card)
        pygame.draw.rect(screen, settings.PANEL_BORDER, self.empty_building_card, 1)
        coming_title = self.section_font.render("Coming Soon", True, settings.BLACK)
        coming_text = self.small_font.render("Future building slot", True, settings.BLACK)
        screen.blit(coming_title, (self.empty_building_card.x + 14, self.empty_building_card.y + 22))
        screen.blit(coming_text, (self.empty_building_card.x + 14, self.empty_building_card.y + 70))

    def _draw_center_game_panel(self, screen):
        total_text = self.title_font.render(f"CHUD Total: {self.game.chuds:.1f}", True, settings.BLACK)
        cps_text = self.title_font.render(f"CHUD/sec: {self.game.total_cps:.1f}", True, settings.BLACK)
        screen.blit(total_text, (self.center_panel.x + 26, self.center_panel.y + 26))
        screen.blit(cps_text, (self.center_panel.x + 26, self.center_panel.y + 70))

        title = self.title_font.render("CHUD Clicker", True, settings.BLACK)
        title_rect = title.get_rect(center=(self.center_panel.centerx, self.click_area.y + 30))
        screen.blit(title, title_rect)

        if self.button_image:
            screen.blit(self.button_image, self.click_button_rect)
        else:
            pygame.draw.rect(screen, settings.LIGHT_BLUE, self.click_button_rect, border_radius=12)
            fallback = self.body_font.render("Click", True, settings.BLACK)
            fallback_rect = fallback.get_rect(center=self.click_button_rect.center)
            screen.blit(fallback, fallback_rect)

        help_text = self.body_font.render("Click the post to earn CHUDs", True, settings.DARK_GRAY)
        help_rect = help_text.get_rect(center=(self.click_area.centerx, self.click_button_rect.bottom + 34))
        screen.blit(help_text, help_rect)

    def _draw_upgrade_panel(self, screen):
        title = self.title_font.render("Upgrades", True, settings.BLACK)
        screen.blit(title, (self.right_panel_top.x + 18, self.right_panel_top.y + 18))

        for upgrade_id in self.upgrade_order:
            rect = self.upgrade_cards[upgrade_id]
            buy_rect = self.upgrade_buy_buttons[upgrade_id]
            upgrade = UPGRADES[upgrade_id]
            owned = upgrade_id in self.game.upgrades_owned
            affordable = self.game.chuds >= upgrade["cost"] and not owned

            pygame.draw.rect(screen, settings.CARD_BG, rect, border_radius=8)
            pygame.draw.rect(screen, settings.PANEL_BORDER, rect, 1, border_radius=8)

            name_text = self.body_font.render(upgrade["name"], True, settings.BLACK)
            cost_text = self.small_font.render(f"Cost: {upgrade['cost']}", True, settings.BLACK)
            screen.blit(name_text, (rect.x + 10, rect.y + 8))
            screen.blit(cost_text, (rect.x + 10, rect.y + 34))

            if owned:
                self._draw_button(screen, buy_rect, "Owned", True, force_color=settings.UPGRADE_OWNED)
            else:
                self._draw_button(screen, buy_rect, "Buy", affordable)

    def _draw_minigame_panel(self, screen):
        title = self.title_font.render("Mini Games", True, settings.BLACK)
        text = self.body_font.render("Reserved space for later", True, settings.BLACK)
        screen.blit(title, (self.right_panel_bottom.x + 18, self.right_panel_bottom.y + 18))
        screen.blit(text, (self.right_panel_bottom.x + 18, self.right_panel_bottom.y + 70))

    def _draw_button(self, screen, rect, label, enabled, force_color=None):
        color = force_color if force_color is not None else (settings.BUTTON_BG if enabled else settings.BUTTON_DISABLED)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        text = self.button_font.render(label, True, settings.WHITE)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
