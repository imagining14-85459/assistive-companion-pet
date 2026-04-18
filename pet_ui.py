import pygame
import win32api, win32con, win32gui
import math
import json
import time
from pet_body import Pet

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
            self.window_position = (window_x, window_y)
            print(f"✓ Transparent overlay enabled at ({window_x}, {window_y})")
        except ImportError:
            print("⚠ pywin32 not available - using solid window")
            self.transparent = False
            self.window_position = (0, 0)
            # For solid mode, just keep the NOFRAME window as is
        
        self.dragging = False
        self.drag_start_screen = (0, 0)
        self.drag_origin = (0, 0)
        
        # Animation tracking
        self.frame = 0
        self.font_small = pygame.font.SysFont("Arial", 9)
        self.font_medium = pygame.font.SysFont("Arial", 11)
        
        # Pet sprite
        self.pet = Pet(125, 110, 0)  # No movement speed
        
        # Speech bubble state
        self.speech_bubble_text = ""
        self.speech_bubble_time = 0
        self.speech_bubble_duration = 5  # seconds
        self.is_loading = False
        self.loading_text = ""
        self.speech_scroll_offset = 0  # For scrolling long text
        self.max_visible_lines = 8  # Maximum lines visible in scrollable area
        
        # Bubble resizing
        self.bubble_width = 310  # Default width
        self.bubble_height = 200  # Default height
        self.bubble_x = 0  # Current bubble position
        self.bubble_y = 0  # Current bubble position
        self.resizing = False
        self.resize_handle_size = 10  # Size of resize handles
        self.load_bubble_size()  # Load saved bubble dimensions
        
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
            {'key': '4', 'label': 'Italian', 'language': 'Italian'},
            {'key': '5', 'label': 'Portuguese', 'language': 'Portuguese'},
            {'key': '6', 'label': 'Chinese', 'language': 'Simplified Chinese'},
            {'key': '7', 'label': 'Japanese', 'language': 'Japanese'},
            {'key': '8', 'label': 'Korean', 'language': 'Korean'},
            {'key': '9', 'label': 'Russian', 'language': 'Russian'},
            {'key': '0', 'label': 'Arabic', 'language': 'Arabic'},
        ]
    def _get_wrapped_lines(self):
        """Get wrapped lines for current speech bubble text"""
        if not self.speech_bubble_text:
            return []
        
        # Load font size
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            font_size = data.get('font_size', 11)
        except:
            font_size = 11
        
        speech_font = pygame.font.SysFont("Arial", font_size)
        max_width = 280
        
        words = self.speech_bubble_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if speech_font.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        return lines

    def show_speech_bubble(self, text, duration=5):
        """Display AI response as a speech bubble"""
        print(f"🗯️ Showing speech bubble: '{text[:50]}...' for {duration}s")
        self.speech_bubble_text = text
        self.speech_bubble_time = time.time()
        self.speech_bubble_duration = duration
        self.speech_scroll_offset = 0  # Reset scroll when showing new text
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

    def set_window_position(self, x, y):
        """Move overlay window to a new screen position."""
        self.window_position = (int(x), int(y))
        if self.hwnd:
            try:
                win32gui.SetWindowPos(
                    self.hwnd,
                    win32con.HWND_TOPMOST,
                    int(x),
                    int(y),
                    0,
                    0,
                    win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
                )
            except Exception:
                pass

    def begin_drag(self):
        """Start moving the overlay window."""
        if not self.hwnd:
            return False
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            self.drag_origin = (rect[0], rect[1])
            self.drag_start_screen = win32gui.GetCursorPos()
            self.dragging = True
            print(f"🐾 Drag started at cursor: {self.drag_start_screen}, window at: {self.drag_origin}")
            return True
        except Exception as e:
            print(f"Error starting drag: {e}")
            return False

    def drag_to(self):
        """Move the overlay window while dragging."""
        if not self.dragging or not self.hwnd:
            return
        try:
            cursor_pos = win32gui.GetCursorPos()
            dx = cursor_pos[0] - self.drag_start_screen[0]
            dy = cursor_pos[1] - self.drag_start_screen[1]
            new_x = self.drag_origin[0] + dx
            new_y = self.drag_origin[1] + dy
            
            # Add bounds checking to keep window on screen
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            
            # Clamp position to keep window visible
            new_x = max(0, min(new_x, screen_width - self.size[0]))
            new_y = max(0, min(new_y, screen_height - self.size[1]))
            
            self.set_window_position(new_x, new_y)
        except Exception as e:
            print(f"Error during drag: {e}")

    def end_drag(self):
        """Stop moving the overlay window."""
        self.dragging = False

    def load_bubble_size(self):
        """Load saved bubble dimensions from pet_data.json"""
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            self.bubble_width = data.get("bubble_width", 310)
            self.bubble_height = data.get("bubble_height", 200)
        except:
            self.bubble_width = 310
            self.bubble_height = 200

    def save_bubble_size(self):
        """Save bubble dimensions to pet_data.json"""
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
        except:
            data = {}
        
        data["bubble_width"] = self.bubble_width
        data["bubble_height"] = self.bubble_height
        
        try:
            with open("pet_data.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving bubble size: {e}")

    def begin_bubble_resize(self, mouse_x, mouse_y):
        """Start resizing the bubble from the given handle"""
        if self.resizing:
            return None
        
        # Check which handle was clicked
        handle_bottom_right = (self.bubble_x + self.bubble_width - self.resize_handle_size, 
                               self.bubble_y + self.bubble_height - self.resize_handle_size)
        handle_rect = pygame.Rect(handle_bottom_right[0], handle_bottom_right[1], 
                                  self.resize_handle_size, self.resize_handle_size)
        
        if handle_rect.collidepoint(mouse_x, mouse_y):
            self.resizing = True
            self.resize_start = (mouse_x, mouse_y)
            return True
        return False

    def resize_bubble(self, mouse_x, mouse_y):
        """Resize the bubble based on mouse movement"""
        if not self.resizing:
            return
        
        dx = mouse_x - self.resize_start[0]
        dy = mouse_y - self.resize_start[1]
        
        # Update bubble size with minimum constraints
        new_width = max(150, self.bubble_width + dx)
        new_height = max(100, self.bubble_height + dy)
        
        # Keep bubble within bounds
        screen_width, screen_height = self.size
        max_width = screen_width - self.bubble_x - 10
        max_height = screen_height - self.bubble_y - 10
        
        self.bubble_width = min(new_width, max_width)
        self.bubble_height = min(new_height, max_height)
        self.resize_start = (mouse_x, mouse_y)

    def end_bubble_resize(self):
        """Stop resizing the bubble and save dimensions"""
        if self.resizing:
            self.resizing = False
            self.save_bubble_size()

    def is_bubble_resizable_region(self, mouse_x, mouse_y):
        """Check if the mouse is in the resize handle region"""
        if not self.is_speech_bubble_active():
            return False
        
        # Check the bottom-right corner resize handle
        handle_bottom_right = (self.bubble_x + self.bubble_width - self.resize_handle_size, 
                               self.bubble_y + self.bubble_height - self.resize_handle_size)
        handle_rect = pygame.Rect(handle_bottom_right[0], handle_bottom_right[1], 
                                  self.resize_handle_size, self.resize_handle_size)
        
        return handle_rect.collidepoint(mouse_x, mouse_y)
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
        """Draw the pet character using sprite"""
        # Update pet position for bouncing animation
        self.pet.y = body_y
        self.pet.update_rect()
        
        # Draw pet sprite
        self.screen.blit(self.pet.image, self.pet.rect.topleft)
        
        # Draw hat if equipped
        if self.pet.hat:
            self.screen.blit(self.pet.hat.image, self.pet.hat.rect.topleft)
        
        # Add "AI Pet" label
        label = self.font_medium.render("AI Pet", True, (0, 0, 0))
        self.screen.blit(label, (125 - label.get_width() // 2, int(body_y + 70)))

    def draw_speech_bubble(self):
        """Draw AI response speech bubble with scrolling and resizing"""
        if not self.is_speech_bubble_active():
            return
        
        print(f"🎨 Drawing speech bubble: '{self.speech_bubble_text[:30]}...'")
        
        # Load font size from pet data
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            font_size = data.get('font_size', 11)
        except:
            font_size = 11
        
        # Create font with dynamic size
        speech_font = pygame.font.SysFont("Arial", font_size)
        
        # Wrap text with better handling for long messages
        max_width = self.bubble_width - 40  # Account for padding
        words = self.speech_bubble_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if speech_font.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Calculate visible lines and scrolling
        line_height = font_size + 4
        total_lines = len(lines)
        calculated_visible = (self.bubble_height - 40) // line_height  # Account for padding
        visible_lines = min(calculated_visible, total_lines)
        visible_lines = max(1, visible_lines)  # Ensure at least 1 line
        
        # Position on the RIGHT side of the pet (not above)
        pet_center_x = 125
        self.bubble_x = pet_center_x + 80  # To the right of pet
        self.bubble_y = 60  # Aligned with pet body
        
        bubble_width = self.bubble_width
        bubble_height = self.bubble_height
        
        # Ensure bubble doesn't go off screen
        screen_width, screen_height = self.size
        if self.bubble_x + bubble_width > screen_width - 10:
            self.bubble_x = screen_width - bubble_width - 10
        if self.bubble_y + bubble_height > screen_height - 10:
            self.bubble_y = screen_height - bubble_height - 10
        
        # Bubble background
        pygame.draw.rect(self.screen, (255, 255, 200), (self.bubble_x, self.bubble_y, bubble_width, bubble_height), border_radius=8)
        pygame.draw.rect(self.screen, (0, 0, 0), (self.bubble_x, self.bubble_y, bubble_width, bubble_height), 2, border_radius=8)
        
        # Pointer from pet to bubble (pointing right)
        pointer_x = self.bubble_x
        pointer_y = self.bubble_y + bubble_height // 2
        pygame.draw.polygon(self.screen, (245, 230, 200), [(pointer_x, pointer_y), (pointer_x-8, pointer_y-8), (pointer_x-8, pointer_y+8)])
        pygame.draw.polygon(self.screen, (92, 54, 30), [(pointer_x, pointer_y), (pointer_x-8, pointer_y-8), (pointer_x-8, pointer_y+8)], 2)
        
        # Draw visible text lines with scrolling
        start_line = self.speech_scroll_offset
        end_line = min(start_line + visible_lines, total_lines)
        
        for i, line_idx in enumerate(range(start_line, end_line)):
            line = lines[line_idx]
            text_surf = speech_font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surf, (self.bubble_x + 15, self.bubble_y + 10 + i * line_height))
        
        # Draw scrollbar if needed
        if total_lines > visible_lines:
            scrollbar_width = 8
            scrollbar_x = self.bubble_x + bubble_width - scrollbar_width - 5
            scrollbar_height = bubble_height - 20
            scrollbar_y = self.bubble_y + 10
            
            # Scrollbar background
            pygame.draw.rect(self.screen, (200, 200, 200), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=4)
            
            # Scrollbar handle
            handle_height = max(20, scrollbar_height * visible_lines // total_lines)
            handle_y = scrollbar_y + (scrollbar_height - handle_height) * start_line // (total_lines - visible_lines)
            pygame.draw.rect(self.screen, (100, 100, 100), (scrollbar_x, handle_y, scrollbar_width, handle_height), border_radius=4)
        
        # Draw resize handle (bottom-right corner)
        handle_color = (150, 150, 255) if self.resizing else (200, 200, 200)
        handle_x = self.bubble_x + bubble_width - self.resize_handle_size
        handle_y = self.bubble_y + bubble_height - self.resize_handle_size
        pygame.draw.rect(self.screen, handle_color, (handle_x, handle_y, self.resize_handle_size, self.resize_handle_size))
        pygame.draw.polygon(self.screen, (100, 100, 100), [
            (handle_x + self.resize_handle_size, handle_y + self.resize_handle_size),
            (handle_x, handle_y + self.resize_handle_size),
            (handle_x + self.resize_handle_size, handle_y)
        ])

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
        
        # Update pet hat
        self.pet.update_hat(hat)
        
        # Load current mode
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            mode = data.get("mode", "default")
        except:
            mode = "default"
        
        # Pet color based on mode and focus status (not used with sprite, but keep for future)
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
        
        # Draw mode indicator emoji
        mode_text = "🎯" if mode == "focus" else "📚"
        mode_label = self.font_medium.render(mode_text, True, (255, 255, 255))
        self.screen.blit(mode_label, (10, 10))
        
        # Draw focus warning indicator if in focus mode and focus lost
        if mode == "focus" and focus_status == "lost":
            warning_text = "⚠️"
            warning_label = self.font_medium.render(warning_text, True, (255, 255, 0))
            self.screen.blit(warning_label, (10, 35))
        
        # Draw menu if active
        if self.show_menu:
            self.draw_menu()

        # Draw loading indicator if active
        self.draw_loading()

        # Draw speech bubble last so it stays visible above the menu
        self.draw_speech_bubble()
        
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
