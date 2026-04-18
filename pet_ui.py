import pygame
import win32api, win32con, win32gui
import math
import json
import time

class PetUI:
    def __init__(self, size=(350, 350)):
        pygame.init()
        self.size = size
        self.trans_color = (255, 0, 128) # Fuchsia background
        self.screen = pygame.display.set_mode(size, pygame.NOFRAME | pygame.SRCALPHA)
        pygame.display.set_caption("Aether Assistant - Pet")
        self.hwnd = None
        
        # Try transparent overlay, fallback to solid window
        try:
            import win32api, win32con, win32gui
            hwnd = pygame.display.get_wm_info()["window"]
            self.hwnd = hwnd
            # Position in top-right corner, less intrusive
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            window_x = screen_width - self.size[0] - 20
            window_y = 40  # Near top of screen
            
            # Force window to stay on top and remain visible
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, window_x, window_y, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.trans_color), 0, win32con.LWA_COLORKEY)
            self.transparent = True
            print(f"✓ Transparent overlay enabled at ({window_x}, {window_y})")
        except ImportError:
            print("⚠ pywin32 not available - using solid window")
            self.transparent = False
            # For solid mode, just keep the NOFRAME window as is
        
        # Animation tracking
        self.frame = 0
        self.font_small = pygame.font.SysFont("Arial", 9)
        self.font_medium = pygame.font.SysFont("Arial", 11)
        
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

    def show_speech_bubble(self, text, duration=5):
        """Display AI response as a speech bubble"""
        print(f"🗯️ Showing speech bubble: '{text[:50]}...' for {duration}s")
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

    def draw_pet(self, body_y, color):
        """Draw the pet character"""
        # Draw Pet Body with border
        pygame.draw.circle(self.screen, (0, 0, 0), (125, int(body_y)), 62)  # Black border
        pygame.draw.circle(self.screen, color, (125, int(body_y)), 60) # Body
        pygame.draw.circle(self.screen, (255, 255, 255), (105, int(body_y - 10)), 6) # Eye white L
        pygame.draw.circle(self.screen, (255, 255, 255), (145, int(body_y - 10)), 6) # Eye white R
        pygame.draw.circle(self.screen, (0, 0, 0), (105, int(body_y - 10)), 3) # Pupil L
        pygame.draw.circle(self.screen, (0, 0, 0), (145, int(body_y - 10)), 3) # Pupil R
        
        # Happy mouth (curved smile)
        pygame.draw.arc(self.screen, (0, 0, 0), (110, int(body_y + 5), 30, 20), 0, 3.14, 3)
        
        # Add "AI Pet" label
        label = self.font_medium.render("AI Pet", True, (0, 0, 0))
        self.screen.blit(label, (125 - label.get_width() // 2, int(body_y + 70)))

    def draw_speech_bubble(self):
        """Draw AI response speech bubble"""
        if not self.is_speech_bubble_active():
            return
        
        print(f"🎨 Drawing speech bubble: '{self.speech_bubble_text[:30]}...'")
        
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
        bubble_x = 125 - bubble_width // 2
        bubble_y = 30  # Moved up a bit
        
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
        
        # Pointer to pet (adjusted for new position)
        pointer_x = 125
        pointer_y = bubble_y + bubble_height
        pygame.draw.polygon(self.screen, (245, 230, 200), [(pointer_x, pointer_y), (pointer_x-8, pointer_y+8), (pointer_x+8, pointer_y+8)])
        pygame.draw.polygon(self.screen, (92, 54, 30), [(pointer_x, pointer_y), (pointer_x-8, pointer_y+8), (pointer_x+8, pointer_y+8)], 2)
        
        # Draw text (black on light background for better visibility)
        for i, line in enumerate(lines):
            text_surf = self.font_small.render(line, True, (0, 0, 0))  # Black text
            self.screen.blit(text_surf, (bubble_x + 10, bubble_y + 8 + i * line_height))

    def draw_menu(self):
        """Draw intent-based menu with pixel-art styling"""
        if not self.show_menu:
            return
        
        if self.show_translate_menu:
            # Draw translate language selection menu
            menu_width = 280
            menu_height = len(self.translate_options) * 35 + 50
            menu_x = 175 - menu_width // 2
            menu_y = 180
            
            # Menu background with pixel-art colors
            pygame.draw.rect(self.screen, (245, 230, 200), (menu_x, menu_y, menu_width, menu_height), border_radius=8)  # Parchment background
            pygame.draw.rect(self.screen, (92, 54, 30), (menu_x, menu_y, menu_width, menu_height), 3, border_radius=8)  # Wood border
            
            # Menu title
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
                    pygame.draw.rect(self.screen, (255, 180, 100), (menu_x + 5, option_y, menu_width - 10, 30), border_radius=5)
                
                text = f"{option['key']}: {option['label']}"
                color = (92, 54, 30) if is_selected else (107, 70, 43)
                text_surf = self.font_medium.render(text, True, color)
                self.screen.blit(text_surf, (menu_x + 15, option_y + 5))
        else:
            # Draw main menu with pixel-art styling
            menu_width = 280
            menu_height = len(self.menu_options) * 45 + 20
            menu_x = 175 - menu_width // 2
            menu_y = 180
            
            # Menu background
            pygame.draw.rect(self.screen, (245, 230, 200), (menu_x, menu_y, menu_width, menu_height), border_radius=8)  # Parchment
            pygame.draw.rect(self.screen, (92, 54, 30), (menu_x, menu_y, menu_width, menu_height), 3, border_radius=8)  # Wood border
            
            # Menu title
            title = self.font_medium.render("🤖 AI Study Tools", True, (92, 54, 30))
            self.screen.blit(title, (menu_x + 10, menu_y + 5))
            
            # Menu options
            for i, option in enumerate(self.menu_options):
                option_y = menu_y + 35 + i * 45
                is_selected = i == self.selected_option
                
                # Highlight selected with warm color
                if is_selected:
                    pygame.draw.rect(self.screen, (255, 180, 100), (menu_x + 5, option_y, menu_width - 10, 35), border_radius=5)
                
                # Option text
                text = f"{option['key']}: {option['label']}"
                color = (92, 54, 30) if is_selected else (107, 70, 43)
                text_surf = self.font_medium.render(text, True, color)
                self.screen.blit(text_surf, (menu_x + 15, option_y + 8))

    def draw(self, hat=None, focus_status=None):
        """Main draw function"""
        # Clear screen with background
        self.screen.fill(self.trans_color)  # Fill with transparent color
        
        if self.transparent and self.hwnd:
            self.keep_on_top()
        
        # Load current mode
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            mode = data.get("mode", "default")
        except:
            mode = "default"
        
        # Pet color based on mode and focus status
        if mode == "focus":
            if focus_status == "lost":
                color = (255, 50, 50)  # Dark red when focus lost
            else:
                color = (255, 100, 100)  # Red for Focus mode
        else:
            color = (100, 200, 255)  # Blue for Default mode
        
        # Gentle bouncing animation (predictable and smooth)
        bounce = math.sin(self.frame * 0.05) * 3  # Slower, smaller bounce
        body_y = 110 + bounce
        
        # Draw pet
        self.draw_pet(body_y, color)
        
        # Draw hat if equipped
        if hat == "Top Hat":
            hat_y = 40 + bounce
            pygame.draw.rect(self.screen, (40, 40, 40), (95, int(hat_y), 60, 25))
            pygame.draw.rect(self.screen, (10, 10, 10), (85, int(hat_y + 25), 80, 5))
        
        # Draw mode indicator emoji
        mode_text = "🎯" if mode == "focus" else "📚"
        mode_label = self.font_medium.render(mode_text, True, (255, 255, 255))
        self.screen.blit(mode_label, (10, 10))
        
        # Draw focus warning indicator if in focus mode and focus lost
        if mode == "focus" and focus_status == "lost":
            warning_text = "⚠️"
            warning_label = self.font_medium.render(warning_text, True, (255, 255, 0))
            self.screen.blit(warning_label, (10, 35))
        
        # Draw speech bubble if active
        self.draw_speech_bubble()
        
        # Draw loading indicator if active
        self.draw_loading()
        
        # Draw menu if active
        self.draw_menu()
        
        # Draw instructions if menu is showing
        if self.show_menu:
            inst_text = self.font_small.render("Use arrow keys, Enter to select, ESC to close", True, (150, 150, 150))
            self.screen.blit(inst_text, (10, 230))
            alt_text = self.font_small.render("Alt+A to open menu anytime", True, (150, 150, 150))
            self.screen.blit(alt_text, (10, 245))

        self.frame += 1
        pygame.display.update()

    def keep_on_top(self):
        """Ensure the overlay stays topmost on Windows"""
        try:
            import win32con, win32gui
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
        except Exception:
            pass

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
