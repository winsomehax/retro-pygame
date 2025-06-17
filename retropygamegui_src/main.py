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

from retropygamegui_src.config import app_config
from retropygamegui_src.data_manager import DataManager
from retropygamegui_src.models import Game, Platform, Emulator
from retropygamegui_src.plugins import get_plugin_instance

from PIL import Image

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
DEFAULT_LINE_HEIGHT = 45
DEFAULT_FONT_SIZE = 20
FPS = 60

PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORBITRON_FONT_PATH = os.path.join(PROJECT_ROOT_DIR, "fonts", "Orbitron-Regular.ttf")
ROBOTO_FONT_PATH = os.path.join(PROJECT_ROOT_DIR, "fonts", "Roboto-Regular.ttf")
ASSETS_ICONS_DIR = os.path.join(PROJECT_ROOT_DIR, "assets", "icons")

DARK_SLATE_GRAY = (47, 79, 79)
DARK_SLATE_BLUE = (72, 61, 139)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CARD_BACKGROUND_COLOR = (40, 40, 50)
CARD_HOVER_BACKGROUND_COLOR = (60, 60, 70)
IMAGE_PADDING = 8
TEXT_COLOR = WHITE

PAGE_TITLE_FONT_SIZE = 48
TITLE_FONT_SIZE = 20
PLATFORM_FONT_SIZE = 18
DESCRIPTION_FONT_SIZE = 14
LINE_SPACING = 4

# --- UI Font Definitions ---
UI_MODAL_TITLE_FONT_SIZE = 32
UI_LABEL_FONT_SIZE = 20
UI_INPUT_FONT_SIZE = 20
UI_BUTTON_FONT_SIZE = 20
UI_ERROR_FONT_SIZE = 18

active_modal = None
current_search_plugin = None
active_plugins_list = []


def lerp(start, end, t):
    return start + t * (end - start)

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
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

class TextInput:
    def __init__(self, x, y, width, height, font, initial_text="", text_color=WHITE, active_color=pygame.Color('lightskyblue3'), inactive_color=pygame.Color('gray30'), max_length=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = initial_text
        self.text_color = text_color
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.active = False
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.cursor_visible = False
        self.cursor_timer = 0
        self.max_length = max_length

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.cursor_visible = True
                self.cursor_timer = 0
            else:
                self.active = False
            self.color = self.active_color if self.active else self.inactive_color
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            elif self.max_length == 0 or len(self.text) < self.max_length:
                self.text += event.unicode
            self.text_surface = self.font.render(self.text, True, self.text_color)
            self.cursor_visible = True
            self.cursor_timer = 0
        return self.active

    def update(self, delta_time):
        if self.active:
            self.cursor_timer += delta_time
            if self.cursor_timer >= 0.5:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + (self.rect.height - self.text_surface.get_height()) // 2))
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + self.text_surface.get_width()
            cursor_y_start = self.rect.y + 5
            cursor_y_end = self.rect.y + self.rect.height - 5
            pygame.draw.line(screen, self.text_color, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 1)

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.text_color)

