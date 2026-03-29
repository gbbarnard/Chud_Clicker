import pygame
import settings
from menus import MenuManager


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        pygame.RESIZABLE,
    )
    pygame.display.set_caption("CHUD Collector 2026")
    clock = pygame.time.Clock()

    menu_manager = MenuManager()

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                menu_manager.update_layout(event.w, event.h)

            menu_manager.handle_event(event)

        menu_manager.update(dt)

        screen.fill(settings.GRAY)
        menu_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()