import os
import random
import time
import pygame
import settings
from maths import (
    BUILDINGS,
    UPGRADES,
    GameState,
    add_manual_click,
    get_click_value,
    buy_building,
    buy_upgrade,
    get_building_cost,
    get_upgrade_cost,
    get_upgrade_required_building,
    is_upgrade_unlocked,
    update_game,
    COIN_OPTIONS,
    process_coin_bet,
    get_speed_click_cost,
    process_speed_click_hit,
    start_speed_click_session,
    SPEED_CLICK_COOLDOWN,
    format_chud_amount,
    can_play_minigame,      # Add this
    clear_minigame_gates,   # Add this
)

BUILDING_IMAGE_FILES = {
    "Reddit Bots": "Reddit_bots.webp",
    "Gaming Pc": "Gamer_pc.webp",
    "Waifu's": "Waifu.webp",
    "Fast Food": "Fast_food.webp",
}

UPGRADE_IMAGE_FILES = {
    "redit bots": "Karma_farms.webp",
    "Gaming PC": "OverClock.webp",
    "Cardboard Cutout": "NSFW.webp",
    "global_boost": "All_a_man_needs.webp",
    "Fast Food": "Chicken_nuggies.webp",
    "Mtn Dew": "Mtn_dew.webp",
    "Mini Game": "Gamer_leans.webp",
}


class Toggle:
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.index = 0

    def update_pos(self, x, y):
        self.rect.topleft = (x, y)

    def draw(self, surface, font, active_color):
        pygame.draw.rect(surface, (100, 100, 100), self.rect, border_radius=8)
        half_w = self.rect.width // 2
        toggle_rect = pygame.Rect(
            self.rect.x + (self.index * half_w),
            self.rect.y,
            half_w,
            self.rect.height,
        )
        pygame.draw.rect(surface, active_color, toggle_rect, border_radius=8)

        for i, opt in enumerate(self.options):
            text = font.render(opt, True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(
                    self.rect.x + (i * half_w) + half_w // 2,
                    self.rect.centery,
                )
            )
            surface.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.index = 1 - self.index
        return self.options[self.index]