class Button:
    def __init__(self, x, y, width, height, text, font, text_color=WHITE, bg_color=pygame.Color('dodgerblue'), hover_bg_color=pygame.Color('lightskyblue'), callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_bg_color = hover_bg_color
        self.current_bg_color = self.bg_color
        self.callback = callback
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_bg_color = self.hover_bg_color if self.is_hovered else self.bg_color
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.callback:
                self.callback()
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_bg_color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

class FormModal:
    def __init__(self, screen_width, screen_height, title, fields_config, data_manager,
                 save_callback, cancel_callback, platform_id_for_emulator=None, current_data=None, search_button_config=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_text = title
        self.fields_config = fields_config
        self.data_manager = data_manager
        self.save_callback = save_callback
        self.cancel_callback = cancel_callback
        self.platform_id_for_emulator = platform_id_for_emulator
        self.current_data = current_data
        self.search_button_config = search_button_config

        self.modal_width = int(screen_width * 0.8)
        self.modal_height = int(screen_height * 0.8)
        self.modal_x = (screen_width - self.modal_width) // 2
        self.modal_y = (screen_height - self.modal_height) // 2
        self.modal_rect = pygame.Rect(self.modal_x, self.modal_y, self.modal_width, self.modal_height)

        self.overlay_color = (0, 0, 0, 180)

        self.title_font = None
        self.label_font = None
        self.input_font = None
        self.button_font = None
        self.search_button_font = None
        self.error_font = None
        self.search_result_font = None

        self.fields = {}
        self.field_labels = {}
        self.active_field_index = 0
        self.error_message = None
        self.error_message_surface = None

        self.search_results = []
        self.search_results_area_rect = None
        self.search_result_item_height = 28
        self.selected_search_result_index = -1
        self.search_active = False
        self.search_scroll_offset_y = 0
        self.total_search_results_height = 0
        self.use_selected_result_button = None
        self.search_online_button = None

        self._setup_layout_and_fonts()
        self._setup_fields()
        self._setup_buttons()

        if self.current_data:
            self._populate_fields_with_current_data()

    def _setup_layout_and_fonts(self):
        try:
            self.title_font = pygame.font.Font(ORBITRON_FONT_PATH, UI_MODAL_TITLE_FONT_SIZE)
            self.label_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_LABEL_FONT_SIZE)
            self.input_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_INPUT_FONT_SIZE)
            self.button_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_BUTTON_FONT_SIZE)
            self.search_button_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_BUTTON_FONT_SIZE -2)
            self.error_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_ERROR_FONT_SIZE)
            self.search_result_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_INPUT_FONT_SIZE - 3)
        except pygame.error as e:
            print(f"FormModal: Font loading error - {e}. Using default fonts.")
            default_font_size = 20
            self.title_font = pygame.font.Font(None, 30)
            self.label_font = pygame.font.Font(None, default_font_size)
            self.input_font = pygame.font.Font(None, default_font_size)
            self.button_font = pygame.font.Font(None, default_font_size)
            self.search_button_font = pygame.font.Font(None, default_font_size -2)
            self.error_font = pygame.font.Font(None, 18)
            self.search_result_font = pygame.font.Font(None, default_font_size - 3)

        self.form_area_width = int(self.modal_width * 0.50)
        self.search_area_width = self.modal_width - self.form_area_width - 15

        self.form_area_rect = pygame.Rect(self.modal_x + 5, self.modal_y, self.form_area_width -10, self.modal_height)
        self.search_results_area_rect = pygame.Rect(
            self.modal_x + self.form_area_width + 10,
            self.modal_y + 50,
            self.search_area_width - 5,
            self.modal_height - 100
        )

        use_button_height = 35
        self.use_selected_result_button = Button(
            x=self.search_results_area_rect.left,
            y=self.search_results_area_rect.bottom + 5,
            width=self.search_results_area_rect.width,
            height=use_button_height,
            text="Use Selected Result",
            font=self.button_font,
            callback=self._use_selected_search_result
        )

    def _setup_fields(self):
        input_field_height = 35
        label_input_spacing = 5
        field_vertical_spacing = 15
        current_y = self.form_area_rect.top + 60

        for i, config in enumerate(self.fields_config):
            field_name = config['name']
            label_text = config['label']

            label_surface = self.label_font.render(label_text, True, WHITE)
            label_x = self.form_area_rect.left + 20
            label_y = current_y
            self.field_labels[field_name] = (label_surface, (label_x, label_y))

            input_y = label_y + label_surface.get_height() + label_input_spacing
            input_width = self.form_area_width - 40

            initial_value = ""
            text_input = TextInput(
                x=self.form_area_rect.left + 20, y=input_y,
                width=input_width, height=input_field_height,
                font=self.input_font, initial_text=initial_value
            )
            if i == 0:
                text_input.active = True
                text_input.color = text_input.active_color
            self.fields[field_name] = text_input

            current_y = input_y + input_field_height + field_vertical_spacing

        if self.fields_config:
            first_field_name = self.fields_config[0]['name']
            if first_field_name in self.fields:
                 self.fields[first_field_name].active = True
                 self.fields[first_field_name].color = self.fields[first_field_name].active_color
                 self.active_field_index = 0

    def _populate_fields_with_current_data(self):
        if not self.current_data: return
        for config in self.fields_config:
            field_name = config['name']
            if field_name in self.fields and hasattr(self.current_data, field_name):
                value = getattr(self.current_data, field_name)
                self.fields[field_name].set_text(str(value) if value is not None else "")

    def _setup_buttons(self):
        button_width = 100
        button_height = 35
        button_spacing = 10
        button_y = self.form_area_rect.bottom - button_height - 20

        cancel_button_x = self.form_area_rect.left + self.form_area_width - button_width - 20
        self.cancel_button = Button(
            cancel_button_x, button_y, button_width, button_height, "Cancel", self.button_font,
            callback=self.cancel_callback
        )

        save_button_x = cancel_button_x - button_width - button_spacing
        self.save_button = Button(
            save_button_x, button_y, button_width, button_height, "Save", self.button_font,
            callback=self._save
        )

        if self.search_button_config and callable(self.search_button_config.get('callback')):
            search_button_text = self.search_button_config.get('text', "Search")
            search_button_x = save_button_x - button_width - button_spacing
            self.search_online_button = Button(
                search_button_x, button_y, button_width, button_height, search_button_text,
                self.search_button_font if self.search_button_font else self.button_font,
                callback=self.search_button_config['callback']
            )
        else:
            self.search_online_button = None

    def get_form_data(self) -> dict:
        data = {}
        for field_name, text_input_obj in self.fields.items():
            data[field_name] = text_input_obj.get_text()
        return data

    def set_search_results(self, results: list[dict]):
        self.search_results = results if results else []
        self.search_active = True
        self.selected_search_result_index = -1
        self.search_scroll_offset_y = 0
        self.total_search_results_height = len(self.search_results) * self.search_result_item_height
        if not self.search_results:
             self.search_results = [{'name': "No results found.", 'source_platform_id': '__NO_RESULTS__'}]

    def _use_selected_search_result(self):
        if self.selected_search_result_index != -1 and self.selected_search_result_index < len(self.search_results):
            selected_data = self.search_results[self.selected_search_result_index]

            field_mapping = {
                'platform_id': selected_data.get('source_platform_id'),
                'name': selected_data.get('name'),
                'manufacturer': selected_data.get('manufacturer'),
                'release_year': str(selected_data.get('release_year', '')) if selected_data.get('release_year') is not None else '',
                'description': selected_data.get('description')
            }

            for field_key, value_to_set in field_mapping.items():
                if field_key in self.fields and value_to_set is not None:
                    self.fields[field_key].set_text(str(value_to_set))

            self.search_active = False
            self.search_results = []
            self.selected_search_result_index = -1
        else:
            print("FormModal: No search result selected to use.")

    def _set_active_field(self, new_index):
        if not self.fields_config: return

        current_field_name = self.fields_config[self.active_field_index]['name']
        if current_field_name in self.fields:
            self.fields[current_field_name].active = False
            self.fields[current_field_name].color = self.fields[current_field_name].inactive_color

        self.active_field_index = new_index % len(self.fields_config)

        new_field_name = self.fields_config[self.active_field_index]['name']
        if new_field_name in self.fields:
            self.fields[new_field_name].active = True
            self.fields[new_field_name].color = self.fields[new_field_name].active_color
            self.fields[new_field_name].cursor_visible = True
            self.fields[new_field_name].cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.cancel_callback()
                return True
            if event.key == pygame.K_TAB:
                if self.fields_config:
                    self._set_active_field(self.active_field_index + (1 if not event.mod & pygame.KMOD_SHIFT else -1))
                return True
            if event.key == pygame.K_RETURN:
                if self.search_active and self.use_selected_result_button and self.use_selected_result_button.is_hovered :
                     self._use_selected_search_result()
                elif self.fields_config and len(self.fields_config) > 0 and \
                     self.fields_config[self.active_field_index]['name'] in self.fields and \
                     self.fields[self.fields_config[self.active_field_index]['name']].active :
                    self._save()
                else:
                    self._save()
                return True

        mouse_pos = event.pos
        if self.search_active and event.type == pygame.MOUSEBUTTONDOWN:
            if self.use_selected_result_button and self.use_selected_result_button.rect.collidepoint(mouse_pos):
                if self.use_selected_result_button.handle_event(event):
                    return True

            if self.search_results_area_rect.collidepoint(mouse_pos):
                relative_mouse_y = mouse_pos[1] - self.search_results_area_rect.top + self.search_scroll_offset_y
                clicked_item_index = relative_mouse_y // self.search_result_item_height

                if 0 <= clicked_item_index < len(self.search_results):
                    if self.search_results[clicked_item_index].get('source_platform_id') not in ['__INFO__', '__NO_RESULTS__', '__NO_PLUGIN__']:
                        self.selected_search_result_index = clicked_item_index
                        print(f"Selected search result: {self.search_results[self.selected_search_result_index]['name']}")
                return True

        if self.search_active and event.type == pygame.MOUSEWHEEL:
            if self.search_results_area_rect.collidepoint(mouse_pos):
                if self.total_search_results_height > self.search_results_area_rect.height:
                    self.search_scroll_offset_y -= event.y * 20
                    max_scroll = self.total_search_results_height - self.search_results_area_rect.height
                    self.search_scroll_offset_y = max(0, min(self.search_scroll_offset_y, max_scroll))
                return True

        active_field_handled_by_input = False
        if self.fields_config and len(self.fields_config) > 0 and \
           self.fields_config[self.active_field_index]['name'] in self.fields:
            active_field_name = self.fields_config[self.active_field_index]['name']
            if self.fields[active_field_name].handle_event(event):
                active_field_handled_by_input = True

        if not active_field_handled_by_input:
            if self.save_button.handle_event(event): return True
            if self.cancel_button.handle_event(event): return True
            if self.search_online_button and self.search_online_button.handle_event(event): return True

        if event.type == pygame.MOUSEBUTTONDOWN and not active_field_handled_by_input:
            clicked_on_a_field = False
            if self.form_area_rect.collidepoint(event.pos):
                for i, config in enumerate(self.fields_config):
                    field_name = config['name']
                    if field_name in self.fields and self.fields[field_name].rect.collidepoint(event.pos):
                        self._set_active_field(i)
                        self.fields[field_name].handle_event(event)
                        clicked_on_a_field = True
                        break
                if not clicked_on_a_field:
                    if self.fields_config and len(self.fields_config) > 0 :
                        current_field_name = self.fields_config[self.active_field_index]['name']
                        if current_field_name in self.fields:
                            self.fields[current_field_name].active = False
                            self.fields[current_field_name].color = self.fields[current_field_name].inactive_color
        return False

    def _save(self):
        form_data = {}
        self.error_message = None
        self.error_message_surface = None

        for config in self.fields_config:
            field_name = config['name']
            if field_name not in self.fields: continue
            value = self.fields[field_name].get_text()
            if config.get('required', False) and not value.strip():
                self.error_message = f"'{config['label']}' is required."
                self.error_message_surface = self.error_font.render(self.error_message, True, pygame.Color('red'))
                return
            form_data[field_name] = value

        self.save_callback(form_data, self.platform_id_for_emulator, self.current_data)

    def update(self, delta_time):
        for field in self.fields.values():
            field.update(delta_time)

    def draw(self, screen):
        overlay_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay_surface.fill(self.overlay_color)
        screen.blit(overlay_surface, (0, 0))

        pygame.draw.rect(screen, DARK_SLATE_BLUE, self.modal_rect)
        pygame.draw.rect(screen, WHITE, self.modal_rect, 2)

        title_surface = self.title_font.render(self.title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.modal_rect.centerx, self.modal_rect.top + 30))
        screen.blit(title_surface, title_rect)

        for field_name_key in self.fields:
            if field_name_key + "_label" in self.field_labels:
                 label_surface, label_pos = self.field_labels[field_name_key + "_label"]
                 screen.blit(label_surface, label_pos)
            self.fields[field_name_key].draw(screen)

        if self.error_message_surface:
            error_x = self.form_area_rect.left + 20
            error_y = self.save_button.rect.top - self.error_message_surface.get_height() - 10
            screen.blit(self.error_message_surface, (error_x, error_y))

        self.save_button.draw(screen)
        self.cancel_button.draw(screen)
        if self.search_online_button:
            self.search_online_button.draw(screen)

        if self.search_active:
            pygame.draw.rect(screen, pygame.Color('gray20'), self.search_results_area_rect)
            pygame.draw.rect(screen, WHITE, self.search_results_area_rect, 1)

            # Visible area for search results
            visible_search_area_top = self.search_results_area_rect.top
            visible_search_area_bottom = self.search_results_area_rect.bottom

            for i, result in enumerate(self.search_results):
                item_y_true = self.search_results_area_rect.top + 5 + (i * self.search_result_item_height) - self.search_scroll_offset_y

                if item_y_true + self.search_result_item_height < visible_search_area_top or \
                   item_y_true > visible_search_area_bottom:
                    continue

                item_rect_on_screen = pygame.Rect(
                    self.search_results_area_rect.left + 5,
                    item_y_true,
                    self.search_results_area_rect.width - 10,
                    self.search_result_item_height
                )

                item_text = result.get('name', 'Unknown Result')
                if 'manufacturer' in result and result.get('manufacturer'):
                    item_text += f" ({result['manufacturer']})"

                is_info_item = result.get('source_platform_id') in ['__INFO__', '__NO_RESULTS__', '__NO_PLUGIN__']
                text_color = pygame.Color('gray60') if is_info_item else WHITE
                result_surface = self.search_result_font.render(item_text, True, text_color)

                if i == self.selected_search_result_index and not is_info_item:
                    pygame.draw.rect(screen, pygame.Color('lightskyblue3'), item_rect_on_screen)

                if item_rect_on_screen.bottom > visible_search_area_top and item_rect_on_screen.top < visible_search_area_bottom:
                    clipping_rect = item_rect_on_screen.clip(self.search_results_area_rect)
                    text_blit_pos = (item_rect_on_screen.x + 5, item_rect_on_screen.centery - result_surface.get_height() // 2)

                    if text_blit_pos[1] >= visible_search_area_top and \
                       text_blit_pos[1] + result_surface.get_height() <= visible_search_area_bottom:
                        screen.blit(result_surface, text_blit_pos, area=result_surface.get_rect().clip(clipping_rect.move(-text_blit_pos[0], -text_blit_pos[1])))

            if self.use_selected_result_button and any(r.get('source_platform_id') not in ['__INFO__', '__NO_RESULTS__', '__NO_PLUGIN__'] for r in self.search_results):
                self.use_selected_result_button.draw(screen)

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

# PlatformCard Definition
PLATFORM_CARD_PADDING = 10
PLATFORM_CARD_BUTTON_HEIGHT = 30
PLATFORM_CARD_BUTTON_WIDTH = 150 # Width for "Edit Platform" / "Add Emulator" buttons
PLATFORM_CARD_BG_COLOR = DARK_SLATE_GRAY
PLATFORM_CARD_TEXT_COLOR = WHITE
PLATFORM_CARD_LINE_SPACING = 5

# Define font sizes for PlatformCard (can be moved to constants later)
PLATFORM_NAME_FONT_SIZE = 28
PLATFORM_DETAIL_FONT_SIZE = 18
PLATFORM_DESCRIPTION_FONT_SIZE = 16
EMULATOR_HEADING_FONT_SIZE = 22
EMULATOR_NAME_FONT_SIZE = 18
EMULATOR_COMMAND_FONT_SIZE = 14
BUTTON_FONT_SIZE = 16


class PlatformCard:
    def __init__(self, platform: Platform, emulators: list[Emulator], card_width: int, data_manager: DataManager, view_callbacks: dict):
        self.platform = platform
        self.platform_id = platform.platform_id # Store platform_id
        self.emulators = emulators
        self.card_width = card_width
        self.data_manager = data_manager
        self.view_callbacks = view_callbacks # e.g. {'open_emulator_form': callback_method}


        # Initialize fonts (consider passing a font manager or dict if this grows)
        try:
            self.platform_name_font = pygame.font.Font(ORBITRON_FONT_PATH, PLATFORM_NAME_FONT_SIZE)
            self.detail_font = pygame.font.Font(ROBOTO_FONT_PATH, PLATFORM_DETAIL_FONT_SIZE)
            self.description_font = pygame.font.Font(ROBOTO_FONT_PATH, PLATFORM_DESCRIPTION_FONT_SIZE)
            self.emulator_heading_font = pygame.font.Font(ORBITRON_FONT_PATH, EMULATOR_HEADING_FONT_SIZE)
            self.emulator_name_font = pygame.font.Font(ROBOTO_FONT_PATH, EMULATOR_NAME_FONT_SIZE)
            self.emulator_command_font = pygame.font.Font(ROBOTO_FONT_PATH, EMULATOR_COMMAND_FONT_SIZE)
            self.button_font = pygame.font.Font(ROBOTO_FONT_PATH, BUTTON_FONT_SIZE)
        except pygame.error as e:
            print(f"Warning: Font file not found for PlatformCard ({e}). Falling back to default font.")
            self.platform_name_font = pygame.font.Font(None, PLATFORM_NAME_FONT_SIZE)
            self.detail_font = pygame.font.Font(None, PLATFORM_DETAIL_FONT_SIZE)
            self.description_font = pygame.font.Font(None, PLATFORM_DESCRIPTION_FONT_SIZE)
            self.emulator_heading_font = pygame.font.Font(None, EMULATOR_HEADING_FONT_SIZE)
            self.emulator_name_font = pygame.font.Font(None, EMULATOR_NAME_FONT_SIZE)
            self.emulator_command_font = pygame.font.Font(None, EMULATOR_COMMAND_FONT_SIZE)
            self.button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)

        self.surface = None # Will be created in _render_card_surface
        self.rect = pygame.Rect(0, 0, self.card_width, 0) # Height will be determined by content

        self._render_card_surface() # Initial render to determine height and content

    def _render_card_surface(self):
        current_y = PLATFORM_CARD_PADDING

        # Platform Name
        name_surface = self.platform_name_font.render(self.platform.name, True, PLATFORM_CARD_TEXT_COLOR)
        current_y += name_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # Manufacturer and Release Year
        detail_text = f"Manufacturer: {self.platform.manufacturer or 'N/A'} | Year: {self.platform.release_year or 'N/A'}"
        detail_surface = self.detail_font.render(detail_text, True, PLATFORM_CARD_TEXT_COLOR)
        current_y += detail_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # Description
        description_lines = []
        if self.platform.description:
            description_lines = wrap_text(self.platform.description, self.description_font, self.card_width - 2 * PLATFORM_CARD_PADDING)
        for line_text in description_lines:
            current_y += self.description_font.get_height() # Line spacing handled by wrap_text implicitly or add PLATFORM_CARD_LINE_SPACING
        current_y += PLATFORM_CARD_LINE_SPACING if description_lines else 0

        # "Edit Platform" Button Placeholder
        self.edit_platform_button_rect = pygame.Rect(
            PLATFORM_CARD_PADDING, current_y,
            PLATFORM_CARD_BUTTON_WIDTH, PLATFORM_CARD_BUTTON_HEIGHT
        )
        current_y += PLATFORM_CARD_BUTTON_HEIGHT + PLATFORM_CARD_LINE_SPACING * 2 # More spacing after button

        # "Emulators:" Heading
        emulator_heading_surface = self.emulator_heading_font.render("Emulators:", True, PLATFORM_CARD_TEXT_COLOR)
        current_y += emulator_heading_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # List of Emulators
        if self.emulators:
            for emulator in self.emulators:
                emu_name_surface = self.emulator_name_font.render(f"- {emulator.name}", True, PLATFORM_CARD_TEXT_COLOR)
                current_y += emu_name_surface.get_height() + PLATFORM_CARD_LINE_SPACING // 2

                emu_command_text = f"  Command: {emulator.command}"
                emu_command_surface = self.emulator_command_font.render(emu_command_text, True, PLATFORM_CARD_TEXT_COLOR)
                current_y += emu_command_surface.get_height() + PLATFORM_CARD_LINE_SPACING
        else:
            no_emu_surface = self.detail_font.render("No emulators configured for this platform.", True, PLATFORM_CARD_TEXT_COLOR)
            current_y += no_emu_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # "Add Emulator" Button Placeholder
        self.add_emulator_button_rect = pygame.Rect(
            PLATFORM_CARD_PADDING, current_y,
            PLATFORM_CARD_BUTTON_WIDTH, PLATFORM_CARD_BUTTON_HEIGHT
        )
        current_y += PLATFORM_CARD_BUTTON_HEIGHT + PLATFORM_CARD_PADDING # Final padding at the bottom

        # Create the actual surface with calculated height
        self.rect.height = current_y
        self.surface = pygame.Surface((self.card_width, self.rect.height))
        self.surface.fill(PLATFORM_CARD_BG_COLOR)

        # --- Blit everything onto the surface ---
        current_y = PLATFORM_CARD_PADDING # Reset Y for blitting

        # Platform Name
        self.surface.blit(name_surface, (PLATFORM_CARD_PADDING, current_y))
        current_y += name_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # Manufacturer and Release Year
        self.surface.blit(detail_surface, (PLATFORM_CARD_PADDING, current_y))
        current_y += detail_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # Description
        if self.platform.description:
            for line_text in description_lines:
                line_surf = self.description_font.render(line_text, True, PLATFORM_CARD_TEXT_COLOR)
                self.surface.blit(line_surf, (PLATFORM_CARD_PADDING, current_y))
                current_y += self.description_font.get_height() # + PLATFORM_CARD_LINE_SPACING
            current_y += PLATFORM_CARD_LINE_SPACING if description_lines else 0

        # "Edit Platform" Button Placeholder (Draw simple rect)
        pygame.draw.rect(self.surface, DARK_SLATE_BLUE, self.edit_platform_button_rect)
        edit_text_surf = self.button_font.render("Edit Platform", True, WHITE)
        edit_text_rect = edit_text_surf.get_rect(center=self.edit_platform_button_rect.center)
        self.surface.blit(edit_text_surf, edit_text_rect)
        current_y = self.edit_platform_button_rect.bottom + PLATFORM_CARD_LINE_SPACING * 2

        # "Emulators:" Heading
        self.surface.blit(emulator_heading_surface, (PLATFORM_CARD_PADDING, current_y))
        current_y += emulator_heading_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # List of Emulators
        if self.emulators:
            for emulator in self.emulators:
                emu_name_surface = self.emulator_name_font.render(f"- {emulator.name}", True, PLATFORM_CARD_TEXT_COLOR)
                self.surface.blit(emu_name_surface, (PLATFORM_CARD_PADDING, current_y))
                current_y += emu_name_surface.get_height() + PLATFORM_CARD_LINE_SPACING // 2

                emu_command_text = f"  Command: {emulator.command}"
                # Wrap emulator command if too long
                wrapped_cmd_lines = wrap_text(emu_command_text, self.emulator_command_font, self.card_width - PLATFORM_CARD_PADDING * 3) # Indented
                for i, cmd_line_text in enumerate(wrapped_cmd_lines):
                    emu_command_surface = self.emulator_command_font.render(cmd_line_text, True, PLATFORM_CARD_TEXT_COLOR)
                    self.surface.blit(emu_command_surface, (PLATFORM_CARD_PADDING + 15, current_y)) # Indent command
                    if i < len(wrapped_cmd_lines) -1: # If more lines for this command
                         current_y += emu_command_surface.get_height()
                current_y += emu_command_surface.get_height() + PLATFORM_CARD_LINE_SPACING
        else:
            no_emu_surface = self.detail_font.render("No emulators configured.", True, PLATFORM_CARD_TEXT_COLOR)
            self.surface.blit(no_emu_surface, (PLATFORM_CARD_PADDING, current_y))
            current_y += no_emu_surface.get_height() + PLATFORM_CARD_LINE_SPACING

        # "Add Emulator" Button
        self.add_emulator_button = Button(
            x=self.add_emulator_button_rect.x, y=self.add_emulator_button_rect.y,
            width=self.add_emulator_button_rect.width, height=self.add_emulator_button_rect.height,
            text="Add Emulator", font=self.button_font,
            callback=lambda: self.view_callbacks['open_emulator_form'](self.platform_id)
        )
        self.add_emulator_button.draw(self.surface) # Draw button onto the card's surface

    def handle_event(self, event: pygame.event.Event, mouse_offset_y: int = 0) -> bool:
        # Adjust mouse position for card's relative position if necessary (e.g. if card itself is scrollable, not needed here)
        # Buttons are drawn on the card's surface, so their rects are relative to the card's top-left (0,0)
        # We need to transform the event's mouse position to be relative to the card's surface.

        original_mouse_pos = event.pos
        # Create a new event with mouse position relative to the card's surface for button handling
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
            # mouse_offset_y is the card's current y position on the content_render_surface
            # self.rect.x/y is the card's absolute screen position if drawn directly on screen
            # For PlatformView, cards are drawn on content_render_surface then blitted.
            # The event.pos is screen-absolute. Buttons are relative to card surface.
            # We need event.pos relative to where card.surface is blitted.
            # This is tricky. For now, assume PlatformView will adjust event.pos before calling this.
            # OR, PlatformCard's buttons need their rects updated to screen coords before handling event.
            # Let's try the latter: update button rects to screen coords before passing event.

            # Create a copy of the event to modify mouse position safely
            # This is getting complicated. A simpler way:
            # PlatformView passes event.pos. PlatformCard checks collision for its own rect.
            # If inside, then it checks its buttons by transforming event.pos to be relative to card surface.

            # Let's assume for now the event passed to this button is already adjusted or the button uses screen rect.
            # The Button class uses self.rect which is set at init. This needs to be screen-relative for event.pos.
            # Simplification: PlatformView will transform mouse coordinates for its cards.
            # So, event.pos passed here is already relative to the card's surface.

            # Re-evaluate: The Button class takes absolute screen coords for x,y.
            # So, when creating button on card, its x,y should be absolute.
            # This means _render_card_surface needs card's absolute top-left (from draw call).
            # This is not ideal as _render_card_surface is for creating the static card image.

            # Alternative: Button.handle_event takes an offset.
            # self.add_emulator_button.rect is relative to card surface.
            # event.pos is absolute.
            # Effective mouse pos for button: (event.pos[0] - self.rect.left, event.pos[1] - self.rect.top)

            # Let's assume PlatformView will adjust event.pos to be relative to the card's position on the content_surface
            # if this method is called from PlatformView.draw loop or similar.
            # For now, the Button expects event.pos to be in screen coordinates.
            # We must update the button's screen rect before its handle_event.

            # This is the actual screen rect of the card.
            # self.add_emulator_button's rect is relative to the card's surface.
            # So, its screen rect is self.rect.left + self.add_emulator_button.rect.left, ...

            # Let's make Button.handle_event work with its own stored rect (which should be screen-absolute)
            # This means when the card is drawn at a position, its buttons' screen rects must be updated.
            # This is done in PlatformCard.draw()

            if self.add_emulator_button.handle_event(event):
                return True
        return False

    def draw(self, target_surface: pygame.Surface, position: tuple[int, int]):
        self.rect.topleft = position # Update card's own screen position

        # Update screen positions of interactive elements (buttons)
        # The button's rect in its class is used for collision. So it must be screen-absolute.
        # Original button rect is relative to card surface.
        self.add_emulator_button.rect.topleft = (
            self.rect.left + PLATFORM_CARD_PADDING, # Original x relative to card surface
            self.rect.top + self.add_emulator_button_rect.top # Original y relative to card surface
        )
        # Also update text_rect for centering, if text can change or button moves
        self.add_emulator_button.text_rect = self.add_emulator_button.text_surface.get_rect(center=self.add_emulator_button.rect.center)

        # TODO: Do the same for edit_platform_button if it becomes a real Button

        target_surface.blit(self.surface, self.rect)


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

