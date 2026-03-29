import os
import pygame
import settings
from maths import (
    BUILDINGS,
    BUILDING_UPGRADE_MAP,
    UPGRADES,
    GameState,
    add_manual_click,
    buy_building,
    buy_upgrade,
    get_building_cost,
    get_building_multiplier,
    update_game,
)


class MenuManager:
    def __init__(self):
        self.game = GameState()
        self.font = pygame.font.SysFont("Arial", settings.POST_FONT_SIZE)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.button_font = pygame.font.SysFont("Arial", 20)
        self.tiny_font = pygame.font.SysFont("Arial", 16)

        self.button_rect = pygame.Rect(
            860,
            250,
            settings.POST_BUTTON_WIDTH,
            settings.POST_BUTTON_HEIGHT,
        )

        self.building_order = ["poster", "bot", "factory"]
        self.building_cards = {}
        self.building_buy_buttons = {}
        self.upgrade_buttons = {}

        card_x = 40
        card_y = 250
        card_width = 680
        card_height = 110
        card_gap = 18
        buy_button_width = 155
        buy_button_height = 42
        upgrade_button_width = 92
        upgrade_button_height = 28

        for index, building_id in enumerate(self.building_order):
            card_rect = pygame.Rect(
                card_x,
                card_y + index * (card_height + card_gap),
                card_width,
                card_height,
            )
            self.building_cards[building_id] = card_rect
            self.building_buy_buttons[building_id] = pygame.Rect(
                card_rect.right - buy_button_width - 18,
                card_rect.bottom - buy_button_height - 16,
                buy_button_width,
                buy_button_height,
            )
            self.upgrade_buttons[building_id] = pygame.Rect(
                card_rect.right - upgrade_button_width - 18,
                card_rect.top + 12,
                upgrade_button_width,
                upgrade_button_height,
            )

        image_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "Reddit Post Button .png",
        )

        self.button_image = pygame.image.load(image_path).convert_alpha()
        self.button_image = pygame.transform.smoothscale(
            self.button_image,
            (settings.POST_BUTTON_WIDTH, settings.POST_BUTTON_HEIGHT),
        )
        
        self.thumbnail_image = pygame.transform.smoothscale(self.button_image, (125, 84))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                add_manual_click(self.game)
                return

            for building_id in self.building_order:
                if self.upgrade_buttons[building_id].collidepoint(event.pos):
                    upgrade_id = BUILDING_UPGRADE_MAP[building_id]
                    buy_upgrade(self.game, upgrade_id)
                    return

                if self.building_buy_buttons[building_id].collidepoint(event.pos):
                    buy_building(self.game, building_id)
                    return

    def update(self, dt):
        update_game(self.game, dt)

    def draw(self, screen):
        screen.blit(self.button_image, self.button_rect)

        counter_text = self.font.render(f"CHUD Total: {self.game.chuds:.1f}", True, settings.BLACK)
        screen.blit(counter_text, (40, 35))

        cps_text = self.font.render(f"CHUD/sec: {self.game.total_cps:.1f}", True, settings.BLACK)
        screen.blit(cps_text, (40, 85))

        heading = self.font.render("Buildings", True, settings.BLACK)
        screen.blit(heading, (40, 190))

        for building_id in self.building_order:
            self.draw_building_card(screen, building_id)

    def draw_building_card(self, screen, building_id):
        building = BUILDINGS[building_id]
        card_rect = self.building_cards[building_id]
        buy_rect = self.building_buy_buttons[building_id]
        upgrade_rect = self.upgrade_buttons[building_id]

        owned = self.game.buildings_owned[building_id]
        next_cost = get_building_cost(building_id, owned)
        upgrade_id = BUILDING_UPGRADE_MAP[building_id]
        upgrade = UPGRADES[upgrade_id]
        has_upgrade = upgrade_id in self.game.upgrades_owned
        building_multiplier = get_building_multiplier(self.game, building_id)
        effective_cps = building["base_cps"] * building_multiplier

        pygame.draw.rect(screen, settings.WHITE, card_rect, border_radius=14)
        pygame.draw.rect(screen, settings.DARK_GRAY, card_rect, width=2, border_radius=14)

        thumb_rect = self.thumbnail_image.get_rect()
        thumb_rect.x = card_rect.x + 14
        thumb_rect.y = card_rect.y + 13
        screen.blit(self.thumbnail_image, thumb_rect)

        name_text = self.small_font.render(building["name"], True, settings.BLACK)
        screen.blit(name_text, (thumb_rect.right + 16, card_rect.y + 16))

        line_one = self.small_font.render(
            f"Owned {owned} | +{effective_cps:.1f} CHUD/sec each",
            True,
            settings.BLACK,
        )
        screen.blit(line_one, (thumb_rect.right + 16, card_rect.y + 45))

        line_two = self.tiny_font.render(
            f"Next cost: {next_cost} | Base: {building['base_cps']:.1f} | Multiplier: x{building_multiplier:.1f}",
            True,
            settings.BLACK,
        )
        screen.blit(line_two, (thumb_rect.right + 16, card_rect.y + 74))

        upgrade_color = settings.GREEN if has_upgrade else (120, 150, 180)
        if not has_upgrade and self.game.chuds >= upgrade["cost"]:
            upgrade_color = settings.ORANGE

        pygame.draw.rect(screen, upgrade_color, upgrade_rect, border_radius=10)
        if has_upgrade:
            upgrade_label = self.tiny_font.render("UPG: OWNED", True, settings.WHITE)
        else:
            upgrade_label = self.tiny_font.render(f"UPG {upgrade['cost']}", True, settings.WHITE)
        upgrade_label_rect = upgrade_label.get_rect(center=upgrade_rect.center)
        screen.blit(upgrade_label, upgrade_label_rect)

        can_afford_building = self.game.chuds >= next_cost
        buy_color = settings.BLUE if can_afford_building else (120, 150, 180)
        pygame.draw.rect(screen, buy_color, buy_rect, border_radius=10)

        buy_text = self.button_font.render(f"Buy {building['name']}", True, settings.WHITE)
        cost_text = self.tiny_font.render(f"Cost: {next_cost}", True, settings.WHITE)
        buy_text_rect = buy_text.get_rect(center=(buy_rect.centerx, buy_rect.centery - 8))
        cost_text_rect = cost_text.get_rect(center=(buy_rect.centerx, buy_rect.centery + 12))
        screen.blit(buy_text, buy_text_rect)
        screen.blit(cost_text, cost_text_rect)
