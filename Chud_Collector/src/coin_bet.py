import pygame
import random
import math

# --- Configuration & Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("High-Stakes Coin Flip")
font = pygame.font.SysFont("Arial", 24)
bold_font = pygame.font.SysFont("Arial", 28, bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 250)
DARK_GRAY = (40, 40, 40)

# Game State
player_points = 1000.0
coin_options = [1, 3, 5, 7]
coin_index = 0  # Starts at 1 coin
cost_multipliers = {1: 0.05, 3: 0.15, 5: 0.25, 7: 0.45}

# Selection States
bet_side = "Heads"
bet_range = "Over"
last_result_text = "Place your bet!"

# --- Load Assets ---
try:
    coin_img = pygame.image.load("coin.png")
    coin_img = pygame.transform.scale(coin_img, (60, 60))
except:
    coin_img = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(coin_img, GOLD, (30, 30), 30)
    pygame.draw.circle(coin_img, BLACK, (30, 30), 30, 2)

# --- UI Helpers ---

def draw_text(text, x, y, color=WHITE, center=False, use_bold=False):
    f = bold_font if use_bold else font
    surf = f.render(text, True, color)
    rect = surf.get_rect(topleft=(x, y))
    if center: rect.center = (x, y)
    screen.blit(surf, rect)

class Toggle:
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.index = 0
    
    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=15)
        half_w = self.rect.width // 2
        toggle_rect = pygame.Rect(self.rect.x + (self.index * half_w), self.rect.y, half_w, self.rect.height)
        pygame.draw.rect(surface, BLUE, toggle_rect, border_radius=15)
        draw_text(self.options[0], self.rect.x + half_w//2, self.rect.centery, center=True)
        draw_text(self.options[1], self.rect.x + half_w + half_w//2, self.rect.centery, center=True)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.index = 1 - self.index
        return self.options[self.index]

# --- Instances & Rects ---
side_toggle = Toggle(300, 250, 200, 40, ["Heads", "Tails"])
range_toggle = Toggle(300, 320, 200, 40, ["Over", "Under"])

# Arrow Button Rects
left_arrow_rect = pygame.Rect(300, 180, 40, 40)
right_arrow_rect = pygame.Rect(460, 180, 40, 40)
bet_button = pygame.Rect(300, 450, 200, 60)

def flip_coins():
    global player_points, last_result_text
    num_coins = coin_options[coin_index]
    cost = player_points * cost_multipliers[num_coins]
    
    results = [random.choice(["Heads", "Tails"]) for _ in range(num_coins)]
    side_count = results.count(bet_side)
    
    half = num_coins / 2
    is_win = False
    if bet_range == "Over" and side_count > half:
        is_win = True
    elif bet_range == "Under" and side_count <= half:
        is_win = True
        
    if is_win:
        reward = cost * (math.pow(1.6, num_coins))
        player_points += reward
        last_result_text = f"WIN! +{int(reward)} pts ({side_count} {bet_side})"
    else:
        player_points -= cost
        last_result_text = f"LOST! -{int(cost)} pts ({side_count} {bet_side})"

# --- Main Loop ---
running = True
while running:
    screen.fill(BLACK)
    
    # Points & Visuals
    draw_text("POINT TOTAL: " + str(int(player_points)), WIDTH//2, 50, GOLD, center=True, use_bold=True)
    screen.blit(coin_img, (WIDTH//2 - 30, 100))
    
    # Labels
    draw_text("Coins:", 200, 185)
    draw_text("Side:", 200, 255)
    draw_text("Guess:", 200, 325)
    
    # --- Arrow Selector UI ---
    # Left Arrow
    pygame.draw.rect(screen, DARK_GRAY, left_arrow_rect, border_radius=5)
    draw_text("<", left_arrow_rect.centerx, left_arrow_rect.centery, center=True)
    
    # Display Value Box
    val_box = pygame.Rect(345, 180, 110, 40)
    pygame.draw.rect(screen, (60, 60, 60), val_box)
    draw_text(str(coin_options[coin_index]), val_box.centerx, val_box.centery, center=True, use_bold=True)
    
    # Right Arrow
    pygame.draw.rect(screen, DARK_GRAY, right_arrow_rect, border_radius=5)
    draw_text(">", right_arrow_rect.centerx, right_arrow_rect.centery, center=True)

    # Toggles & Button
    side_toggle.draw(screen)
    range_toggle.draw(screen)
    
    pygame.draw.rect(screen, GREEN, bet_button, border_radius=10)
    draw_text("FLIP COINS", bet_button.centerx, bet_button.centery, center=True, use_bold=True)
    
    # Result display
    res_col = GREEN if "WIN" in last_result_text else RED if "LOST" in last_result_text else WHITE
    draw_text(last_result_text, WIDTH//2, 550, res_col, center=True)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        bet_side = side_toggle.handle_event(event)
        bet_range = range_toggle.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle Arrow Clicks
            if left_arrow_rect.collidepoint(event.pos):
                if coin_index > 0:
                    coin_index -= 1
            
            if right_arrow_rect.collidepoint(event.pos):
                if coin_index < len(coin_options) - 1:
                    coin_index += 1
            
            # Handle Bet Button
            if bet_button.collidepoint(event.pos):
                if player_points > 1:
                    flip_coins()
                else:
                    last_result_text = "Game Over! No points."

    pygame.display.flip()

pygame.quit()