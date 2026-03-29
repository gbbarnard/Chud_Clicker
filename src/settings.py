import pygame

# Screen Configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
 
# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 121, 211)  # Reddit-ish Blue
LIGHT_BLUE = (148, 197, 255)
DARK_GRAY = (80, 80, 80)
PANEL_BORDER = (110, 110, 110)
# 180 is roughly 70% opacity
LEFT_PANEL_BG = (206, 167, 167, 180)
RIGHT_PANEL_BG = (220, 220, 220, 180)
CENTER_PANEL_BG = (0, 0, 0, 0)#(214, 214, 214, 180)
# Make cards slightly more solid so text remains readable
CARD_BG = (238, 238, 238, 220)
BUTTON_DISABLED = (145, 164, 184)
BUTTON_BG = BLUE
UPGRADE_OWNED = (60, 160, 90)

# Add this for your background filename
BACKGROUND_IMAGE = "background.webp" # or .png/.jpg

# Added from second file
UPGRADE_LOCKED_BG = (228, 190, 190)
UPGRADE_LOCKED_TEXT = (120, 45, 45)
UPGRADE_LOCKED_BUTTON = (176, 110, 110)

# UI Settings
POST_BUTTON_WIDTH = 200
POST_BUTTON_HEIGHT = 50
FONT_SIZE = 36

# Screen Division Logic
THIRD_WIDTH = SCREEN_WIDTH // 3

# Column X-coordinates maY NOT NEED
# LEFT_COLUMN_X = 0
# CENTER_COLUMN_X = THIRD_WIDTH
# RIGHT_COLUMN_X = THIRD_WIDTH * 2

# --- Flexible Column Widths ---
# Define exactly how wide you want the side columns to be
LEFT_COL_WIDTH = 300   # e.g., for Stats/Inventory
RIGHT_COL_WIDTH = 400  # e.g., for a Shop or Log

# The Center column takes whatever is left
CENTER_COL_WIDTH = SCREEN_WIDTH - (LEFT_COL_WIDTH + RIGHT_COL_WIDTH)

# --- Column X-coordinates (Starting points) ---
LEFT_COLUMN_X = 0
CENTER_COLUMN_X = LEFT_COL_WIDTH
RIGHT_COLUMN_X = LEFT_COL_WIDTH + CENTER_COL_WIDTH

MUSIC_BUTTON_BG = (245, 245, 245)

MUSIC_BUTTON_MUTED_BG = (200, 160, 160)

MUSIC_BUTTON_BORDER = (110, 110, 110)

MUSIC_ENABLED = True

MUSIC_VOLUME = 0.35

MUSIC_CLIP_SECONDS = 30

# --- Dynamic Column Logic ---
# We use a function so we can call it whenever the window size changes
def get_column_layout(current_width):
    # You can keep these fixed, or make them percentages
    left_w = 300
    right_w = 400
    center_w = current_width - (left_w + right_w)

    # Return a dictionary of coordinates and widths
    return {
        "left_x": 0,
        "left_w": left_w,
        "center_x": left_w,
        "center_w": center_w,
        "right_x": left_w + center_w,
        "right_w": right_w
    }
# Music Button Colors
MUSIC_BUTTON_BG = (245, 245, 245)
MUSIC_BUTTON_MUTED_BG = (200, 160, 160)
MUSIC_BUTTON_BORDER = (110, 110, 110)

# Music Engine Settings
MUSIC_ENABLED = True
MUSIC_VOLUME = 0.50
MUSIC_CLIP_SECONDS = 30