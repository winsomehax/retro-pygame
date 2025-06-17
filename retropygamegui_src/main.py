import pygame
import sys
import os

# This block allows the script to be run directly,
# ensuring that the retropygamegui_src package and its modules can be found.
if __name__ == "__main__":
    # Path to the directory containing this script (retropygamegui_src) # type: ignore
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Path to the project root (parent directory of retropygamegui_src)
    project_root = os.path.dirname(current_script_dir)
    # Add the project root to sys.path to allow absolute imports from retropygamegui_src
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # This ensures that 'from retropygamegui_src.module' works.

# Changed from relative to absolute imports based on project_root being in sys.path
from retropygamegui_src.config import app_config # Import app_config
from retropygamegui_src.data_manager import DataManager # type: ignore
from retropygamegui_src.models import Game # Import Game model for type hinting

from PIL import Image # For creating placeholder textures

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
DEFAULT_LINE_HEIGHT = 45 # For text
DEFAULT_FONT_SIZE = 20 # For text
FPS = 60

# --- Font Paths (assuming a 'fonts' directory in the project root) ---
# Ensure these assets exist in the specified paths
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORBITRON_FONT_PATH = os.path.join(PROJECT_ROOT_DIR, "fonts", "Orbitron-Regular.ttf")
ROBOTO_FONT_PATH = os.path.join(PROJECT_ROOT_DIR, "fonts", "Roboto-Regular.ttf")
ASSETS_ICONS_DIR = os.path.join(PROJECT_ROOT_DIR, "assets", "icons")

# --- Colors ---
DARK_SLATE_GRAY = (47, 79, 79)
DARK_SLATE_BLUE = (72, 61, 139)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CARD_BACKGROUND_COLOR = (40, 40, 50) # Darkish blue-grey for the card
CARD_HOVER_BACKGROUND_COLOR = (60, 60, 70) # Slightly lighter for hover
IMAGE_PADDING = 8 # Padding around the cover image inside the card
TEXT_COLOR = WHITE

# --- Font Sizes ---
PAGE_TITLE_FONT_SIZE = 48 # For "RetroGame Manager"
TITLE_FONT_SIZE = 20 # For game name in card, "Description" heading
PLATFORM_FONT_SIZE = 18
DESCRIPTION_FONT_SIZE = 14
LINE_SPACING = 4 # Extra spacing between lines of description text