# PlatformView Definition
PLATFORM_VIEW_BG_COLOR = BLACK # Or another color like DARK_SLATE_BLUE
PLATFORM_VIEW_SCROLL_SPEED = 40
PLATFORM_VIEW_CARD_SPACING = 15 # Vertical spacing between platform cards
PLATFORM_VIEW_ADD_BUTTON_HEIGHT = 40
PLATFORM_VIEW_ADD_BUTTON_WIDTH = 250
PLATFORM_VIEW_ADD_BUTTON_MARGIN = 10

class PlatformView:
    def __init__(self, x: int, y: int, width: int, height: int, data_manager: DataManager):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.data_manager = data_manager

        self.scroll_offset_y = 0.0
        self.total_content_height = 0.0
        self.cards: list[PlatformCard] = []
        self.active_modal = None # View specific modal reference

        # Fonts
        try:
            self.button_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_BUTTON_FONT_SIZE) # Standardized
        except pygame.error as e:
            print(f"Warning: Font file not found for PlatformView ({e}). Falling back to default font.")
            self.button_font = pygame.font.Font(None, UI_BUTTON_FONT_SIZE)
        # Ensure error_font is available for callbacks, if not already part of view's fonts
        try:
            self.error_font = pygame.font.Font(ROBOTO_FONT_PATH, UI_ERROR_FONT_SIZE)
        except:
            self.error_font = pygame.font.Font(None, UI_ERROR_FONT_SIZE)


        # Surface for rendering the scrollable content
        self.content_render_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.populate_platform_cards() # This calls _update_total_content_height

        # "Add New Platform" Button - now a Button object
        self.add_platform_button = Button(
            x=self.x + self.width - PLATFORM_VIEW_ADD_BUTTON_WIDTH - PLATFORM_VIEW_ADD_BUTTON_MARGIN,
            y=self.y + self.height - PLATFORM_VIEW_ADD_BUTTON_HEIGHT - PLATFORM_VIEW_ADD_BUTTON_MARGIN,
            width=PLATFORM_VIEW_ADD_BUTTON_WIDTH,
            height=PLATFORM_VIEW_ADD_BUTTON_HEIGHT,
            text="Add New Platform",
            font=self.button_font,
            callback=self.open_platform_form
        )

    def _save_platform_callback(self, form_data: dict, platform_id_for_emulator, current_platform_data=None): # platform_id_for_emulator is not used here
        global active_modal
        print(f"Save platform callback. Data: {form_data}")

        # current_platform_data would be for editing, not used in this subtask for adding
        # if current_platform_data:
        #     pass # Update existing platform
        # else:
        platform_release_year_str = form_data.get('release_year', '')
        platform_release_year = None
        if platform_release_year_str.isdigit():
            platform_release_year = int(platform_release_year_str)
        elif platform_release_year_str: # If not empty and not digit, it's an invalid year
            if self.active_modal and isinstance(self.active_modal, FormModal):
                err_msg = "Release Year must be a number."
                self.active_modal.error_message = err_msg
                self.active_modal.error_message_surface = self.active_modal.error_font.render(err_msg, True, pygame.Color('red'))
            return # Stay in modal

        new_platform = Platform(
            platform_id=form_data['platform_id'],
            name=form_data['name'],
            manufacturer=form_data.get('manufacturer', ''),
            release_year=platform_release_year,
            description=form_data.get('description', '')
        )
        try:
            self.data_manager.add_platform(new_platform)
        except ValueError as e:
            print(f"Error adding platform: {e}")
            if self.active_modal and isinstance(self.active_modal, FormModal):
                self.active_modal.error_message = str(e)
                self.active_modal.error_message_surface = self.active_modal.error_font.render(str(e), True, pygame.Color('red'))
            return # Stay in modal

        self.active_modal = None # Clear view-specific modal
        active_modal = None # Clear global reference
        self.populate_platform_cards()

    def open_platform_form(self, platform_data=None): # platform_data for editing later
        global active_modal, current_search_plugin # Make sure to use global for assignment
        title = "Add New Platform" # if platform_data is None else "Edit Platform"

        fields_config = [
            {'name': 'platform_id', 'label': 'Platform ID (e.g., snes, psx):', 'required': True},
            {'name': 'name', 'label': 'Platform Name (e.g., Super Nintendo):', 'required': True},
            {'name': 'manufacturer', 'label': 'Manufacturer (optional):', 'required': False},
            {'name': 'release_year', 'label': 'Release Year (optional, e.g., 1990):', 'required': False},
            {'name': 'description', 'label': 'Description (optional):', 'required': False},
        ]

        def perform_platform_search_callback():
            global active_modal, current_search_plugin # Ensure access to globals
            if active_modal and isinstance(active_modal, FormModal) and current_search_plugin:
                form_values = active_modal.get_form_data()
                platform_name_to_search = form_values.get('name', '')
                if platform_name_to_search:
                    print(f"PlatformView: Searching for platform '{platform_name_to_search}' using {current_search_plugin.get_name()}")
                    results = current_search_plugin.search_platform_info(platform_name_to_search)
                    active_modal.set_search_results(results)
                else:
                    print("PlatformView: No platform name entered to search.")
                    # Optionally inform user via modal error or a specific search result message
                    active_modal.set_search_results([{'name': "Please enter a name to search.", 'source_platform_id': '__INFO__'}])
            elif not current_search_plugin:
                 print("PlatformView: No search plugin configured.")
                 if active_modal and isinstance(active_modal, FormModal):
                    active_modal.set_search_results([{'name': "No search plugin available.", 'source_platform_id': '__NO_PLUGIN__'}])
            else:
                print("PlatformView: No active modal for platform search.")

        search_button_config = {
            'text': 'Search Online', # Text for the button
            'callback': perform_platform_search_callback
        }

        new_modal = FormModal(
            SCREEN_WIDTH, SCREEN_HEIGHT, title, fields_config, self.data_manager,
            save_callback=self._save_platform_callback,
            cancel_callback=self._cancel_modal_callback, # Reuses emulator cancel
            current_data=platform_data,
            search_button_config=search_button_config # Pass search button config
        )
        self.active_modal = new_modal # Set view-specific modal reference
        active_modal = new_modal # Set global active_modal


    def _save_platform_callback(self, form_data: dict, platform_id_for_emulator, current_platform_data=None): # platform_id_for_emulator is not used here
        global active_modal # Ensure we are referencing the global active_modal for assignment
        print(f"Save platform callback. Data: {form_data}")

        platform_release_year_str = form_data.get('release_year', '')
        platform_release_year = None
        if platform_release_year_str: # Only attempt conversion if not empty
            if platform_release_year_str.isdigit():
                platform_release_year = int(platform_release_year_str)
            else: # If not empty and not digit, it's an invalid year
                if self.active_modal and isinstance(self.active_modal, FormModal):
                    err_msg = "Release Year must be a number."
                    self.active_modal.error_message = err_msg
                    # Use self.error_font if available, else modal's error_font
                    font_to_use = self.error_font if hasattr(self, 'error_font') else self.active_modal.error_font
                    self.active_modal.error_message_surface = font_to_use.render(err_msg, True, pygame.Color('red'))
                return # Stay in modal

        new_platform = Platform(
            platform_id=form_data['platform_id'],
            name=form_data['name'],
            manufacturer=form_data.get('manufacturer', ''),
            release_year=platform_release_year,
            description=form_data.get('description', '')
        )
        try:
            self.data_manager.add_platform(new_platform)
        except ValueError as e:
            print(f"Error adding platform: {e}")
            if self.active_modal and isinstance(self.active_modal, FormModal):
                self.active_modal.error_message = str(e)
                font_to_use = self.error_font if hasattr(self, 'error_font') else self.active_modal.error_font
                self.active_modal.error_message_surface = font_to_use.render(str(e), True, pygame.Color('red'))
            return

        self.active_modal = None
        active_modal = None
        self.populate_platform_cards()

    def open_platform_form(self, platform_data=None):
        global active_modal, current_search_plugin
        title = "Add New Platform"

        fields_config = [
            {'name': 'platform_id', 'label': 'Platform ID (e.g., snes, psx):', 'required': True},
            {'name': 'name', 'label': 'Platform Name (e.g., Super Nintendo):', 'required': True},
            {'name': 'manufacturer', 'label': 'Manufacturer (optional):', 'required': False},
            {'name': 'release_year', 'label': 'Release Year (optional, e.g., 1990):', 'required': False},
            {'name': 'description', 'label': 'Description (optional):', 'required': False},
        ]

        def perform_platform_search_callback():
            global active_modal, current_search_plugin
            if active_modal and isinstance(active_modal, FormModal) and current_search_plugin:
                form_values = active_modal.get_form_data()
                platform_name_to_search = form_values.get('name', '')
                if platform_name_to_search:
                    print(f"PlatformView: Searching for platform '{platform_name_to_search}' using {current_search_plugin.get_name()}")
                    results = current_search_plugin.search_platform_info(platform_name_to_search)
                    active_modal.set_search_results(results)
                else:
                    print("PlatformView: No platform name entered to search.")
                    active_modal.set_search_results([{'name': "Please enter a name to search.", 'source_platform_id': '__INFO__'}])
            elif not current_search_plugin:
                 print("PlatformView: No search plugin configured.")
                 if active_modal and isinstance(active_modal, FormModal):
                    active_modal.set_search_results([{'name': "No search plugin available.", 'source_platform_id': '__NO_PLUGIN__'}])
            else:
                print("PlatformView: No active modal for platform search.")

        search_button_config = {
            'text': 'Search Online',
            'callback': perform_platform_search_callback
        }

        new_modal = FormModal(
            SCREEN_WIDTH, SCREEN_HEIGHT, title, fields_config, self.data_manager,
            save_callback=self._save_platform_callback,
            cancel_callback=self._cancel_modal_callback,
            current_data=platform_data,
            search_button_config=search_button_config
        )
        self.active_modal = new_modal
        active_modal = new_modal


    def populate_platform_cards(self):
        self.cards = []
        platforms = self.data_manager.get_all_platforms()
        card_width = self.width
        # Consider scrollbar width if visible
        # if self._is_scrollbar_needed(): card_width -= 15 # Scrollbar width

        view_callbacks = {'open_emulator_form': self.open_emulator_form}

        for platform_obj in platforms:
            emulators = self.data_manager.get_emulators_for_platform(platform_obj.platform_id)
            card = PlatformCard(platform_obj, emulators, card_width, self.data_manager, view_callbacks)
            self.cards.append(card)
        self._update_total_content_height() # Recalculate height and adjust scroll


    def _update_total_content_height(self):
        current_h = PLATFORM_VIEW_CARD_SPACING # Start with top spacing
        for card in self.cards:
            current_h += card.rect.height + PLATFORM_VIEW_CARD_SPACING
        self.total_content_height = current_h

        # Adjust scroll offset if content is now smaller than scroll offset
        max_scroll = max(0, self.total_content_height - self.height)
        self.scroll_offset_y = max(0, min(self.scroll_offset_y, max_scroll))



    def _save_emulator_callback(self, form_data: dict, platform_id: str, existing_emulator_data: Emulator = None):
        print(f"Save emulator callback for platform {platform_id}. Data: {form_data}")
        global active_modal # Ensure we are referencing the global active_modal

        if existing_emulator_data: # This would be for editing
            # existing_emulator_data.name = form_data['name'] ... etc.
            # self.data_manager.update_emulator_on_platform(platform_id, existing_emulator_data.emulator_id, existing_emulator_data)
            print("Updating emulator (Not fully implemented yet)")
            pass
        else: # Adding new emulator
            new_emulator = Emulator(
                emulator_id=form_data['emulator_id'],
                name=form_data['name'],
                command=form_data['command'],
                description=form_data.get('description', ''),
                website=form_data.get('website', '')
            )
            try:
                self.data_manager.add_emulator_to_platform(platform_id, new_emulator)
            except ValueError as e:
                print(f"Error adding emulator: {e}")
                if self.active_modal and isinstance(self.active_modal, FormModal):
                     self.active_modal.error_message = str(e)
                     self.active_modal.error_message_surface = self.active_modal.error_font.render(str(e), True, pygame.Color('red'))
                return

        self.active_modal = None
        active_modal = None # Clear global reference
        self.populate_platform_cards()

    def _cancel_modal_callback(self):
        global active_modal # Ensure we are referencing the global active_modal
        self.active_modal = None
        active_modal = None


    def open_emulator_form(self, platform_id: str, emulator_data: Emulator = None):
        global active_modal # Ensure we are setting the global active_modal
        title = "Add New Emulator" if emulator_data is None else "Edit Emulator"
        fields_config = [
            {'name': 'emulator_id', 'label': 'Emulator ID (e.g., snes9x):', 'required': True},
            {'name': 'name', 'label': 'Emulator Name (e.g., Snes9x):', 'required': True},
            {'name': 'command', 'label': 'Command (use %ROM% for ROM path):', 'required': True},
            {'name': 'description', 'label': 'Description (optional):', 'required': False},
            {'name': 'website', 'label': 'Website (optional):', 'required': False},
        ]

        # Create the modal and assign it to both the view's and the global active_modal variable
        new_modal = FormModal(
            SCREEN_WIDTH, SCREEN_HEIGHT, title, fields_config, self.data_manager,
            save_callback=self._save_emulator_callback,
            cancel_callback=self._cancel_modal_callback,
            platform_id_for_emulator=platform_id,
            current_data=emulator_data
        )
        self.active_modal = new_modal
        active_modal = new_modal


    def handle_event(self, event: pygame.event.Event):
        # The global active_modal is handled in the main loop first.
        # This view's self.active_modal is primarily for its own state management if needed,
        # but decisions to open/close modals will set the global one.
        # So, if a modal is active, main loop's event handling for active_modal takes precedence.

        if self.add_platform_button.handle_event(event):
            return True # Event handled by the view's own button

        # Pass events to cards (e.g., for their buttons)
        # Cards are drawn on content_render_surface, which is at self.x, self.y
        # Card positions are relative to content_render_surface.
        # Button rects are updated in PlatformCard.draw to be screen-absolute.
        for card in self.cards:
            # Only process events for cards that are currently visible to some extent
            # card.rect is updated in PlatformCard.draw to its current screen position
            if card.rect.bottom > self.y and card.rect.top < self.y + self.height: # Crude visibility check
                 if card.handle_event(event): # if a card's button handled it
                      return # Event handled by a card button

        if event.type == pygame.MOUSEWHEEL:
            if self.total_content_height > self.height:
                self.scroll_offset_y -= event.y * PLATFORM_VIEW_SCROLL_SPEED
                max_scroll = self.total_content_height - self.height
                self.scroll_offset_y = max(0, min(self.scroll_offset_y, max_scroll))

    def update(self, delta_time: float):
        if self.active_modal:
            self.active_modal.update(delta_time)
            return
        # No card-specific updates for now

    def draw(self, screen: pygame.Surface):
        screen.fill(PLATFORM_VIEW_BG_COLOR, (self.x, self.y, self.width, self.height))
        self.content_render_surface.fill((0,0,0,0)) # Clear with transparency

        current_card_y_on_content_surface = PLATFORM_VIEW_CARD_SPACING - self.scroll_offset_y
        for card in self.cards:
            card_screen_y = self.y + current_card_y_on_content_surface
            # Update card's absolute screen rect for drawing and interaction checks
            card.rect.topleft = (self.x, card_screen_y)

            if card.rect.bottom > self.y and card.rect.top < self.y + self.height:
                 # Draw card onto the content_render_surface at its current scrolled Y position
                 # The card.draw method itself needs the position on the target surface (content_render_surface)
                 card.draw(self.content_render_surface, (0, int(current_card_y_on_content_surface + self.scroll_offset_y)))
            current_card_y_on_content_surface += card.rect.height + PLATFORM_VIEW_CARD_SPACING

        screen.blit(self.content_render_surface, (self.x, self.y))
        self.add_platform_button.draw(screen) # Draw button on main screen

        # Modal is drawn by main loop if active_modal is set globally

