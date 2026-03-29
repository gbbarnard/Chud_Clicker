import pygame
import random
import time

# --- Configuration & Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GOLD = (255, 215, 0)
DARK_GREY = (30, 30, 30)
BUTTON_COLOR = (70, 70, 70)

class SpeedClicker:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Speed Clicker: Chuddin Time")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.btn_font = pygame.font.SysFont("Arial", 32, bold=True)
        
        # Game Balance Variables
        self.chuds_per_second = 10 
        
        # Points & State
        self.total_points = 5000.0
        self.game_active = False
        self.cooldown_end_time = 0
        self.last_result_msg = "Ready to play?"
        
        # Button Rect
        self.start_btn_rect = pygame.Rect(250, 250, 300, 80)
        
        # Round Variables
        self.round_start_time = 0
        self.targets_spawned = 0
        self.max_spawns = 15
        self.current_target = None 
        self.target_spawn_time = 0
        self.target_lifetime = 1500 

    def get_entry_cost(self):
        # cost is chuds_per_second * 180
        # Implementing as 35% of point total per instructions
        return self.total_points * 0.35

    def spawn_target(self):
        size = max(15, 65 - (self.targets_spawned * 3)) 
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(120, SCREEN_HEIGHT - 100)
        self.current_target = pygame.Rect(x, y, size, size)
        self.target_spawn_time = pygame.time.get_ticks()
        self.targets_spawned += 1

    def start_game(self):
        current_time = time.time()
        
        if current_time < self.cooldown_end_time:
            return

        cost = self.get_entry_cost()
        
        if self.total_points >= cost and self.total_points > 0:
            self.total_points -= cost
            self.game_active = True
            self.targets_spawned = 0
            self.round_start_time = pygame.time.get_ticks()
            self.spawn_target()
            self.last_result_msg = "CLICK FAST!"
        else:
            self.last_result_msg = "Insufficient Funds!"

    def end_game(self):
        self.game_active = False
        self.current_target = None
        self.cooldown_end_time = time.time() + 10 
        self.last_result_msg = "Cooldown: 10s"

    def draw_button(self):
        current_time = time.time()
        cost = self.get_entry_cost()
        on_cooldown = current_time < self.cooldown_end_time
        can_afford = self.total_points >= cost and self.total_points > 0
        
        # Determine transparency (Alpha)
        # If can't afford or on cooldown, make it very transparent
        alpha = 255 if (can_afford and not on_cooldown) else 80
        
        # Create a surface for the button to handle transparency
        s = pygame.Surface((self.start_btn_rect.width, self.start_btn_rect.height), pygame.SRCALPHA)
        s.fill((70, 70, 70, alpha))
        self.screen.blit(s, (self.start_btn_rect.x, self.start_btn_rect.y))
        
        # Draw Text on Button
        btn_text = "CHUDDIN TIME?" if not on_cooldown else f"{int(self.cooldown_end_time - current_time)}s"
        text_color = (255, 215, 0, alpha)
        text_surf = self.btn_font.render(btn_text, True, text_color)
        text_rect = text_surf.get_rect(center=self.start_btn_rect.center)
        self.screen.blit(text_surf, text_rect)

    def run(self):
        running = True
        while running:
            curr_ticks = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Logic for clicking the Start Button
                    if not self.game_active:
                        if self.start_btn_rect.collidepoint(mouse_pos):
                            self.start_game()
                    
                    # Logic for clicking the targets
                    elif self.game_active:
                        if self.current_target and self.current_target.collidepoint(mouse_pos):
                            # each successful click grants 500 points
                            # reward is chuds_per_second * 30
                            self.total_points += 500 
                            self.current_target = None 
                            
                            if self.targets_spawned < self.max_spawns:
                                self.spawn_target()
                            else:
                                self.end_game()

            # --- Logic ---
            if self.game_active:
                if curr_ticks - self.round_start_time > 30000:
                    self.end_game()
                
                if self.current_target and (curr_ticks - self.target_spawn_time > self.target_lifetime):
                    if self.targets_spawned < self.max_spawns:
                        self.spawn_target()
                    else:
                        self.end_game()

            # --- Drawing ---
            self.screen.fill(DARK_GREY)
            
            # Draw Points and Message
            pt_text = self.font.render(f"Budget: {int(self.total_points)} pts", True, GOLD)
            msg_text = self.font.render(self.last_result_msg, True, WHITE)
            self.screen.blit(pt_text, (20, 20))
            self.screen.blit(msg_text, (20, 60))
            
            if not self.game_active:
                self.draw_button()
                cost_text = self.font.render(f"Cost to play: {int(self.get_entry_cost())}", True, WHITE)
                self.screen.blit(cost_text, (300, 340))
            else:
                # Draw In-Game Info
                timer = 30 - (curr_ticks - self.round_start_time) // 1000
                t_text = self.font.render(f"Time: {timer}s | Targets: {self.targets_spawned}/15", True, WHITE)
                self.screen.blit(t_text, (500, 20))
                
                if self.current_target:
                    pygame.draw.rect(self.screen, RED, self.current_target)
                    pygame.draw.rect(self.screen, WHITE, self.current_target, 2)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    SpeedClicker().run()