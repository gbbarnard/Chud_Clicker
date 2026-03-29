import os
import random
import pygame
import settings
from menus import MenuManager


class MusicManager:
    def __init__(self):
        self.enabled = getattr(settings, "MUSIC_ENABLED", True)
        self.volume = getattr(settings, "MUSIC_VOLUME", 0.35)
        self.clip_seconds = getattr(settings, "MUSIC_CLIP_SECONDS", 30)

        self.music_files = []
        self.current_track = None
        self.current_track_length = 0.0
        self.clip_end_time = 0
        self.started_ok = False

        if not self.enabled:
            return

        self._load_music_list()
        self._setup_mixer()

    def _load_music_list(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

        possible_tracks = [
            "Froggy Fresh - Dunked On.mp3",
            'NA - 009 Sound System "With A Spirit" OFFICIAL HD.mp3',
            "NA - Nyan Cat! [Official].mp3",
            "Trance - 009 Sound System Dreamscape (HD) (1).mp3",
        ]

        for filename in possible_tracks:
            full_path = os.path.join(assets_dir, filename)
            if os.path.exists(full_path):
                self.music_files.append(full_path)

    def _setup_mixer(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
            self.started_ok = True
        except pygame.error as e:
            print(f"Music mixer failed to initialize: {e}")
            self.started_ok = False

    def _get_track_length(self, filepath):
        try:
            sound = pygame.mixer.Sound(filepath)
            return float(sound.get_length())
        except pygame.error as e:
            print(f"Could not read track length for {filepath}: {e}")
            return 0.0

    def play_random_clip(self):
        if not self.enabled or not self.started_ok or not self.music_files:
            return

        self.current_track = random.choice(self.music_files)
        self.current_track_length = self._get_track_length(self.current_track)

        start_pos = 0.0
        if self.current_track_length > self.clip_seconds:
            max_start = max(0.0, self.current_track_length - self.clip_seconds)
            start_pos = random.uniform(0.0, max_start)

        try:
            pygame.mixer.music.load(self.current_track)
            pygame.mixer.music.play(start=start_pos)
            self.clip_end_time = pygame.time.get_ticks() + int(self.clip_seconds * 1000)
        except pygame.error as e:
            print(f"Could not play music clip from {self.current_track}: {e}")

    def update(self):
        if not self.enabled or not self.started_ok or not self.music_files:
            return

        now = pygame.time.get_ticks()

        if not pygame.mixer.music.get_busy():
            self.play_random_clip()
            return

        if now >= self.clip_end_time:
            pygame.mixer.music.stop()

    def set_muted(self, muted: bool):
        if not self.started_ok:
            return
        pygame.mixer.music.set_volume(0.0 if muted else self.volume)

    def cleanup(self):
        if self.started_ok:
            pygame.mixer.music.stop()


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        pygame.RESIZABLE,
    )
    pygame.display.set_caption("CHUD Collector 2026")
    clock = pygame.time.Clock()

    menu_manager = MenuManager()
    music_manager = MusicManager()

    if music_manager.started_ok:
        music_manager.play_random_clip()

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
        music_manager.update()
        music_manager.set_muted(menu_manager.game.music_muted)

        screen.fill(settings.GRAY)
        menu_manager.draw(screen)
        pygame.display.flip()

    music_manager.cleanup()
    pygame.quit()


if __name__ == "__main__":
    main()