# --- Module-level globals for state accessible by callbacks ---
active_modal = None
current_search_plugin = None # Will hold the currently selected plugin for search operations
# Initialize plugins early (mock for now as an example)
try:
    mock_plugin_instance = get_plugin_instance("mock")
except Exception as e: # Catch potential errors if plugin system changes/fails
    print(f"Error initializing mock_plugin_instance: {e}")
    mock_plugin_instance = None

active_plugins_list = [mock_plugin_instance] if mock_plugin_instance else []
if active_plugins_list:
    current_search_plugin = active_plugins_list[0]
else:
    print("Warning: No search plugins loaded. Search functionality will be disabled.")


def main():
    pygame.init()
    current_view = "games"
    # active_modal is now a module global, initialized above
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
    GRID_COLS = 2
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

    # Pass SCREEN_WIDTH, SCREEN_HEIGHT to PlatformView if it needs to open modals
    # Or, PlatformView.open_emulator_form can access global SCREEN_WIDTH, SCREEN_HEIGHT
    platform_view = PlatformView(
        x=GRID_VIEWPORT_X, y=GRID_VIEWPORT_Y,
        width=GRID_VIEWPORT_WIDTH, height=GRID_VIEWPORT_HEIGHT,
        data_manager=data_manager
    )

    running = True
    while running:
        delta_time_ms = clock.tick(FPS)
        delta_time_s = delta_time_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- Global event handling (modal, then view switching, then view-specific) ---
            if active_modal: # Modal consumes all events first
                active_modal.handle_event(event)
            elif event.type == pygame.KEYDOWN: # Handle global key presses if no modal
                if event.key == pygame.K_ESCAPE:
                    running = False # Global escape to quit
                elif event.key == pygame.K_p:
                    if current_view == "games": current_view = "platforms"
                    else: current_view = "games"
                    print(f"Switched to {current_view} view")
                # Let views handle their own specific key presses if needed
                elif current_view == "games":
                    game_grid.handle_event(event)
                elif current_view == "platforms":
                    platform_view.handle_event(event) # This will now correctly pass to cards
            # Pass other events (like MOUSEWHEEL, MOUSEBUTTONDOWN for non-key events) to current view
            elif current_view == "games":
                game_grid.handle_event(event)
            elif current_view == "platforms":
                platform_view.handle_event(event) # This will now correctly pass to cards


        # --- Updates ---
        if active_modal:
            active_modal.update(delta_time_s)
        elif current_view == "games":
            game_grid.update(delta_time_s)
        elif current_view == "platforms":
            platform_view.update(delta_time_s)

        # --- Drawing ---
        screen.fill(BLACK)
        screen.blit(page_title_surface, page_title_rect)

        if current_view == "games":
            game_grid.draw(screen)
        elif current_view == "platforms":
            platform_view.draw(screen)

        if active_modal: # Draw modal on top of the current view
            active_modal.draw(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()