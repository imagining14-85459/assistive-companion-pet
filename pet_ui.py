import pygame
import win32api, win32con, win32gui

class PetUI:
    def __init__(self, size=(200, 200)):
        pygame.init()
        self.size = size
        self.trans_color = (255, 0, 128) # Fuchsia background
        self.screen = pygame.display.set_mode(size, pygame.NOFRAME)
        
        # Transparent Overlay Logic
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.trans_color), 0, win32con.LWA_COLORKEY)

    def draw(self, state, hat=None):
        self.screen.fill(self.trans_color)
        color = (150, 255, 150) if state == "focused" else (255, 150, 150)
        
        # Draw Pet (You can replace these with self.screen.blit for PNG images)
        pygame.draw.circle(self.screen, color, (100, 110), 60) # Body
        pygame.draw.circle(self.screen, (0,0,0), (80, 100), 5) # Eye L
        pygame.draw.circle(self.screen, (120, 100), (120, 100), 5) # Eye R
        
        if hat == "Top Hat":
            pygame.draw.rect(self.screen, (40, 40, 40), (70, 40, 60, 25))
            pygame.draw.rect(self.screen, (10, 10, 10), (60, 65, 80, 5))

        pygame.display.update()
