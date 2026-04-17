import pygame
import win32api, win32con, win32gui
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
        self.font_small = pygame.font.SysFont("Arial", 9)
        self.font_medium = pygame.font.SysFont("Arial", 11)
        
        # Speech bubble state
        self.speech_bubble_text = ""
        self.speech_bubble_time = 0
        self.speech_bubble_duration = 5  # seconds
        
        # Menu state
        self.show_menu = False
        self.menu_options = [
            {'key': 'S', 'label': 'Simplify', 'intent': 'simplify'},
            {'key': 'T', 'label': 'Translate', 'intent': 'translate'},
            {'key': 'B', 'label': 'Bionic', 'intent': 'bionic'},
            {'key': 'E', 'label': 'Explain', 'intent': 'explain'},
        ]
        self.selected_option = 0
        
        # Transparent Overlay Logic
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.trans_color), 0, win32con.LWA_COLORKEY)

    def show_speech_bubble(self, text, duration=5):
        """Display AI response as a speech bubble"""
        self.speech_bubble_text = text
        self.speech_bubble_time = time.time()
        self.speech_bubble_duration = duration

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

    def select_menu_option(self):
        """Get currently selected menu option"""
        if self.selected_option < len(self.menu_options):
            return self.menu_options[self.selected_option]
        return None

    def draw_speech_bubble(self):
        """Draw AI response speech bubble"""
        if not self.is_speech_bubble_active():
            return
        
        # Wrap text
        max_width = 180
        words = self.speech_bubble_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.font_small.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Draw bubble background
        line_height = 18
        bubble_height = len(lines) * line_height + 15
        bubble_width = max_width + 20
        bubble_x = 125 - bubble_width // 2
        bubble_y = 40
        
        # Bubble rectangle
        pygame.draw.rect(self.screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (bubble_x, bubble_y, bubble_width, bubble_height), 2, border_radius=10)
        
        # Pointer to pet
        pygame.draw.polygon(self.screen, (255, 255, 255), [(125, bubble_y + bubble_height), (115, bubble_y + bubble_height + 10), (135, bubble_y + bubble_height + 10)])
        
        # Draw text
        for i, line in enumerate(lines):
            text_surf = self.font_small.render(line, True, (0, 0, 0))
            self.screen.blit(text_surf, (bubble_x + 10, bubble_y + 7 + i * line_height))

    def draw_menu(self):
        """Draw intent-based menu"""
        if not self.show_menu:
            return
        
        menu_width = 200
        menu_height = len(self.menu_options) * 35 + 20
        menu_x = 125 - menu_width // 2
        menu_y = 150
        
        # Menu background
        pygame.draw.rect(self.screen, (40, 40, 40), (menu_x, menu_y, menu_width, menu_height), border_radius=10)
        pygame.draw.rect(self.screen, (100, 200, 255), (menu_x, menu_y, menu_width, menu_height), 3, border_radius=10)
        
        # Menu title
        title = self.font_medium.render("Text Actions", True, (255, 255, 255))
        self.screen.blit(title, (menu_x + 10, menu_y + 5))
        
        # Menu options
        for i, option in enumerate(self.menu_options):
            option_y = menu_y + 30 + i * 35
            is_selected = i == self.selected_option
            
            # Highlight selected
            if is_selected:
                pygame.draw.rect(self.screen, (100, 200, 255), (menu_x + 5, option_y, menu_width - 10, 30), border_radius=5)
            
            # Option text
            text = f"{option['key']}: {option['label']}"
            color = (255, 255, 100) if is_selected else (200, 200, 200)
            text_surf = self.font_small.render(text, True, color)
            self.screen.blit(text_surf, (menu_x + 15, option_y + 8))

    def draw(self, pet: Pet, hat=None):
        """Main draw function"""
        self.screen.fill(self.trans_color)
        
        # Load current mode
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            mode = data.get("mode", "default")
        except:
            mode = "default"
        
        # Pet color based on mode
        if mode == "focus":
            color = (255, 100, 100)  # Red for Focus mode
        else:
            color = (100, 200, 255)  # Blue for Default mode
        
        # Animation: bouncing effect
        bounce = math.sin(self.frame * 0.1) * 5
        body_y = pet.y + bounce
        
        # Draw pet
        sprites = pygame.sprite.Group()
        sprites.add(pet)
        sprites.draw(self.screen)
        
        # Draw hat if equipped #TODO
        # if hat == "Top Hat":
        #     hat_y = 40 + bounce
        #     pygame.draw.rect(self.screen, (40, 40, 40), (95, int(hat_y), 60, 25))
        #     pygame.draw.rect(self.screen, (10, 10, 10), (85, int(hat_y + 25), 80, 5))
        
        # Draw mode indicator emoji
        mode_text = "🎯" if mode == "focus" else "📚"
        mode_label = self.font_medium.render(mode_text, True, (255, 255, 255))
        self.screen.blit(mode_label, (10, 10))
        
        # Draw speech bubble if active
        self.draw_speech_bubble()
        
        # Draw menu if active
        self.draw_menu()
        
        # Draw instructions if menu is showing
        if self.show_menu:
            inst_text = self.font_small.render("Use arrow keys, Enter to select", True, (150, 150, 150))
            self.screen.blit(inst_text, (10, 230))

        self.frame += 1
        pygame.display.update()
