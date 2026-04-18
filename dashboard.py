import pygame
import json
import os

class Dashboard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 500))
        pygame.display.set_caption("Bit & Bite Dashboard")
        self.font = pygame.font.SysFont("Verdana", 18)
        
    def run(self):
        running = True
        msg = ""
        while running:
            with open("pet_data.json", "r") as f: data = json.load(f)
            self.screen.fill((30, 33, 40))
            
            # Stats Display
            lvl_txt = self.font.render(f"LVL {data['level']} | Coins: ${int(data['currency'])}", True, (255,255,255))
            self.screen.blit(lvl_txt, (20, 20))
            
            # Shop Button
            hat_btn = pygame.draw.rect(self.screen, (70, 80, 200), (20, 100, 360, 50), border_radius=10)
            self.screen.blit(self.font.render("Buy Top Hat - $150", True, (255,255,255)), (40, 115))

            # Display currency
            coins_txt = self.font.render(f"Coins: ${int(data['currency'])}", True, (255, 215, 0))
            coins_rect = coins_txt.get_rect(topright=(380, 20)) 
            self.screen.blit(coins_txt, coins_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEBUTTONDOWN and hat_btn.collidepoint(event.pos):
                    if data["currency"] >= 150:
                        data["currency"] -= 150
                        data["equipped_hat"] = "Top Hat"
                        with open("pet_data.json", "w") as f: json.dump(data, f)
            
            pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    Dashboard().run()
