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
        # Use one shared game state only.
        self.game = GameState()

        self.building_order = list(BUILDINGS.keys())
        self.upgrade_order = list(UPGRADES.keys())

        base_font_size = getattr(settings, "FONT_SIZE", 24)
        self.title_font = pygame.font.SysFont("Arial", 34)
        self.section_font = pygame.font.SysFont("Arial", 28)
        self.body_font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.button_font = pygame.font.SysFont("Arial", 20)
        self.font = pygame.font.SysFont("Arial", base_font_size)
        self.font_small = pygame.font.SysFont("Arial", 18)

        self.button_image = None
        self.hovered_building_id = None

        self._load_assets()
        self.update_layout(
            getattr(settings, "SCREEN_WIDTH", 1200),
            getattr(settings, "SCREEN_HEIGHT", 700),
        )

    def _load_assets(self):
        image_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "Reddit Post Button .png",
        )

        if os.path.exists(image_path):
            image = pygame.image.load(image_path).convert_alpha()
            post_w = getattr(settings, "POST_BUTTON_WIDTH", 260)
            post_h = getattr(settings, "POST_BUTTON_HEIGHT", 160)
            self.button_image = pygame.transform.smoothscale(image, (post_w, post_h))

    def update_layout(self, width, height):
        self.screen_width = width
        self.screen_height = height

        outer_margin = getattr(settings, "OUTER_MARGIN", 12)
        panel_gap = getattr(settings, "PANEL_GAP", 0)

        left_w = min(getattr(settings, "LEFT_PANEL_WIDTH", 260), max(200, width // 3))
        right_w = min(getattr(settings, "RIGHT_PANEL_WIDTH", 260), max(200, width // 3))
        right_top_h = getattr(settings, "RIGHT_TOP_HEIGHT", max(220, height // 2 - outer_margin))
        card_gap = getattr(settings, "CARD_GAP", 0)

        content_h = height - (outer_margin * 2)
        center_w = width - (outer_margin * 2) - left_w - right_w - (panel_gap * 2)
        center_w = max(260, center_w)

        self.left_panel = pygame.Rect(outer_margin, outer_margin, left_w, content_h)
        self.center_panel = pygame.Rect(self.left_panel.right + panel_gap, outer_margin, center_w, content_h)
        self.right_panel_top = pygame.Rect(self.center_panel.right + panel_gap, outer_margin, right_w, min(right_top_h, content_h))
        self.right_panel_bottom = pygame.Rect(
            self.center_panel.right + panel_gap,
            self.right_panel_top.bottom,
            right_w,
            height - outer_margin - self.right_panel_top.bottom,
        )

        # Aliases for compatibility with the older main/menu code.
        self.left_panel_rect = self.left_panel
        self.right_panel_rect = pygame.Rect(self.right_panel_top.x, self.right_panel_top.y, right_w, content_h)
        self.right_top_half = self.right_panel_top
        self.right_bottom_half = self.right_panel_bottom
        self.layout = {
            "center_x": self.center_panel.x,
            "right_x": self.right_panel_top.x,
        }

        # Building cards on the left.
        self.building_cards = {}
        self.building_buy_buttons = {}
        self.left_bars = []

        visible_slots = max(4, len(self.building_order))
        available_h = self.left_panel.height
        card_h = max(100, (available_h - (card_gap * (visible_slots - 1))) // visible_slots)
        card_h = min(card_h, getattr(settings, "SIDEBAR_CARD_HEIGHT", 130))

        for idx, building_id in enumerate(self.building_order):
            rect = pygame.Rect(
                self.left_panel.x,
                self.left_panel.y + idx * (card_h + card_gap),
                self.left_panel.width,
                card_h,
            )
            self.building_cards[building_id] = rect
            self.left_bars.append(rect)
            self.building_buy_buttons[building_id] = pygame.Rect(rect.right - 96, rect.bottom - 42, 82, 28)

        self.empty_building_card = pygame.Rect(
            self.left_panel.x,
            self.left_panel.y + len(self.building_order) * (card_h + card_gap),
            self.left_panel.width,
            card_h,
        )

        # Center click area.
        post_w = getattr(settings, "POST_BUTTON_WIDTH", 260)
        post_h = getattr(settings, "POST_BUTTON_HEIGHT", 160)
        center_click_w = post_w + 100
        center_click_h = post_h + 120
        self.click_area = pygame.Rect(0, 0, center_click_w, center_click_h)
        self.click_area.center = self.center_panel.center

        self.click_button_rect = pygame.Rect(0, 0, post_w, post_h)
        self.click_button_rect.centerx = self.click_area.centerx
        self.click_button_rect.y = self.click_area.y + 70
        self.post_button_rect = self.click_button_rect

        # Optional right-side button alias from the older version.
        self.right_button_rect = pygame.Rect(
            self.right_panel_bottom.x + 20,
            self.right_panel_bottom.y + 70,
            max(120, self.right_panel_bottom.width - 40),
            48,
        )

        # Upgrade cards on the right.
        self.upgrade_cards = {}
        self.upgrade_buy_buttons = {}
        upgrade_card_h = getattr(settings, "UPGRADE_CARD_HEIGHT", 62)
        upgrade_x = self.right_panel_top.x + 12
        upgrade_y = self.right_panel_top.y + 56
        upgrade_w = self.right_panel_top.width - 24

        for idx, upgrade_id in enumerate(self.upgrade_order):
            rect = pygame.Rect(
                upgrade_x,
                upgrade_y + idx * (upgrade_card_h + 10),
                upgrade_w,
                upgrade_card_h,
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

            # Clicking a building card also tries to buy it, like the older left-bar version.
            for building_id, rect in self.building_cards.items():
                if rect.collidepoint(event.pos):
                    buy_building(self.game, building_id)
                    return

            for upgrade_id, rect in self.upgrade_buy_buttons.items():
                if rect.collidepoint(event.pos):
                    buy_upgrade(self.game, upgrade_id)
                    return

        elif event.type == pygame.MOUSEMOTION:
            self.hovered_building_id = None
            for building_id, rect in self.building_cards.items():
                if rect.collidepoint(event.pos):
                    self.hovered_building_id = building_id
                    break

    def update(self, dt):
        update_game(self.game, dt)

    def draw(self, screen):
        self._draw_panels(screen)
        self._draw_building_sidebar(screen)
        self._draw_center_game_panel(screen)
        self._draw_upgrade_panel(screen)
        self._draw_minigame_panel(screen)
        self._draw_hover_tooltip(screen)

    def _draw_panels(self, screen):
        gray = getattr(settings, "GRAY", (210, 210, 210))
        left_bg = getattr(settings, "LEFT_PANEL_BG", (198, 160, 160))
        center_bg = getattr(settings, "CENTER_PANEL_BG", gray)
        right_bg = getattr(settings, "RIGHT_PANEL_BG", (220, 220, 220))
        border = getattr(settings, "PANEL_BORDER", getattr(settings, "BLACK", (0, 0, 0)))

        screen.fill(gray)
        pygame.draw.rect(screen, left_bg, self.left_panel)
        pygame.draw.rect(screen, center_bg, self.center_panel)
        pygame.draw.rect(screen, right_bg, self.right_panel_top)
        pygame.draw.rect(screen, right_bg, self.right_panel_bottom)

        for rect in [self.left_panel, self.center_panel, self.right_panel_top, self.right_panel_bottom]:
            pygame.draw.rect(screen, border, rect, 1)

    def _draw_building_sidebar(self, screen):
        border = getattr(settings, "PANEL_BORDER", getattr(settings, "BLACK", (0, 0, 0)))
        left_bg = getattr(settings, "LEFT_PANEL_BG", (198, 160, 160))

        for building_id in self.building_order:
            rect = self.building_cards[building_id]
            buy_rect = self.building_buy_buttons[building_id]
            building = BUILDINGS[building_id]
            owned = self.game.buildings_owned[building_id]
            cost = get_building_cost(building_id, owned)
            hovered = self.hovered_building_id == building_id

            fill = tuple(min(255, c + 15) for c in left_bg) if hovered else left_bg
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, border, rect, 1)

            title = self.section_font.render(building.get("name", building_id.title()), True, getattr(settings, "BLACK", (0, 0, 0)))
            owned_text = self.body_font.render(f"Owned: {owned}", True, getattr(settings, "BLACK", (0, 0, 0)))
            cps_text = self.small_font.render(f"+{building['base_cps']} CHUD/sec each", True, getattr(settings, "BLACK", (0, 0, 0)))
            cost_text = self.small_font.render(f"Next cost: {cost}", True, getattr(settings, "BLACK", (0, 0, 0)))

            screen.blit(title, (rect.x + 14, rect.y + 14))
            screen.blit(owned_text, (rect.x + 14, rect.y + 50))
            screen.blit(cps_text, (rect.x + 14, rect.y + 78))
            screen.blit(cost_text, (rect.x + 14, rect.y + 98))

            self._draw_button(screen, buy_rect, "Buy", self.game.chuds >= cost)

        if self.empty_building_card.bottom <= self.left_panel.bottom:
            pygame.draw.rect(screen, left_bg, self.empty_building_card)
            pygame.draw.rect(screen, border, self.empty_building_card, 1)
            coming_title = self.section_font.render("Coming Soon", True, getattr(settings, "BLACK", (0, 0, 0)))
            coming_text = self.small_font.render("Future building slot", True, getattr(settings, "BLACK", (0, 0, 0)))
            screen.blit(coming_title, (self.empty_building_card.x + 14, self.empty_building_card.y + 22))
            screen.blit(coming_text, (self.empty_building_card.x + 14, self.empty_building_card.y + 60))

    def _draw_center_game_panel(self, screen):
        black = getattr(settings, "BLACK", (0, 0, 0))
        dark_gray = getattr(settings, "DARK_GRAY", (60, 60, 60))
        light_blue = getattr(settings, "LIGHT_BLUE", (160, 200, 255))

        total_text = self.title_font.render(f"CHUD Total: {self.game.chuds:.1f}", True, black)
        cps_text = self.title_font.render(f"CHUD/sec: {self.game.total_cps:.1f}", True, black)
        screen.blit(total_text, (self.center_panel.x + 26, self.center_panel.y + 26))
        screen.blit(cps_text, (self.center_panel.x + 26, self.center_panel.y + 70))

        title = self.title_font.render("CHUD Clicker", True, black)
        title_rect = title.get_rect(center=(self.center_panel.centerx, self.click_area.y + 30))
        screen.blit(title, title_rect)

        if self.button_image:
            screen.blit(self.button_image, self.click_button_rect)
        else:
            pygame.draw.rect(screen, light_blue, self.click_button_rect, border_radius=12)
            fallback = self.body_font.render("Click", True, black)
            fallback_rect = fallback.get_rect(center=self.click_button_rect.center)
            screen.blit(fallback, fallback_rect)

        help_text = self.body_font.render("Click the post to earn CHUDs", True, dark_gray)
        help_rect = help_text.get_rect(center=(self.click_area.centerx, self.click_button_rect.bottom + 34))
        screen.blit(help_text, help_rect)

    def _draw_upgrade_panel(self, screen):
        black = getattr(settings, "BLACK", (0, 0, 0))
        card_bg = getattr(settings, "CARD_BG", (235, 235, 235))
        border = getattr(settings, "PANEL_BORDER", black)
        owned_color = getattr(settings, "UPGRADE_OWNED", (88, 165, 92))

        title = self.title_font.render("Upgrades", True, black)
        screen.blit(title, (self.right_panel_top.x + 18, self.right_panel_top.y + 18))

        for upgrade_id in self.upgrade_order:
            rect = self.upgrade_cards[upgrade_id]
            buy_rect = self.upgrade_buy_buttons[upgrade_id]
            upgrade = UPGRADES[upgrade_id]
            owned = upgrade_id in self.game.upgrades_owned
            affordable = self.game.chuds >= upgrade["cost"] and not owned

            pygame.draw.rect(screen, card_bg, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 1, border_radius=8)

            name_text = self.body_font.render(upgrade["name"], True, black)
            cost_text = self.small_font.render(f"Cost: {upgrade['cost']}", True, black)
            screen.blit(name_text, (rect.x + 10, rect.y + 8))
            screen.blit(cost_text, (rect.x + 10, rect.y + 34))

            if owned:
                self._draw_button(screen, buy_rect, "Owned", True, force_color=owned_color)
            else:
                self._draw_button(screen, buy_rect, "Buy", affordable)

    def _draw_minigame_panel(self, screen):
        black = getattr(settings, "BLACK", (0, 0, 0))
        title = self.title_font.render("Mini Games", True, black)
        text = self.body_font.render("Reserved space for later", True, black)
        screen.blit(title, (self.right_panel_bottom.x + 18, self.right_panel_bottom.y + 18))
        screen.blit(text, (self.right_panel_bottom.x + 18, self.right_panel_bottom.y + 70))

    def _draw_hover_tooltip(self, screen):
        if not self.hovered_building_id:
            return

        mouse_pos = pygame.mouse.get_pos()
        building = BUILDINGS[self.hovered_building_id]
        owned = self.game.buildings_owned[self.hovered_building_id]
        cost = get_building_cost(self.hovered_building_id, owned)

        tip_x = min(mouse_pos[0] + 18, self.screen_width - 250)
        tip_y = min(mouse_pos[1] + 18, self.screen_height - 130)
        tip_rect = pygame.Rect(tip_x, tip_y, 235, 110)

        tip_surf = pygame.Surface((tip_rect.width, tip_rect.height), pygame.SRCALPHA)
        tip_surf.fill((20, 20, 20, 230))
        screen.blit(tip_surf, tip_rect.topleft)
        pygame.draw.rect(screen, getattr(settings, "WHITE", (255, 255, 255)), tip_rect, 2)

        lines = [
            f"{building.get('name', self.hovered_building_id.title())}",
            f"Owned: {owned}",
            f"CPS each: {building['base_cps']}",
            f"Next cost: {cost}",
        ]

        for idx, line in enumerate(lines):
            text = self.font_small.render(line, True, getattr(settings, "WHITE", (255, 255, 255)))
            screen.blit(text, (tip_x + 12, tip_y + 10 + idx * 22))

    def _draw_button(self, screen, rect, label, enabled, force_color=None):
        button_bg = getattr(settings, "BUTTON_BG", (25, 124, 214))
        button_disabled = getattr(settings, "BUTTON_DISABLED", (140, 140, 140))
        white = getattr(settings, "WHITE", (255, 255, 255))
        color = force_color if force_color is not None else (button_bg if enabled else button_disabled)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        text = self.button_font.render(label, True, white)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
