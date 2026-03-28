import pygame
import settings
from menus import MenuManager

def main():
<<<<<<< HEAD
    pygame.init()

=======
    # Initialize Pygame
    pygame.init()
    
    # Setup Display
>>>>>>> af8620e168fd4c871db8db461cdaf0fe24f43d37
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("CHUD Collector 2026")
    clock = pygame.time.Clock()

<<<<<<< HEAD
=======
    # Initialize Managers
>>>>>>> af8620e168fd4c871db8db461cdaf0fe24f43d37
    menu_manager = MenuManager()

    running = True
    while running:
<<<<<<< HEAD
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            menu_manager.handle_event(event)

        menu_manager.update(dt)

        screen.fill(settings.GRAY)
        menu_manager.draw(screen)

        pygame.display.flip()
=======
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
>>>>>>> af8620e168fd4c871db8db461cdaf0fe24f43d37

    pygame.quit()

if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> af8620e168fd4c871db8db461cdaf0fe24f43d37