def lerp(start, end, t):
    """Linear interpolation"""
    return start + t * (end - start)

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Wrap text to a given width."""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    return lines

class GameCard:
    """
    Represents a game card that stores game data, handles its own drawing,
    and animates onto the screen. The card has a 9:16 aspect ratio.
    """
    def __init__(self, 
                 game_data: Game, 
                 cover_image_surface: pygame.Surface,
                 data_manager: DataManager, # Added DataManager for platform lookup
                 start_x: float, start_y: float,
                 target_x: float, target_y: float,
                 card_target_width: float, card_target_height: float,
                 animation_delay: float, animation_duration: float = 0.7):
        self.game_data = game_data
        self.data_manager = data_manager
        self.original_cover_image = cover_image_surface # Store the original cover image
        # self.card_render_surface will be created in update_animation
        self.card_render_surface = pygame.Surface((1,1), pygame.SRCALPHA) 

        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y

        # Current animated properties of the card
        self.current_x = self.start_x
        self.current_y = self.start_y
        
        self.start_scale_factor = 0.1 # Start at 10% of target size
        self.current_card_width = card_target_width * self.start_scale_factor
        self.current_card_height = card_target_height * self.start_scale_factor

        self.card_target_width = card_target_width
        self.card_target_height = card_target_height
        
        self.current_alpha = 0.0  # Start transparent
        self.target_alpha = 255.0 # Fully opaque
        
        self.animation_delay = animation_delay
        self.animation_time_elapsed = 0.0
        self.animation_duration = animation_duration
        self.is_animating = True
        self.is_hovered = False # New attribute for hover state
        
        self.rect = self.card_render_surface.get_rect(center=(self.current_x, self.current_y))

        # Initialize fonts based on design document
        try:
            self.title_font = pygame.font.Font(ORBITRON_FONT_PATH, TITLE_FONT_SIZE)
            self.description_heading_font = pygame.font.Font(ORBITRON_FONT_PATH, TITLE_FONT_SIZE) # Orbitron for "Description"
            self.platform_font = pygame.font.Font(ROBOTO_FONT_PATH, PLATFORM_FONT_SIZE)
            self.description_font = pygame.font.Font(ROBOTO_FONT_PATH, DESCRIPTION_FONT_SIZE)
        except pygame.error as e:
            print(f"Warning: Font file not found ({e}). Falling back to default font.")
            # Fallback to default system font if custom fonts are not found
            self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
            self.description_heading_font = pygame.font.Font(None, TITLE_FONT_SIZE)
            self.platform_font = pygame.font.Font(None, PLATFORM_FONT_SIZE)
            self.description_font = pygame.font.Font(None, DESCRIPTION_FONT_SIZE)


        # Initial update to set up the card surface based on initial small size
        self._update_card_surface()

    def set_hover_state(self, hovered: bool):
        """Sets the hover state of the card and triggers a redraw if it changed."""
        if self.is_hovered != hovered:
            self.is_hovered = hovered
            # Re-render the card surface to reflect hover state change
            self._update_card_surface()

    def update_animation(self, delta_time: float):
        if not self.is_animating:
            return

        if self.animation_delay > 0:
            self.animation_delay -= delta_time
            if self.animation_delay > 0:
                return
            # If delay finished, use any overshoot from this frame for animation
            delta_time = abs(self.animation_delay) 
            self.animation_delay = 0.0
        
        self.animation_time_elapsed += delta_time
        progress = min(self.animation_time_elapsed / self.animation_duration, 1.0)

        self.current_x = lerp(self.start_x, self.target_x, progress)
        self.current_y = lerp(self.start_y, self.target_y, progress)
        
        current_scale_factor = lerp(self.start_scale_factor, 1.0, progress)
        
        self.current_card_width = self.card_target_width * current_scale_factor
        self.current_card_height = self.card_target_height * current_scale_factor
        
        self.current_alpha = lerp(0, self.target_alpha, progress)

        if progress >= 1.0:
            self.is_animating = False
            # Snap to final values
            self.current_x = self.target_x
            self.current_y = self.target_y
            self.current_card_width = self.card_target_width
            self.current_card_height = self.card_target_height
            self.current_alpha = self.target_alpha

        self._update_card_surface()

    def _update_card_surface(self):
        # Ensure card dimensions are at least 1x1
        draw_card_width = max(1, int(self.current_card_width))
        draw_card_height = max(1, int(self.current_card_height))

        self.card_render_surface = pygame.Surface((draw_card_width, draw_card_height), pygame.SRCALPHA)
        bg_color_to_use = CARD_HOVER_BACKGROUND_COLOR if self.is_hovered else CARD_BACKGROUND_COLOR
        self.card_render_surface.fill(bg_color_to_use + (int(self.current_alpha),)) # Apply alpha to fill

        # --- Define areas ---
        # Adjust height ratios: ~55% for image, 45% for text (title, platform, desc)
        image_area_height_ratio = 0.55
        text_area_height_ratio = 1.0 - image_area_height_ratio

        cover_image_display_area_y_start = IMAGE_PADDING
        cover_image_display_area_height = draw_card_height * image_area_height_ratio - IMAGE_PADDING
        
        text_area_y_start = cover_image_display_area_y_start + cover_image_display_area_height + IMAGE_PADDING
        text_area_width = draw_card_width - 2 * IMAGE_PADDING

        # --- Scale and blit the cover image onto the card ---
        if self.original_cover_image:
            img_area_w = draw_card_width - 2 * IMAGE_PADDING
            # Use the allocated height for the image area
            img_area_h = cover_image_display_area_height - IMAGE_PADDING 

            if img_area_w > 0 and img_area_h > 0 :
                orig_cover_w, orig_cover_h = self.original_cover_image.get_size()
                
                if orig_cover_w > 0 and orig_cover_h > 0:
                    scale_w = img_area_w / orig_cover_w
                    scale_h = img_area_h / orig_cover_h
                    scale = min(scale_w, scale_h)
                    
                    scaled_cover_w = int(orig_cover_w * scale)
                    scaled_cover_h = int(orig_cover_h * scale)

                    if scaled_cover_w > 0 and scaled_cover_h > 0:
                        scaled_cover_img = pygame.transform.smoothscale(
                            self.original_cover_image, (scaled_cover_w, scaled_cover_h)
                        )
                        # Position to blit scaled cover image (centered in its allocated area)
                        cover_x = IMAGE_PADDING + (img_area_w - scaled_cover_w) / 2
                        cover_y = cover_image_display_area_y_start + (img_area_h - scaled_cover_h) / 2
                        self.card_render_surface.blit(scaled_cover_img, (cover_x, cover_y))
        
        # --- Render Game Title ---
        current_text_y = text_area_y_start
        if self.game_data.title and text_area_width > 0:
            wrapped_title_lines = wrap_text(self.game_data.title, self.title_font, text_area_width)
            for i, line in enumerate(wrapped_title_lines):
                # For titles, let's only show a max of 2 lines to keep it concise on the card
                if i >= 2 and len(wrapped_title_lines) > 2: 
                    line = line[:text_area_width//self.title_font.size("a")[0] - 3] + "..." # Add ellipsis
                title_line_surface = self.title_font.render(line, True, TEXT_COLOR)
                # Left-align text
                title_line_rect = title_line_surface.get_rect(topleft=(IMAGE_PADDING, current_text_y))
                self.card_render_surface.blit(title_line_surface, title_line_rect)
                current_text_y += self.title_font.get_height() # No extra line spacing for title lines
                if i >= 1 and len(wrapped_title_lines) > 2: break # Stop after 2 lines if more

        # --- Render Platform Name ---
        current_text_y += LINE_SPACING // 2 # Smaller spacing after title block
        platform_name = "Unknown Platform"
        if self.game_data.platform in self.data_manager.platforms:
            platform_name = self.data_manager.platforms[self.game_data.platform].name
        
        platform_text_surface = self.platform_font.render(platform_name, True, TEXT_COLOR)
        # Left-align text
        platform_text_rect = platform_text_surface.get_rect(topleft=(IMAGE_PADDING, current_text_y))
        self.card_render_surface.blit(platform_text_surface, platform_text_rect)
        current_text_y = platform_text_rect.bottom + LINE_SPACING

        # --- Render "Description" Heading ---
        if self.game_data.description and text_area_width > 0: # Only show heading if there's a description
            desc_heading_text = "Description"
            desc_heading_surface = self.description_heading_font.render(desc_heading_text, True, TEXT_COLOR)
            # Left-align text
            desc_heading_rect = desc_heading_surface.get_rect(topleft=(IMAGE_PADDING, current_text_y))
            self.card_render_surface.blit(desc_heading_surface, desc_heading_rect)
            current_text_y += self.description_heading_font.get_height()
            current_text_y += LINE_SPACING // 2 # Small spacing before actual description lines

        # --- Render Game Description ---
        if self.game_data.description and text_area_width > 0:
            wrapped_description_lines = wrap_text(self.game_data.description, self.description_font, text_area_width)
            for i, line in enumerate(wrapped_description_lines):
                if i >= 3: # Limit to 3 lines as per design.md
                    # Add ellipsis to the last visible line if there's more text
                    if len(wrapped_description_lines) > 3 and line:
                         # Estimate chars that fit, subtract for "..."
                        max_chars = text_area_width // (self.description_font.size("a")[0] if self.description_font.size("a")[0] > 0 else 1)
                        line = line[:max_chars - 3] + "..."
                    elif not line and i == 2 and len(wrapped_description_lines) > 3: # If 3rd line is empty but there's more
                        line = "..." # Show ellipsis if 3rd line would be empty but there's more
                if i >= 3: break

                if current_text_y + self.description_font.get_height() > draw_card_height - IMAGE_PADDING: # Stop if out of card bounds
                    break
                desc_line_surface = self.description_font.render(line, True, TEXT_COLOR)
                # Left-align text
                desc_line_rect = desc_line_surface.get_rect(topleft=(IMAGE_PADDING, current_text_y))
                self.card_render_surface.blit(desc_line_surface, desc_line_rect)
                current_text_y += self.description_font.get_height() + LINE_SPACING

        self.rect = self.card_render_surface.get_rect(center=(self.current_x, self.current_y))


    def draw(self, screen: pygame.Surface):
        screen.blit(self.card_render_surface, self.rect)

class Grid:
    """
    Manages a collection of GameCards, arranges them, and handles scrolling.
    """
    def __init__(self, x: float, y: float, width: float, height: float,
                 data_manager: DataManager,
                 cols: int,
                 card_target_width: float, card_target_height: float,
                 margin_horizontal: float, margin_vertical: float,
                 card_animation_start_x: float, card_animation_start_y: float,
                 card_animation_stagger_delay: float,
                 scroll_speed: int = 50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data_manager = data_manager
        self.cols = cols
        self.card_target_width = card_target_width
        self.card_target_height = card_target_height
        self.margin_horizontal = margin_horizontal
        self.margin_vertical = margin_vertical
        self.card_animation_start_x = card_animation_start_x
        self.card_animation_start_y = card_animation_start_y
        self.card_animation_stagger_delay = card_animation_stagger_delay
        self.scroll_speed = scroll_speed

        self.cards: list[GameCard] = []
        self.scroll_offset_y = 0.0
        self.total_content_height = 0.0

        # Surface for rendering the grid's content, enabling clipping and scrolling
        self.content_surface = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)

    def _update_content_height(self):
        if not self.cards:
            self.total_content_height = 0
            return
        
        num_rows = (len(self.cards) + self.cols - 1) // self.cols
        self.total_content_height = num_rows * self.card_target_height + \
                                    max(0, num_rows - 1) * self.margin_vertical
        
        # Ensure scroll_offset_y is within valid bounds
        max_scroll = max(0, self.total_content_height - self.height)
        self.scroll_offset_y = max(0, min(self.scroll_offset_y, max_scroll))

    def add_game_card(self, game_obj: Game, cover_image_surface: pygame.Surface, card_index: int):
        row = card_index // self.cols
        col = card_index % self.cols

        # Calculate target X and Y for the card's center, relative to the screen.
        # This is where the card animates to.
        # card_content_x_in_grid_layout is the x-offset of the card's top-left within the grid's full content area
        card_content_x_in_grid_layout = col * (self.card_target_width + self.margin_horizontal)
        card_content_y_in_grid_layout = row * (self.card_target_height + self.margin_vertical)

        # Absolute screen target position for the card's center
        target_x_abs = self.x + card_content_x_in_grid_layout + self.card_target_width / 2
        target_y_abs = self.y + card_content_y_in_grid_layout + self.card_target_height / 2

        card = GameCard(
            game_data=game_obj,
            cover_image_surface=cover_image_surface,
            data_manager=self.data_manager,
            start_x=self.card_animation_start_x,
            start_y=self.card_animation_start_y,
            target_x=target_x_abs,
            target_y=target_y_abs,
            card_target_width=self.card_target_width,
            card_target_height=self.card_target_height,
            animation_delay=card_index * self.card_animation_stagger_delay
        )
        self.cards.append(card)

    def populate_from_data(self, games_data: dict[str, Game]):
        self.cards = [] # Clear existing cards
        supported_icon_extensions = ["jpg", "jpeg", "png", "webp"]
        game_idx = 0

        for game_slug, game_obj in games_data.items():
            cover_image_surface = None
            image_source_info = "placeholder" # For logging

            # 1. Try to load from local assets/icons/
            local_icon_path_found = None
            for ext in supported_icon_extensions:
                potential_path = os.path.join(ASSETS_ICONS_DIR, f"{game_slug}.{ext}")
                if os.path.exists(potential_path):
                    local_icon_path_found = potential_path
                    break
            
            if local_icon_path_found:
                try:
                    cover_image_surface = pygame.image.load(local_icon_path_found).convert_alpha()
                    image_source_info = f"local asset ({local_icon_path_found})"
                except pygame.error as e:
                    print(f"Grid: Pygame error loading local asset {local_icon_path_found} for {game_obj.title}: {e}. Falling back.")
                except Exception as e: # pylint: disable=broad-except
                    print(f"Grid: General error loading local asset {local_icon_path_found} for {game_obj.title}: {e}. Falling back.")

            # 2. If no local asset, try game_obj.cover_image_path (if it's a local file)
            if cover_image_surface is None and game_obj.cover_image_path and os.path.exists(game_obj.cover_image_path):
                try:
                    cover_image_surface = pygame.image.load(game_obj.cover_image_path).convert_alpha()
                    image_source_info = f"game_obj.cover_image_path ({game_obj.cover_image_path})"
                except pygame.error as e:
                    print(f"Grid: Pygame error loading from {game_obj.cover_image_path} for {game_obj.title}: {e}. Falling back.")
                except Exception as e: # pylint: disable=broad-except
                    print(f"Grid: General error loading from {game_obj.cover_image_path} for {game_obj.title}: {e}. Falling back.")
            
            # 3. If still no image, use placeholder
            if cover_image_surface is None:
                PLACEHOLDER_COVER_WIDTH = 120 
                PLACEHOLDER_COVER_HEIGHT = 160
                pil_img = Image.new('RGBA', (PLACEHOLDER_COVER_WIDTH, PLACEHOLDER_COVER_HEIGHT), DARK_SLATE_BLUE)
                image_bytes = pil_img.tobytes()
                cover_image_surface = pygame.image.fromstring(image_bytes, pil_img.size, 'RGBA').convert_alpha()
                image_source_info = "placeholder" # Already default, but explicit

            # print(f"Grid: Using {image_source_info} for {game_obj.title}") # Optional: for debugging image source
            self.add_game_card(game_obj, cover_image_surface, game_idx)
            game_idx += 1
        self._update_content_height()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            if self.total_content_height > self.height:
                self.scroll_offset_y -= event.y * self.scroll_speed
                max_scroll = max(0, self.total_content_height - self.height)
                self.scroll_offset_y = max(0, min(self.scroll_offset_y, max_scroll))
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            # Check hover state for each card
            for card in self.cards:
                # card.rect is in absolute screen coordinates
                is_mouse_over_card = card.rect.collidepoint(mouse_pos)
                card.set_hover_state(is_mouse_over_card)

    def update(self, delta_time: float):
        for card in self.cards:
            card.update_animation(delta_time)
        # Potentially update content height if cards can be added/removed dynamically later
        # self._update_content_height() 

    def draw(self, screen: pygame.Surface):
        self.content_surface.fill((0,0,0,0)) # Clear with transparency for each frame

        for card in self.cards:
            # card.rect is centered at (card.current_x, card.current_y) which are absolute screen coords
            # Calculate draw position on the content_surface (relative to grid's top-left, scrolled)
            draw_x_on_content = card.rect.left - self.x
            draw_y_on_content = card.rect.top - self.y - self.scroll_offset_y
            
            card_blit_rect = card.card_render_surface.get_rect(topleft=(draw_x_on_content, draw_y_on_content))

            # Only blit if the card is visible within the content_surface's bounds
            if self.content_surface.get_rect().colliderect(card_blit_rect):
                self.content_surface.blit(card.card_render_surface, card_blit_rect)

        screen.blit(self.content_surface, (self.x, self.y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RetroNode Game Manager")
    clock = pygame.time.Clock()

    data_manager = DataManager()
    if app_config: # Ensure app_config is loaded
        print("API Keys Loaded:", app_config.get_api_keys())
    else:
        print("Warning: app_config not loaded. API keys might be unavailable.")
    print(f"Loaded {len(data_manager.games)} games.")
    print(f"Loaded {len(data_manager.platforms)} platforms.")
    print(f"Loaded {len(data_manager.emulators)} emulators.")

    # --- Page Title Setup ---
    page_title_text = "RetroGame Manager"
    try:
        page_title_font = pygame.font.Font(ORBITRON_FONT_PATH, PAGE_TITLE_FONT_SIZE)
    except pygame.error as e:
        print(f"Warning: Orbitron font not found for page title ({e}). Falling back to default font.")
        page_title_font = pygame.font.Font(None, PAGE_TITLE_FONT_SIZE)
    
    page_title_surface = page_title_font.render(page_title_text, True, WHITE)
    page_title_rect = page_title_surface.get_rect(center=(SCREEN_WIDTH / 2, 40)) # Position at top-center


    # --- Grid and Card Configuration ---
    # Adjust columns to change card size. Current: 2 (large cards). For approx half size, use 4.
    GRID_COLS = 4
    CARD_ASPECT_RATIO = 9 / 16
    
    # Define the grid's viewport on the screen
    GRID_MARGIN_X = 50
    GRID_MARGIN_Y = page_title_rect.bottom + 30 # Adjust grid Y to be below the page title
    GRID_VIEWPORT_X = GRID_MARGIN_X
    GRID_VIEWPORT_Y = GRID_MARGIN_Y
    GRID_VIEWPORT_WIDTH = SCREEN_WIDTH - (2 * GRID_MARGIN_X)
    GRID_VIEWPORT_HEIGHT = SCREEN_HEIGHT - (2 * GRID_MARGIN_Y)

    # Calculate card dimensions based on grid width and number of columns
    CARD_MARGIN_HORIZONTAL = 15 # Adjusted margin for smaller cards
    CARD_MARGIN_VERTICAL = 20   # Adjusted margin for smaller cards
    
    # Total horizontal space for cards = viewport width - (cols + 1) * margin (for margins around and between)
    # Let's use margin between cards, and grid viewport handles outer padding.
    # Total width for cards themselves: GRID_VIEWPORT_WIDTH - (GRID_COLS - 1) * CARD_MARGIN_HORIZONTAL
    # Width per card: (GRID_VIEWPORT_WIDTH - (GRID_COLS - 1) * CARD_MARGIN_HORIZONTAL) / GRID_COLS
    # This calculation ensures cards + margins fit within the viewport width.
    available_width_for_cards_and_inner_margins = GRID_VIEWPORT_WIDTH
    card_target_width = (available_width_for_cards_and_inner_margins - (GRID_COLS -1) * CARD_MARGIN_HORIZONTAL) / GRID_COLS
    card_target_height = card_target_width / CARD_ASPECT_RATIO

    # Card animation properties
    card_animation_start_x = SCREEN_WIDTH / 2
    card_animation_start_y = SCREEN_HEIGHT + 50 # Start from below the screen
    card_animation_stagger_delay = 0.03

    game_grid = Grid(
        x=GRID_VIEWPORT_X,
        y=GRID_VIEWPORT_Y,
        width=GRID_VIEWPORT_WIDTH,
        height=GRID_VIEWPORT_HEIGHT,
        data_manager=data_manager,
        cols=GRID_COLS,
        card_target_width=card_target_width,
        card_target_height=card_target_height,
        margin_horizontal=CARD_MARGIN_HORIZONTAL,
        margin_vertical=CARD_MARGIN_VERTICAL,
        card_animation_start_x=card_animation_start_x,
        card_animation_start_y=card_animation_start_y,
        card_animation_stagger_delay=card_animation_stagger_delay
    )

    game_grid.populate_from_data(data_manager.games)

    running = True
    while running:
        delta_time_ms = clock.tick(FPS)
        delta_time_s = delta_time_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            game_grid.handle_event(event) # Pass events to the grid

        game_grid.update(delta_time_s) # Update grid (which updates cards)

        screen.fill(BLACK)
        screen.blit(page_title_surface, page_title_rect) # Draw the page title
        game_grid.draw(screen) # Draw the grid (which draws visible cards)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()