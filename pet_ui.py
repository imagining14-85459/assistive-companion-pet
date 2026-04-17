import pygame
import win32api, win32con, win32gui
import math
import json

class PetUI:
    def __init__(self, size=(200, 200)):
        pygame.init()
        self.size = size
        self.trans_color = (255, 0, 128) # Fuchsia background
        self.screen = pygame.display.set_mode(size, pygame.NOFRAME)
        
        # Animation tracking
        self.frame = 0
        self.font = pygame.font.SysFont("Arial", 10)
        
        # Transparent Overlay Logic
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.trans_color), 0, win32con.LWA_COLORKEY)

    def draw(self, hat=None):
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
        body_y = 110 + bounce
        
        # Draw Pet (You can replace these with self.screen.blit for PNG images)
        pygame.draw.circle(self.screen, color, (100, int(body_y)), 60) # Body
        pygame.draw.circle(self.screen, (0, 0, 0), (80, int(body_y - 10)), 5) # Eye L
        pygame.draw.circle(self.screen, (0, 0, 0), (120, int(body_y - 10)), 5) # Eye R
        
        # Happy mouth (curved smile)
        pygame.draw.arc(self.screen, (0, 0, 0), (85, int(body_y + 5), 30, 20), 0, 3.14, 2)
        
        # Mode indicator text
        mode_text = "🎯" if mode == "focus" else "📚"
        mode_label = self.font.render(mode_text, True, (255, 255, 255))
        self.screen.blit(mode_label, (10, 10))
        
        if hat == "Top Hat":
            hat_y = 40 + bounce
            pygame.draw.rect(self.screen, (40, 40, 40), (70, int(hat_y), 60, 25))
            pygame.draw.rect(self.screen, (10, 10, 10), (60, int(hat_y + 25), 80, 5))

        self.frame += 1
        pygame.display.update()

