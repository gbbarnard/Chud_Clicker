import os
import pygame
import settings #

class AssetManager:
    def __init__(self):
        # Determine the base directory (my_game/)
        # Since this file is in src/, we go up one level
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, "assets")
        
        # Caches to prevent reloading files
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def get_path(self, *path_parts):
        """Generates a cross-platform path within the assets folder."""
        return os.path.join(self.assets_dir, *path_parts)

    def load_image(self, name, folder="images", alpha=True, scale=None):
        """Loads and caches images with optional scaling."""
        if name in self.images:
            return self.images[name]

        path = self.get_path(folder, name)
        try:
            image = pygame.image.load(path)
            # Convert for performance
            image = image.convert_alpha() if alpha else image.convert()
            
            if scale:
                image = pygame.transform.smoothscale(image, scale)
            
            self.images[name] = image
            return image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            return None

    def load_sound(self, name, folder="sounds"):
        """Loads and caches sound effects."""
        if name in self.sounds:
            return self.sounds[name]

        path = self.get_path(folder, name)
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"Error loading sound {path}: {e}")
            return None

    def play_music(self, name, folder="sounds", loops=-1, volume=0.5):
        """Handles background music streaming (not cached to save RAM)."""
        path = self.get_path(folder, name)
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"Error playing music {path}: {e}")