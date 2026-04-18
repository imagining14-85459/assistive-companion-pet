import pygame
import sys
import math
import json
import time
from pet_body import Pet

class PetUI:
    def __init__(self, size=(1920, 1080)):
        pygame.init()
        self.size = size
        self.trans_color = (255, 0, 128) # Fuchsia background
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        pygame.display.set_caption("Aether Assistant - Pet")
        
        # Animation tracking
        self.frame = 0
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.font_medium = pygame.font.SysFont("Arial", 18)
        
        # Speech bubble state
        self.speech_bubble_text = ""
        self.speech_bubble_time = 0
        self.speech_bubble_duration = 5  # seconds
        self.is_loading = False
        self.loading_text = ""

        # Menu state
        self.show_menu = False
        self.show_translate_menu = False
        self.menu_options = [
            {'key': 'S', 'label': 'Simplify Text', 'intent': 'simplify', 'requires_clipboard': True},
            {'key': 'T', 'label': 'Translate Text', 'intent': 'translate', 'requires_clipboard': True},
            {'key': 'B', 'label': 'Bionic Reading', 'intent': 'bionic', 'requires_clipboard': True},
            {'key': 'E', 'label': 'Explain Text', 'intent': 'explain', 'requires_clipboard': True},
            {'key': 'C', 'label': 'Study Screen', 'intent': 'screen_study', 'requires_clipboard': False},
        ]
        self.translate_options = [
            {'key': '1', 'label': 'Spanish', 'language': 'Spanish'},
            {'key': '2', 'label': 'French', 'language': 'French'},
            {'key': '3', 'label': 'German', 'language': 'German'},
            {'key': '5', 'label': 'Portuguese', 'language': 'Portuguese'},
            {'key': '6', 'label': 'Chinese', 'language': 'Chinese'},
            {'key': '7', 'label': 'Japanese', 'language': 'Japanese'},
            {'key': '8', 'label': 'Korean', 'language': 'Korean'},
        ]
        self.selected_option = 0

        if sys.platform == "win32":
            import win32api, win32con, win32gui
            hwnd = pygame.display.get_wm_info()["window"]
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.trans_color), 0, win32con.LWA_COLORKEY)
        else:
            # Mac: try to float window above others using pyobjc
            try:
                from AppKit import NSApp, NSFloatingWindowLevel
                NSApp.windows()[0].setLevel_(NSFloatingWindowLevel)
            except ImportError:
                pass  # works without it, just won't float above other windows
        
        # Platform-specific overlay setup
        hwnd = pygame.display.get_wm_info()["window"]
        # Platform-specific overlay setup
        if sys.platform == "win32":
            import win32api, win32con, win32gui
            hwnd = pygame.display.get_wm_info()["window"]
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.trans_color), 0, win32con.LWA_COLORKEY)
        else:
            try:
                from AppKit import NSApp, NSFloatingWindowLevel
                NSApp.windows()[0].setLevel_(NSFloatingWindowLevel)
            except ImportError:
                pass

    def pet_speaks(self, pet, text, duration=5):
        """ Orders a pet to speak. """
        if not pet.shown: return
        self.show_speech_bubble(text, duration)

    def show_speech_bubble(self, text, duration=5):
        """Display AI response as a speech bubble"""
        self.speech_bubble_text = text
        self.speech_bubble_time = time.time()
        self.speech_bubble_duration = duration
        self.hide_loading()

    def show_loading(self, text="Thinking..."):
        """Show a loading state while AI is processing"""
        self.loading_text = text
        self.is_loading = True
        self.speech_bubble_text = ""

    def hide_loading(self):
        """Hide the loading indicator"""
        self.is_loading = False
        self.loading_text = ""

    def is_speech_bubble_active(self):
        """Check if speech bubble should still be displayed"""
        if not self.speech_bubble_text:
            return False
        elapsed = time.time() - self.speech_bubble_time
        return elapsed < self.speech_bubble_duration

    def toggle_menu(self, show=None):
        """Show/hide intent menu"""
        if show is None:
            self.show_menu = not self.show_menu
        else:
            self.show_menu = show
        self.selected_option = 0

    def toggle_translate_menu(self, show=True):
        """Show/hide translate language selection menu"""
        self.show_translate_menu = show
        if show:
            self.selected_option = 0  # Reset selection

    def select_translate_option(self):
        """Get currently selected translate language option"""
        if self.selected_option < len(self.translate_options):
            return self.translate_options[self.selected_option]
        return None

    def select_menu_option(self):
        """Get currently selected main menu option"""
        if self.selected_option < len(self.menu_options):
            return self.menu_options[self.selected_option]
        return None

    def draw_speech_bubble(self, x, y):
        """Draw AI response speech bubble"""
        if not self.is_speech_bubble_active():
            return

        # Wrap text with better handling for long messages
        max_width = 220  # Increased width
        max_lines = 8   # Limit lines to prevent overflow
        words = self.speech_bubble_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.font_small.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                    if len(lines) >= max_lines - 1:  # Leave room for truncation message
                        break
                current_line = word
            else:
                current_line = test_line
        
        if current_line and len(lines) < max_lines:
            lines.append(current_line)
        
        # Truncate if too long
        if len(lines) >= max_lines:
            lines = lines[:max_lines-1]
            lines.append("... (truncated)")

        # Draw bubble background
        line_height = 16
        bubble_height = len(lines) * line_height + 20
        bubble_width = max_width + 20
        bubble_x = x
        bubble_y = y - bubble_height*2
        # Ensure bubble doesn't go off screen
        screen_width, screen_height = self.size
        if bubble_x < 10:
            bubble_x = 10
        if bubble_x + bubble_width > screen_width - 10:
            bubble_x = screen_width - bubble_width - 10
        if bubble_y + bubble_height > screen_height - 10:
            bubble_y = screen_height - bubble_height - 10

        # Bubble rectangle with pixel-art colors (more visible)
        pygame.draw.rect(self.screen, (255, 255, 200), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=8)  # Light yellow background
        pygame.draw.rect(self.screen, (0, 0, 0), (bubble_x, bubble_y, bubble_width, bubble_height), 2, border_radius=8)  # Black border
        
        # Draw text
        for i, line in enumerate(lines):
            text_surf = self.font_small.render(line, True, (0, 0, 0))  # Black text
            self.screen.blit(text_surf, (bubble_x + 10, bubble_y + 8 + i * line_height))

    def pet_menu(self, pet):
        """ Shows the menu, depending on whether the pet is shown or not. """
        if not pet.shown: return
        self.draw_menu(pet.x, pet.y)

    def draw_menu(self, x, y):
        """Draw intent-based menu with pixel-art styling"""
        if not self.show_menu:
            return

        if self.show_translate_menu:
            self.draw_translate_menu(x,y)
        else:
            self.draw_choices_menu(x,y)
    def draw_translate_menu(self, x, y):
        # Draw translate language selection menu
        menu_width = 280
        menu_height = len(self.translate_options) * 35 + 50
        menu_x = x - menu_width
        menu_y = y - menu_height
        # Menu background with pixel-art colors
        pygame.draw.rect(self.screen, (245, 230, 200), (menu_x, menu_y, menu_width, menu_height), border_radius=8)  # Parchment background
        pygame.draw.rect(self.screen, (92, 54, 30), (menu_x, menu_y, menu_width, menu_height), 3, border_radius=8)  # Wood border

        title = self.font_medium.render("🌐 Select Language", True, (92, 54, 30))
        self.screen.blit(title, (menu_x + 10, menu_y + 5))

        # Back option
        back_y = menu_y + 30
        is_selected = self.selected_option == -1
        if is_selected:
            pygame.draw.rect(self.screen, (255, 180, 100), (menu_x + 5, back_y, menu_width - 10, 30), border_radius=5)
        back_text = self.font_medium.render("← Back to Main Menu", True, (92, 54, 30) if is_selected else (107, 70, 43))
        self.screen.blit(back_text, (menu_x + 15, back_y + 5))

        # Language options
        for i, option in enumerate(self.translate_options):
            option_y = menu_y + 70 + i * 35
            is_selected = i == self.selected_option

            if is_selected:
                pygame.draw.rect(self.screen, (255, 180, 100), (menu_x + 5, option_y, menu_width - 10, 30),
                                 border_radius=5)

            text = f"{option['key']}: {option['label']}"
            color = (92, 54, 30) if is_selected else (107, 70, 43)
            text_surf = self.font_medium.render(text, True, color)
            self.screen.blit(text_surf, (menu_x + 15, option_y + 5))

    def draw_choices_menu(self, x, y):
        menu_width = 200
        menu_height = len(self.menu_options) * 45 + 20
        menu_x = x - menu_width
        menu_y = y - menu_height

        # Menu background
        pygame.draw.rect(self.screen, (245, 230, 200), (menu_x, menu_y, menu_width, menu_height),
                         border_radius=8)  # Parchment
        pygame.draw.rect(self.screen, (92, 54, 30), (menu_x, menu_y, menu_width, menu_height), 3,
                         border_radius=8)  # Wood border

        # Menu title
        title = self.font_medium.render("🤖 AI Study Tools", True, (92, 54, 30))
        self.screen.blit(title, (menu_x + 10, menu_y + 5))

        # Menu options
        for i, option in enumerate(self.menu_options):
            option_y = menu_y + 35 + i * 45
            is_selected = i == self.selected_option

            # Highlight selected with warm color
            if is_selected:
                pygame.draw.rect(self.screen, (255, 180, 100), (menu_x + 5, option_y, menu_width - 10, 35),
                                 border_radius=5)

            # Option text
            text = f"{option['key']}: {option['label']}"
            color = (92, 54, 30) if is_selected else (107, 70, 43)
            text_surf = self.font_medium.render(text, True, color)
            self.screen.blit(text_surf, (menu_x + 15, option_y + 8))

    def draw(self, pet: Pet):
        """Main draw function"""
        self.screen.fill(self.trans_color)
        
        # Load current mode
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            mode = data.get("mode", "default")
        except (FileNotFoundError, json.JSONDecodeError):
            mode = "default"
        
        # Pet color based on mode
        if mode == "focus":
            color = (255, 100, 100)  # Red for Focus mode
        else:
            color = (100, 200, 255)  # Blue for Default mode
        
        # Animation: bouncing effect
        bounce = math.sin(self.frame * 0.1)
        pet.y = pet.y + bounce
        pet.update_rect()

        # Draw pet
        if pet.shown:
            sprites = pygame.sprite.Group()
            sprites.add(pet)
            if pet.hat: sprites.add(pet.hat)
            sprites.draw(self.screen)
        
        # Draw mode indicator emoji
        mode_text = "🎯" if mode == "focus" else "📚"
        mode_label = self.font_medium.render(mode_text, True, (255, 255, 255))
        self.screen.blit(mode_label, (10, 10))
        
        # Draw speech bubble if active
        if pet.shown: self.draw_speech_bubble(pet.x, pet.y)
        
        # Draw menu if active
        self.pet_menu(pet)
        
        # Draw instructions if menu is showing #TODO: move with pet
        if self.show_menu:
            inst_text = self.font_small.render("Use arrow keys, Enter to select, ESC to close", True, (150, 150, 150))
            self.screen.blit(inst_text, (10, 230))
            alt_text = self.font_small.render("Alt+A to open menu anytime", True, (150, 150, 150))
            self.screen.blit(alt_text, (10, 245))

        self.frame += 1
        pygame.display.update()

    def draw_loading(self):
        """Draw temporary loading text when AI is processing"""
        if not self.is_loading or not self.loading_text:
            return
        loading_surf = self.font_medium.render(self.loading_text, True, (255, 255, 255))
        bg_width = loading_surf.get_width() + 16
        bg_height = loading_surf.get_height() + 10
        bg_x = 10
        bg_y = self.size[1] - bg_height - 10
        loading_bg = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        loading_bg.fill((0, 0, 0, 180))
        self.screen.blit(loading_bg, (bg_x, bg_y))
        pygame.draw.rect(self.screen, (255, 255, 255), (bg_x, bg_y, bg_width, bg_height), 1, border_radius=6)
        self.screen.blit(loading_surf, (bg_x + 8, bg_y + 5))