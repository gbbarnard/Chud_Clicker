import pygame
import settings

class MenuManager:
    def __init__(self):
        self.chud_total = 0
        self.font = pygame.font.SysFont("Arial", settings.FONT_SIZE)
        
        # Define the Button Rectangle (Centered)
        self.button_rect = pygame.Rect(
            (settings.SCREEN_WIDTH // 2) - (settings.BUTTON_WIDTH // 2),
            (settings.SCREEN_HEIGHT // 2) - (settings.BUTTON_HEIGHT // 2),
            settings.BUTTON_WIDTH,
            settings.BUTTON_HEIGHT
        )

    def handle_event(self, event):
        """Checks if the button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                if self.button_rect.collidepoint(event.pos):
                    self.chud_total += 1
                    print(f"Post successful! Total CHUDs: {self.chud_total}")

    def draw(self, screen):
        """Renders the UI elements to the screen."""
        # Draw the Button
        pygame.draw.rect(screen, settings.BLUE, self.button_rect)
        
        # Button Text
        btn_text = self.font.render("Reddit Post", True, settings.WHITE)
        btn_text_rect = btn_text.get_rect(center=self.button_rect.center)
        screen.blit(btn_text, btn_text_rect)

        # CHUD Counter Text
        counter_text = self.font.render(f"CHUD Total: {self.chud_total}", True, settings.BLACK)
        screen.blit(counter_text, (50, 50))