class MenuManager:
    def __init__(self):
        self.game = GameState()
        self.click_effects = [] # List to track floating +CHUD text

        self.active_minigame = "coin_flip"
        self.coin_idx = 0
        self.bet_result_text = "Ready to flip?"

        # Speed Clicker State
        self.speed_active = False
        self.speed_cooldown_end = 0
        self.speed_targets_hit = 0
        self.speed_max_targets = 15
        self.speed_current_target = None
        self.speed_target_spawn_time = 0
        self.speed_target_lifetime = 1500  # ms
        self.speed_round_start_time = 0
        self.speed_msg = "Ready?"

        self.side_toggle = Toggle(0, 0, 140, 30, ["Heads", "Tails"])
        self.range_toggle = Toggle(0, 0, 140, 30, ["Over", "Under"])

        self.building_order = list(BUILDINGS.keys())
        self.upgrade_order = self._build_upgrade_order()

        self.title_font = None
        self.section_font = None
        self.body_font = None
        self.small_font = None
        self.button_font = None
        self.font_small = None

        self.button_source_image = None
        self.button_image = None

        self.bg_source_image = None
        self.bg_image = None

        self.building_source_images = {}
        self.upgrade_source_images = {}
        self.building_images = {}
        self.upgrade_images = {}

        self.hovered_building_id = None
        self.hovered_upgrade_id = None

        self.music_button_rect = pygame.Rect(0, 0, 0, 0)
        self.upgrade_scroll_offset = 0
        self.upgrade_scroll_speed = 36
        self.upgrade_content_height = 0
        self.upgrade_viewport_rect = pygame.Rect(0, 0, 0, 0)

        self._load_assets()
        self.update_layout(
            getattr(settings, "SCREEN_WIDTH", 1280),
            getattr(settings, "SCREEN_HEIGHT", 720),
        )

    def _load_assets(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

        def load_image_file(filename):
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    return pygame.image.load(path).convert_alpha()
                except pygame.error as e:
                    print(f"Could not load image {filename}: {e}")
            else:
                print(f"Missing image file: {filename}")
            return None

        self.button_source_image = load_image_file("Reddit Post Button .png")
        # Load background from assets folder
        self.bg_source_image = load_image_file(settings.BACKGROUND_IMAGE)

        for building_id, filename in BUILDING_IMAGE_FILES.items():
            image = load_image_file(filename)
            if image:
                self.building_source_images[building_id] = image

        for upgrade_id, filename in UPGRADE_IMAGE_FILES.items():
            image = load_image_file(filename)
            if image:
                self.upgrade_source_images[upgrade_id] = image

    def _scale_card_image(self, image, target_size):
        if image is None:
            return None

        target_w, target_h = target_size
        if target_w <= 0 or target_h <= 0:
            return None

        img_w, img_h = image.get_size()
        if img_w <= 0 or img_h <= 0:
            return None

        scale = min(target_w / img_w, target_h / img_h)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        return pygame.transform.smoothscale(image, (new_w, new_h))

    def _build_upgrade_order(self):
        building_index = {
            building_id: idx for idx, building_id in enumerate(self.building_order)
        }

        def sort_key(upgrade_id):
            upgrade = UPGRADES[upgrade_id]
            required_building = get_upgrade_required_building(upgrade_id)
            if required_building in building_index:
                return (
                    0,
                    building_index[required_building],
                    upgrade.get("name", upgrade_id).lower(),
                )
            return (1, len(building_index), upgrade.get("name", upgrade_id).lower())

        return sorted(UPGRADES.keys(), key=sort_key)

    def update_layout(self, width, height):
        self.screen_width = width
        self.screen_height = height

        outer_margin = max(8, width // 100)
        panel_gap = max(8, width // 90)
        vertical_gap = max(8, height // 70)
        card_gap = max(6, height // 110)

        self.title_font = pygame.font.SysFont("Arial", max(22, min(38, width // 32)))
        self.section_font = pygame.font.SysFont("Arial", max(18, min(30, width // 42)))
        self.body_font = pygame.font.SysFont("Arial", max(14, min(24, width // 52)))
        self.small_font = pygame.font.SysFont("Arial", max(12, min(18, width // 75)))
        self.button_font = pygame.font.SysFont("Arial", max(13, min(20, width // 65)))
        self.font_small = pygame.font.SysFont("Arial", max(12, min(18, width // 75)))

        # Dedicated HUD fonts (Larger than standard UI fonts)
        self.hud_total_font = pygame.font.SysFont("Arial", max(40, min(64, width // 20)), bold=True) 
        self.hud_cps_font = pygame.font.SysFont("Arial", max(20, min(32, width // 40)))

        content_h = height - (outer_margin * 2)

        left_w = max(180, int(width * 0.22))
        right_w = max(220, int(width * 0.24))
        center_w = width - (outer_margin * 2) - left_w - right_w - (panel_gap * 2)

        if center_w < 280:
            shrink_needed = 280 - center_w
            left_w = max(150, left_w - shrink_needed // 2)
            right_w = max(180, right_w - shrink_needed // 2)
            center_w = width - (outer_margin * 2) - left_w - right_w - (panel_gap * 2)

        top_h = int((content_h - vertical_gap) * 0.62)
        bottom_h = content_h - top_h - vertical_gap

        self.left_panel = pygame.Rect(outer_margin, outer_margin, left_w, content_h)
        self.center_panel = pygame.Rect(
            self.left_panel.right + panel_gap,
            outer_margin,
            center_w,
            content_h,
        )
        self.right_panel_top = pygame.Rect(
            self.center_panel.right + panel_gap,
            outer_margin,
            right_w,
            top_h,
        )
        self.right_panel_bottom = pygame.Rect(
            self.center_panel.right + panel_gap,
            self.right_panel_top.bottom + vertical_gap,
            right_w,
            bottom_h,
        )

        self.left_panel_rect = self.left_panel
        self.right_panel_rect = pygame.Rect(
            self.right_panel_top.x,
            self.right_panel_top.y,
            right_w,
            content_h,
        )
        self.right_top_half = self.right_panel_top
        self.right_bottom_half = self.right_panel_bottom
        self.layout = {
            "center_x": self.center_panel.x,
            "right_x": self.right_panel_top.x,
        }

        self.building_cards = {}
        self.left_bars = []

        building_slots = len(self.building_order) + 1
        building_available_h = self.left_panel.height
        card_h = (building_available_h - (card_gap * (building_slots - 1))) // building_slots
        card_h = max(72, min(card_h, 125))

        for idx, building_id in enumerate(self.building_order):
            rect = pygame.Rect(
                self.left_panel.x,
                self.left_panel.y + idx * (card_h + card_gap),
                self.left_panel.width,
                card_h,
            )
            self.building_cards[building_id] = rect
            self.left_bars.append(rect)

        self.empty_building_card = pygame.Rect(
            self.left_panel.x,
            self.left_panel.y + len(self.building_order) * (card_h + card_gap),
            self.left_panel.width,
            card_h,
        )

        base_post_w = getattr(settings, "POST_BUTTON_WIDTH", 260)
        base_post_h = getattr(settings, "POST_BUTTON_HEIGHT", 160)
        aspect_ratio = base_post_h / base_post_w

        post_w = min(int(self.center_panel.width * 0.55), 320)
        post_w = max(205, post_w)
        post_h = int(post_w * aspect_ratio) + 50

        center_click_w = post_w + 100
        center_click_h = post_h + 130

        self.click_area = pygame.Rect(0, 0, center_click_w, center_click_h)
        self.click_area.center = self.center_panel.center

        self.click_button_rect = pygame.Rect(0, 0, post_w, post_h)
        self.click_button_rect.centerx = self.center_panel.centerx - 10
        # Align to the bottom of the center panel with a small margin
        self.click_button_rect.bottom = self.center_panel.bottom - (outer_margin * 2) - 15
        
        self.post_button_rect = self.click_button_rect

        if self.button_source_image:
            self.button_image = pygame.transform.smoothscale(
                self.button_source_image,
                (post_w, post_h),
            )

        self.upgrade_cards = {}

        inner_pad = max(8, self.right_panel_top.width // 22)
        title_space = self.title_font.get_height() + 26
        upgrade_gap = max(6, height // 120)

        upgrade_x = self.right_panel_top.x + inner_pad
        upgrade_y = self.right_panel_top.y + title_space
        upgrade_w = self.right_panel_top.width - (inner_pad * 2)

        slots = max(1, len(self.upgrade_order))
        available_h = self.right_panel_top.height - title_space - inner_pad
        upgrade_card_h = (available_h - (upgrade_gap * (slots - 1))) // slots
        upgrade_card_h = max(42, min(upgrade_card_h, 84))

        for idx, upgrade_id in enumerate(self.upgrade_order):
            rect = pygame.Rect(
                upgrade_x,
                upgrade_y + idx * (upgrade_card_h + upgrade_gap),
                upgrade_w,
                upgrade_card_h,
            )
            self.upgrade_cards[upgrade_id] = rect

        if self.button_source_image:
            self.button_image = pygame.transform.smoothscale(
                self.button_source_image,
                (post_w, post_h),
            )

        # --- ADDED FROM menus_not_keeping.py ---
        music_btn_size = max(30, min(42, width // 30))
        screen_margin = 14
        self.music_button_rect = pygame.Rect(
            screen_margin,
            height - music_btn_size - screen_margin,
            music_btn_size,
            music_btn_size,
        )

        self.upgrade_cards = {}
        inner_pad = max(8, self.right_panel_top.width // 22)
        title_space = self.title_font.get_height() + 26
        upgrade_gap = max(8, height // 110)

        upgrade_x = self.right_panel_top.x + inner_pad
        upgrade_y = self.right_panel_top.y + title_space
        upgrade_w = self.right_panel_top.width - (inner_pad * 2)

        # Set larger upgrade card height
        upgrade_card_h = max(88, min(110, self.right_panel_top.height // 4))

        self.upgrade_viewport_rect = pygame.Rect(
            upgrade_x,
            upgrade_y,
            upgrade_w,
            self.right_panel_top.bottom - upgrade_y - inner_pad,
        )

        for idx, upgrade_id in enumerate(self.upgrade_order):
            rect = pygame.Rect(
                upgrade_x,
                upgrade_y + idx * (upgrade_card_h + upgrade_gap),
                upgrade_w,
                upgrade_card_h,
            )
            self.upgrade_cards[upgrade_id] = rect

        self.upgrade_content_height = 0
        if self.upgrade_order:
            last_rect = self.upgrade_cards[self.upgrade_order[-1]]
            self.upgrade_content_height = last_rect.bottom - upgrade_y

        max_scroll = max(0, self.upgrade_content_height - self.upgrade_viewport_rect.height)
        self.upgrade_scroll_offset = max(0, min(self.upgrade_scroll_offset, max_scroll))

        self.building_images = {}
        for building_id, rect in self.building_cards.items():
            source = self.building_source_images.get(building_id)
            if source:
                image_area_w = min(58, max(40, rect.width // 4))
                image_area_h = rect.height - 16
                self.building_images[building_id] = self._scale_card_image(
                    source,
                    (image_area_w, image_area_h),
                )

        self.upgrade_images = {}
        for upgrade_id, rect in self.upgrade_cards.items():
            source = self.upgrade_source_images.get(upgrade_id)
            if source:
                image_area = rect.height - 12
                self.upgrade_images[upgrade_id] = self._scale_card_image(
                    source,
                    (image_area, image_area),
                )

        # Mini-game layout
        switcher_w = min(
            getattr(settings, "MINIGAME_SWITCHER_WIDTH", 50),
            max(40, self.right_panel_bottom.width // 3),
        )
        self.minigame_switcher_rect = pygame.Rect(
            self.right_panel_bottom.x,
            self.right_panel_bottom.y,
            switcher_w,
            self.right_panel_bottom.height,
        )
        self.minigame_content_rect = pygame.Rect(
            self.minigame_switcher_rect.right,
            self.right_panel_bottom.y,
            self.right_panel_bottom.width - switcher_w,
            self.right_panel_bottom.height,
        )

        tab_margin = 6
        tab_w = max(28, switcher_w - tab_margin * 2)
        tab_h = 40
        self.btn_flip_tab = pygame.Rect(
            self.minigame_switcher_rect.x + tab_margin,
            self.minigame_switcher_rect.y + 10,
            tab_w,
            tab_h,
        )
        self.btn_speed_tab = pygame.Rect(
            self.minigame_switcher_rect.x + tab_margin,
            self.minigame_switcher_rect.y + 60,
            tab_w,
            tab_h,
        )

        content = self.minigame_content_rect
        toggle_w = min(140, max(100, content.width - 30))
        self.side_toggle.rect.size = (toggle_w, 30)
        self.range_toggle.rect.size = (toggle_w, 30)
        self.side_toggle.update_pos(content.x + 15, content.y + 100)
        self.range_toggle.update_pos(content.x + 15, content.y + 140)

        self.arrow_l = pygame.Rect(content.x + 15, content.y + 60, 30, 30)
        self.arrow_r = pygame.Rect(content.x + min(content.width - 45, 125), content.y + 60, 30, 30)
        self.flip_btn = pygame.Rect(
            content.x + 15,
            content.y + 185,
            max(110, content.width - 30),
            40,
        )
        self.speed_start_btn = pygame.Rect(
            content.x + 20,
            content.y + 100,
            max(120, content.width - 40),
            50,
        )

        if self.bg_source_image:
            self.bg_image = pygame.transform.smoothscale(
                self.bg_source_image, 
                (width, height)
            )

    def handle_event(self, event):
        # 1. HANDLE UPGRADE PANEL SCROLLING (Mouse Wheel)
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.upgrade_viewport_rect.collidepoint(mouse_pos):
                max_scroll = max(0, self.upgrade_content_height - self.upgrade_viewport_rect.height)
                self.upgrade_scroll_offset -= event.y * self.upgrade_scroll_speed
                self.upgrade_scroll_offset = max(0, min(self.upgrade_scroll_offset, max_scroll))
                return

        # 2. HANDLE MOUSE CLICKS
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Upgrade Panel Scrolling (Buttons 4/5 for older mice/Linux compatibility)
            if self.upgrade_viewport_rect.collidepoint(event.pos):
                max_scroll = max(0, self.upgrade_content_height - self.upgrade_viewport_rect.height)
                if event.button == 4:  # Scroll Up
                    self.upgrade_scroll_offset = max(0, self.upgrade_scroll_offset - self.upgrade_scroll_speed)
                    return
                elif event.button == 5:  # Scroll Down
                    self.upgrade_scroll_offset = min(max_scroll, self.upgrade_scroll_offset + self.upgrade_scroll_speed)
                    return

            # Primary Interactions (Left Click)
            if event.button == 1:
                # Music Button Toggle
                if self.music_button_rect.collidepoint(event.pos):
                    self.game.music_muted = not getattr(self.game, 'music_muted', False)
                    return

                # Minigame Tab Switching (Gated by Buildings)
                if self.btn_flip_tab.collidepoint(event.pos):
                    if can_play_minigame(self.game, "coin_flip"):
                        self.active_minigame = "coin_flip"
                    return
                if self.btn_speed_tab.collidepoint(event.pos):
                    if can_play_minigame(self.game, "speed_click"):
                        self.active_minigame = "speed_click"
                    return

                # Active Minigame Interactions
                if self.active_minigame == "coin_flip":
                    side = self.side_toggle.handle_event(event)
                    range_val = self.range_toggle.handle_event(event)
                    
                    if self.arrow_l.collidepoint(event.pos) and self.coin_idx > 0:
                        self.coin_idx -= 1
                        return
                    if self.arrow_r.collidepoint(event.pos) and self.coin_idx < len(COIN_OPTIONS) - 1:
                        self.coin_idx += 1
                        return
                    if self.flip_btn.collidepoint(event.pos):
                        self.bet_result_text = process_coin_bet(self.game, COIN_OPTIONS[self.coin_idx], side, range_val)
                        clear_minigame_gates(self.game, "coin_flip") # Clear 20-level gates
                        return

                elif self.active_minigame == "speed_click":
                    if not self.speed_active:
                        if self.speed_start_btn.collidepoint(event.pos) and time.time() > self.speed_cooldown_end:
                            if start_speed_click_session(self.game):
                                self.speed_active = True
                                self.speed_targets_hit = 0
                                self.speed_round_start_time = pygame.time.get_ticks()
                                self._spawn_speed_target()
                                self.speed_msg = "CLICK!"
                            else:
                                self.speed_msg = "Too Poor!"
                            return
                    else:
                        if self.speed_current_target and self.speed_current_target.collidepoint(event.pos):
                            process_speed_click_hit(self.game)
                            self.speed_targets_hit += 1
                            self.speed_current_target = None
                            if self.speed_targets_hit < self.speed_max_targets:
                                self._spawn_speed_target()
                            else:
                                self._end_speed_round() # This method should call clear_minigame_gates
                            return

                # Main Post Click (Includes Floating Effect)
                if self.click_button_rect.collidepoint(event.pos):
                    val = get_click_value(self.game)
                    self.click_effects.append({
                        "pos": list(event.pos),
                        "text": f"+{format_chud_amount(val)}",
                        "alpha": 255,
                        "timer": 1.0
                    })
                    add_manual_click(self.game)
                    return

                # Buy Buildings
                for building_id, rect in self.building_cards.items():
                    if rect.collidepoint(event.pos):
                        buy_building(self.game, building_id)
                        return

                # Buy Upgrades (Scroll-Aware and Viewport-Clipped)
                for upgrade_id, rect in self.upgrade_cards.items():
                    draw_rect = rect.move(0, -self.upgrade_scroll_offset)
                    if self.upgrade_viewport_rect.collidepoint(event.pos) and draw_rect.collidepoint(event.pos):
                        buy_upgrade(self.game, upgrade_id)
                        return

        # 3. HANDLE MOUSE MOTION (Hover Tooltips)
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_building_id = None
            self.hovered_upgrade_id = None

            # Building Hovers
            for building_id, rect in self.building_cards.items():
                if rect.collidepoint(event.pos):
                    self.hovered_building_id = building_id
                    return

            # Upgrade Hovers (Only triggers if mouse is inside the top panel viewport)
            for upgrade_id, rect in self.upgrade_cards.items():
                draw_rect = rect.move(0, -self.upgrade_scroll_offset)
                if self.upgrade_viewport_rect.collidepoint(event.pos) and draw_rect.collidepoint(event.pos):
                    self.hovered_upgrade_id = upgrade_id
                    return
    def update(self, dt):
        update_game(self.game, dt)

        # --- ANIMATE CLICK EFFECTS ---
        for effect in self.click_effects[:]:
            effect["timer"] -= dt
            effect["pos"][1] -= 80 * dt  # Move upward 80 pixels/sec
            # Fade alpha linearly based on remaining time
            effect["alpha"] = max(0, int(255 * effect["timer"])) 
            
            # Remove from list when timer runs out
            if effect["timer"] <= 0:
                self.click_effects.remove(effect)

        if self.speed_active:
            curr = pygame.time.get_ticks()

            if curr - self.speed_round_start_time > 15000:
                self._end_speed_round()

            elif self.speed_current_target and (
                curr - self.speed_target_spawn_time > self.speed_target_lifetime
            ):
                if self.speed_targets_hit < self.speed_max_targets:
                    self._spawn_speed_target()
                else:
                    self._end_speed_round()

    def draw(self, screen):
        # 1. Draw Background Image first
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
            screen.fill(settings.GRAY) # Fallback

        self._draw_panels(screen)
        self._draw_building_sidebar(screen)
        self._draw_center_game_panel(screen)
        self._draw_upgrade_panel(screen)
        self._draw_minigame_area(screen)
        self._draw_hover_tooltip(screen)

    def _draw_panels(self, screen):
        border = getattr(settings, "PANEL_BORDER", (0, 0, 0))

        # Helper to draw transparent panels
        def draw_alpha_rect(rect, color):
            # Only perform drawing if the panel has some opacity
            if color[3] > 0:
                surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                surf.fill(color)
                screen.blit(surf, (rect.x, rect.y))
                # Draw the border only for visible panels
                pygame.draw.rect(screen, border, rect, 1)
            # If color[3] is 0 (Center Panel), we skip the fill and the border entirely

        draw_alpha_rect(self.left_panel, settings.LEFT_PANEL_BG)
        draw_alpha_rect(self.center_panel, settings.CENTER_PANEL_BG)
        draw_alpha_rect(self.right_panel_top, settings.RIGHT_PANEL_BG)
        draw_alpha_rect(self.right_panel_bottom, settings.RIGHT_PANEL_BG)

    def _draw_building_sidebar(self, screen):
        border = getattr(settings, "PANEL_BORDER", getattr(settings, "BLACK", (0, 0, 0)))
        black = getattr(settings, "BLACK", (0, 0, 0))
        card_bg = getattr(settings, "BUILDING_CARD_BG", (255, 255, 255))
        disabled_bg = getattr(settings, "BUILDING_DISABLED_BG", (218, 218, 218))
        hover_boost = 10

        for building_id in self.building_order:
            rect = self.building_cards[building_id]
            building = BUILDINGS[building_id]
            owned = self.game.buildings_owned[building_id]
            cost = get_building_cost(building_id, owned)
            affordable = self.game.chuds >= cost
            hovered = self.hovered_building_id == building_id

            fill = card_bg if affordable else disabled_bg
            if hovered:
                fill = tuple(min(255, c + hover_boost) for c in fill)

            card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            # Ensure 'fill' has 4 values, e.g., (255, 255, 255, 200)
            if len(fill) == 3: fill = (*fill, 200) 
            card_surf.fill(fill)
            screen.blit(card_surf, (rect.x, rect.y))
            pygame.draw.rect(screen, border, rect, 1)

            icon = self.building_images.get(building_id)
            text_x = rect.x + 14

            if icon:
                icon_rect = icon.get_rect()
                icon_rect.left = rect.x + 8
                icon_rect.centery = rect.centery
                screen.blit(icon, icon_rect)
                text_x = icon_rect.right + 10
            else:
                placeholder = pygame.Rect(rect.x + 8, rect.y + 8, 48, rect.height - 16)
                pygame.draw.rect(screen, (180, 180, 180), placeholder, border_radius=6)
                pygame.draw.rect(screen, border, placeholder, 1, border_radius=6)
                text_x = placeholder.right + 10

            title = self.section_font.render(building.get("name", building_id.title()), True, black)
            owned_text = self.body_font.render(f"Owned: {owned}", True, black)
            cps_text = self.small_font.render(
                f"+{format_chud_amount(building['base_cps'])} CHUD/sec each",
                True,
                black,
            )
            cost_text = self.small_font.render(
                f"Next cost: {format_chud_amount(cost)}",
                True,
                black,
            )

            screen.blit(title, (text_x, rect.y + 10))
            screen.blit(owned_text, (text_x, rect.y + 40))
            screen.blit(cps_text, (text_x, rect.y + 64))
            screen.blit(cost_text, (text_x, rect.y + 86))

        coming_bg = getattr(settings, "BUILDING_DISABLED_BG", (218, 218, 218))
        if self.empty_building_card.bottom <= self.left_panel.bottom:
            pygame.draw.rect(screen, coming_bg, self.empty_building_card)
            pygame.draw.rect(screen, border, self.empty_building_card, 1)
            coming_title = self.section_font.render("Coming Soon", True, black)
            coming_text = self.small_font.render("Future building slot", True, black)
            screen.blit(
                coming_title,
                (self.empty_building_card.x + 14, self.empty_building_card.y + 18),
            )
            screen.blit(
                coming_text,
                (self.empty_building_card.x + 14, self.empty_building_card.y + 52),
            )

    def _spawn_speed_target(self):
        c = self.minigame_content_rect
        size = max(20, 50 - (self.speed_targets_hit * 2))
        x = random.randint(c.x + 10, max(c.x + 11, c.right - size - 10))
        y = random.randint(c.y + 60, max(c.y + 61, c.bottom - size - 10))
        self.speed_current_target = pygame.Rect(x, y, size, size)
        self.speed_target_spawn_time = pygame.time.get_ticks()

    def _end_speed_round(self):
        self.speed_active = False
        self.speed_current_target = None
        self.speed_cooldown_end = time.time() + SPEED_CLICK_COOLDOWN
        self.speed_msg = "Finished!"

    def _draw_center_game_panel(self, screen):
        black = getattr(settings, "BLACK", (0, 0, 0))
        dark_gray = getattr(settings, "DARK_GRAY", (60, 60, 60))
        light_blue = getattr(settings, "LIGHT_BLUE", (160, 200, 255))

        # (Keep the HUD stats at the top)
        formatted_total = format_chud_amount(self.game.chuds)
        formatted_cps = format_chud_amount(self.game.total_cps)
        # Use the new hud_total_font and hud_cps_font here
        total_text = self.hud_total_font.render(f"{formatted_total} CHUDs", True, black)
        cps_text = self.hud_cps_font.render(f"CHUD/sec: {formatted_cps}", True, dark_gray)
        # Recalculate rects for the larger text sizes to keep them centered
        total_rect = total_text.get_rect(centerx=self.center_panel.centerx, top=self.center_panel.top + 40)
        cps_rect = cps_text.get_rect(centerx=total_rect.centerx, top=total_rect.bottom + 10)
        screen.blit(total_text, total_rect)
        screen.blit(cps_text, cps_rect)

        self._draw_click_effects(screen)

        button_bg = getattr(settings, "MUSIC_BUTTON_BG", (245, 245, 245))
        button_muted_bg = getattr(settings, "MUSIC_BUTTON_MUTED_BG", (200, 160, 160))
        button_border = getattr(settings, "MUSIC_BUTTON_BORDER", (110, 110, 110))

        is_muted = getattr(self.game, 'music_muted', False)
        fill = button_muted_bg if is_muted else button_bg

        pygame.draw.rect(screen, fill, self.music_button_rect, border_radius=8)
        pygame.draw.rect(screen, button_border, self.music_button_rect, 1, border_radius=8)

        icon_text = "M" if not is_muted else "X"
        icon = self.body_font.render(icon_text, True, getattr(settings, "BLACK", (0,0,0)))
        icon_rect = icon.get_rect(center=self.music_button_rect.center)
        screen.blit(icon, icon_rect)
        # --- REMOVED: CHUD Clicker title ---

        # # Draw the button image (if it exists) or just the colored rect
        # if self.button_image:
        #     screen.blit(self.button_image, self.click_button_rect)
        # else:
        #     # If no image, just draw a clean rectangle without "Click" text
        #     pygame.draw.rect(screen, light_blue, self.click_button_rect, border_radius=12)
    
    def _draw_click_effects(self, screen):
        """Renders floating text with transparency."""
        for effect in self.click_effects:
            # Create a temporary surface to support per-pixel alpha
            text_surf = self.body_font.render(effect["text"], True, (0, 0, 0)) # Green text
            text_surf.set_alpha(effect["alpha"])
            screen.blit(text_surf, effect["pos"])
    # Replace entire method in menus.py
    def _draw_upgrade_panel(self, screen):
        black = getattr(settings, "BLACK", (0, 0, 0))
        card_bg = getattr(settings, "CARD_BG", (255, 255, 255))
        disabled_card_bg = getattr(settings, "BUILDING_DISABLED_BG", (218, 218, 218))
        border = getattr(settings, "PANEL_BORDER", black)
        locked_card_bg = getattr(settings, "UPGRADE_LOCKED_BG", (228, 190, 190))
        locked_text_color = getattr(settings, "UPGRADE_LOCKED_TEXT", (120, 45, 45))

        title = self.title_font.render("Upgrades", True, black)
        screen.blit(title, (self.right_panel_top.x + 18, self.right_panel_top.y + 14))

        viewport = self.upgrade_viewport_rect
        old_clip = screen.get_clip()
        screen.set_clip(viewport)

        for upgrade_id in self.upgrade_order:
            base_rect = self.upgrade_cards[upgrade_id]
            rect = base_rect.move(0, -self.upgrade_scroll_offset)

            # Skip drawing if outside viewport
            if rect.bottom < viewport.top or rect.top > viewport.bottom:
                continue

            upgrade = UPGRADES[upgrade_id]
            level = self.game.upgrades_owned[upgrade_id]
            cost = get_upgrade_cost(upgrade_id, level)
            unlocked = is_upgrade_unlocked(self.game, upgrade_id)
            affordable = unlocked and self.game.chuds >= cost
            hovered = self.hovered_upgrade_id == upgrade_id

            if not unlocked:
                fill_color = locked_card_bg
            elif affordable:
                fill_color = card_bg
            else:
                fill_color = disabled_card_bg

            if hovered:
                fill_color = tuple(min(255, c + 8) for c in fill_color)

            pygame.draw.rect(screen, fill_color, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 1, border_radius=8)

            icon = self.upgrade_images.get(upgrade_id)
            text_x = rect.x + 10

            if icon:
                icon_rect = icon.get_rect()
                icon_rect.left = rect.x + 8
                icon_rect.centery = rect.centery
                screen.blit(icon, icon_rect)
                text_x = icon_rect.right + 10

            name_text = self.body_font.render(upgrade["name"], True, black if unlocked else locked_text_color)
            level_text = self.small_font.render(f"Lv. {level}", True, black if unlocked else locked_text_color)

            screen.blit(name_text, (text_x, rect.y + 10))
            screen.blit(level_text, (rect.right - level_text.get_width() - 10, rect.y + 12))

            if unlocked:
                detail_text = self.small_font.render(f"Cost: {format_chud_amount(cost)}", True, black)
            else:
                required_building = get_upgrade_required_building(upgrade_id)
                required_name = BUILDINGS[required_building]["name"] if required_building in BUILDINGS else required_building
                detail_text = self.small_font.render(f"Need: {required_name}", True, locked_text_color)

            screen.blit(detail_text, (text_x, rect.bottom - detail_text.get_height() - 10))

        screen.set_clip(old_clip)

        # Draw Scrollbar
        if self.upgrade_content_height > self.upgrade_viewport_rect.height:
            track_rect = pygame.Rect(self.upgrade_viewport_rect.right - 6, self.upgrade_viewport_rect.top, 6, self.upgrade_viewport_rect.height)
            pygame.draw.rect(screen, (190, 190, 190), track_rect, border_radius=4)

            thumb_height = max(30, int(viewport.height * (viewport.height / self.upgrade_content_height)))
            max_scroll = self.upgrade_content_height - viewport.height
            thumb_y = track_rect.y + int((self.upgrade_scroll_offset / max_scroll) * (track_rect.height - thumb_height))
            pygame.draw.rect(screen, (110, 110, 110), pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height), border_radius=4)
    def _draw_button(self, screen, rect, label, enabled, force_color=None):
        button_bg = getattr(settings, "BUTTON_BG", (25, 124, 214))
        button_disabled = getattr(settings, "BUTTON_DISABLED", (140, 140, 140))
        white = getattr(settings, "WHITE", (255, 255, 255))
        border = getattr(settings, "PANEL_BORDER", getattr(settings, "BLACK", (0, 0, 0)))

        color = force_color if force_color is not None else (
            button_bg if enabled else button_disabled
        )
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 1, border_radius=8)

        text = self.button_font.render(label, True, white)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    def _draw_minigame_area(self, screen):
        dark_gray = getattr(settings, "DARK_GRAY", (80, 80, 80))
        black = getattr(settings, "BLACK", (0, 0, 0))
        white = getattr(settings, "WHITE", (255, 255, 255))
        blue = getattr(settings, "BLUE", (0, 121, 211))
        coin_gold = getattr(settings, "COIN_GOLD", (255, 215, 0))
        border = getattr(settings, "PANEL_BORDER", black)

        pygame.draw.rect(screen, dark_gray, self.minigame_switcher_rect)
        pygame.draw.rect(screen, border, self.minigame_switcher_rect, 1)

        flip_color = blue if self.active_minigame == "coin_flip" else (110, 110, 110)
        speed_color = coin_gold if self.active_minigame == "speed_click" else (110, 110, 110)

        pygame.draw.rect(screen, flip_color, self.btn_flip_tab, border_radius=8)
        pygame.draw.rect(screen, speed_color, self.btn_speed_tab, border_radius=8)
        pygame.draw.rect(screen, border, self.btn_flip_tab, 1, border_radius=8)
        pygame.draw.rect(screen, border, self.btn_speed_tab, 1, border_radius=8)

        flip_text = self.button_font.render("C", True, white)
        speed_text = self.button_font.render("S", True, black if self.active_minigame == "speed_click" else white)
        screen.blit(flip_text, flip_text.get_rect(center=self.btn_flip_tab.center))
        screen.blit(speed_text, speed_text.get_rect(center=self.btn_speed_tab.center))

        if self.active_minigame == "coin_flip":
            self._draw_coin_flip(screen)
        elif self.active_minigame == "speed_click":
            self._draw_speed_click(screen)

    def _draw_coin_flip(self, screen):
        c = self.minigame_content_rect
        black = getattr(settings, "BLACK", (0, 0, 0))
        white = getattr(settings, "WHITE", (255, 255, 255))
        dark_gray = getattr(settings, "DARK_GRAY", (80, 80, 80))
        blue = getattr(settings, "BLUE", (0, 121, 211))

        title = self.section_font.render("CoinBet Casino", True, black)
        screen.blit(title, (c.x + 15, c.y + 10))

        pygame.draw.rect(screen, dark_gray, self.arrow_l, border_radius=5)
        pygame.draw.rect(screen, dark_gray, self.arrow_r, border_radius=5)

        l_txt = self.button_font.render("<", True, white)
        r_txt = self.button_font.render(">", True, white)
        screen.blit(l_txt, l_txt.get_rect(center=self.arrow_l.center))
        screen.blit(r_txt, r_txt.get_rect(center=self.arrow_r.center))

        val_text = self.body_font.render(f"{COIN_OPTIONS[self.coin_idx]} Coins", True, black)
        screen.blit(val_text, (c.x + 55, c.y + 62))

        self.side_toggle.draw(screen, self.small_font, blue)
        self.range_toggle.draw(screen, self.small_font, blue)

        self._draw_button(screen, self.flip_btn, "FLIP CHUDs", True, force_color=(50, 200, 50))

        res_txt = self.small_font.render(self.bet_result_text, True, black)
        screen.blit(res_txt, (c.x + 15, c.y + 235))

    def _draw_speed_click(self, screen):
        c = self.minigame_content_rect
        black = getattr(settings, "BLACK", (0, 0, 0))
        white = getattr(settings, "WHITE", (255, 255, 255))

        title = self.section_font.render("Aim Train", True, black)
        screen.blit(title, (c.x + 15, c.y + 10))

        msg = self.small_font.render(self.speed_msg, True, black)
        screen.blit(msg, (c.x + 15, c.y + 40))

        if not self.speed_active:
            on_cd = time.time() < self.speed_cooldown_end
            color = (100, 100, 100) if on_cd else (70, 200, 70)
            self._draw_button(
                screen,
                self.speed_start_btn,
                (
                    f"Wait {int(self.speed_cooldown_end - time.time())}s"
                    if on_cd
                    else f"START ({format_chud_amount(get_speed_click_cost(self.game))})"
                ),
                not on_cd,
                force_color=color,
            )
        else:
            elapsed = pygame.time.get_ticks() - self.speed_round_start_time
            time_left = max(0, 15 - (elapsed // 1000))
            timer_color = (200, 0, 0) if time_left < 5 else black
            timer_surf = self.small_font.render(f"Time: {time_left}s", True, timer_color)
            screen.blit(timer_surf, (c.right - 85, c.y + 40))

            if self.speed_current_target:
                pygame.draw.rect(screen, (200, 0, 0), self.speed_current_target, border_radius=4)
                pygame.draw.rect(screen, white, self.speed_current_target, 2, border_radius=4)

            prog = self.small_font.render(
                f"Hits: {self.speed_targets_hit}/{self.speed_max_targets}",
                True,
                black,
            )
            screen.blit(prog, (c.x + 15, c.bottom - 30))

    def _draw_hover_tooltip(self, screen):
        lines = None
        if self.hovered_building_id:
            lines = self._get_building_tooltip_lines(self.hovered_building_id)
        elif self.hovered_upgrade_id:
            lines = self._get_upgrade_tooltip_lines(self.hovered_upgrade_id)

        if not lines:
            return

        mouse_pos = pygame.mouse.get_pos()
        line_height = 22
        tip_w = 285
        tip_h = 14 + len(lines) * line_height
        tip_x = min(mouse_pos[0] + 18, self.screen_width - tip_w - 12)
        tip_y = min(mouse_pos[1] + 18, self.screen_height - tip_h - 12)
        tip_rect = pygame.Rect(tip_x, tip_y, tip_w, tip_h)

        tip_surf = pygame.Surface((tip_rect.width, tip_rect.height), pygame.SRCALPHA)
        tip_surf.fill((20, 20, 20, 230))
        screen.blit(tip_surf, tip_rect.topleft)
        pygame.draw.rect(screen, getattr(settings, "WHITE", (255, 255, 255)), tip_rect, 2)

        for idx, line in enumerate(lines):
            text = self.font_small.render(
                line,
                True,
                getattr(settings, "WHITE", (255, 255, 255)),
            )
            screen.blit(text, (tip_x + 12, tip_y + 10 + idx * line_height))

    def _get_building_tooltip_lines(self, building_id):
        building = BUILDINGS[building_id]
        owned = self.game.buildings_owned[building_id]
        cost = get_building_cost(building_id, owned)
        return [
            f"{building.get('name', building_id.title())}",
            f"Owned: {owned}",
            f"CPS each: {format_chud_amount(building['base_cps'])}",
            f"Next cost: {format_chud_amount(cost)}",
        ]

    def _get_upgrade_tooltip_lines(self, upgrade_id):
        upgrade = UPGRADES[upgrade_id]
        level = self.game.upgrades_owned[upgrade_id]
        lines = [upgrade.get("name", upgrade_id), f"Level: {level}"]

        required_building = get_upgrade_required_building(upgrade_id)
        if required_building:
            required_name = BUILDINGS.get(required_building, {}).get("name", required_building)
            lines.append(f"Need building: {required_name}")

        upgrade_type = upgrade.get("type")
        value = upgrade.get("value", 1)
        target = upgrade.get("target")

        if upgrade_type == "building_multiplier" and target:
            target_name = BUILDINGS.get(target, {}).get("name", target)
            lines.append(f"Effect: x{value:g} to {target_name}")
        elif upgrade_type == "global_multiplier":
            lines.append(f"Effect: x{value:g} to all CPS")
        elif upgrade_type == "click_multiplier":
            lines.append(f"Effect: x{value:g} to click power")
        elif upgrade_type == "mini_game_multiplier":
            lines.append(f"Effect: x{value:g} to mini games")

        lines.append(f"Next cost: {format_chud_amount(get_upgrade_cost(upgrade_id, level))}")
        return lines