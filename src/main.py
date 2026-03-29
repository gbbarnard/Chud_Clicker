import pygame
import settings
from menus import MenuManager

def main():
    # Initialize Pygame
    pygame.init()
    
    # Setup Display
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), 
        pygame.RESIZABLE
    )
    pygame.display.set_caption("CHUD Collector 2026")
    clock = pygame.time.Clock()

    # Initialize Managers
    menu_manager = MenuManager()

    running = True
    while running:

        dt = clock.tick(settings.FPS) / 1000.0

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            else:
                # Pass events to the menu manager
                menu_manager.handle_event(event)

            # 2. DETECT RESIZE
            if event.type == pygame.VIDEORESIZE:
                # Update the display surface to the new size
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # Tell the menu manager to reposition its elements
                menu_manager.update_layout(event.w, event.h)
            
            
        menu_manager.update(dt)
    

        # 3. Rendering
        screen.fill(settings.GRAY) # Background
        
        menu_manager.draw(screen) # Draw UI

        pygame.display.flip()
        
        # 4. Cap Frame Rate
        clock.tick(settings.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
