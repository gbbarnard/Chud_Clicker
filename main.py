import pygame
import settings
from menus import MenuManager

def main():
    # Initialize Pygame
    pygame.init()
    
    # Setup Display
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("CHUD Collector 2026")
    clock = pygame.time.Clock()

    # Initialize Managers
    menu_manager = MenuManager()

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to the menu manager
            menu_manager.handle_event(event)

        # 2. Update Logic (none needed for this simple demo)

        # 3. Rendering
        screen.fill(settings.GRAY) # Background
        
        menu_manager.draw(screen) # Draw UI

        pygame.display.flip()
        
        # 4. Cap Frame Rate
        clock.tick(settings.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
