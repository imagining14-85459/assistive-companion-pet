import pygame
import json
import subprocess
import time
from pet_ui import PetUI
from pet_brain import PetBrain

def main():
    ui = PetUI()
    brain = PetBrain()
    clock = pygame.time.Clock()
    
    # Secret Code Tracker
    input_buffer = ""
    
    running = True
    while running:
        with open("pet_data.json", "r") as f: data = json.load(f)
        
        is_focused = brain.is_focusing()
        
        # Reward Logic
        if is_focused:
            data["currency"] += 0.02
            data["xp"] += 0.05
            # Level Up Logic (based on your script.js)
            if data["xp"] >= (data["level"] * 100):
                data["level"] += 1
                data["xp"] = 0
        
        with open("pet_data.json", "w") as f: json.dump(data, f)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                # Secret Code "posturegod"
                input_buffer += event.unicode
                if "posturegod" in input_buffer:
                    data["currency"] += 1000
                    input_buffer = ""
                
                if event.key == pygame.K_m: # M key opens Dashboard
                    subprocess.Popen(["python", "dashboard.py"])
                
                if event.key == pygame.K_SPACE: # SPACE key asks AI
                    print("AI is reading screen...")
                    res = brain.study_the_screen("Simplify what is on my screen.")
                    print(f"PET: {res}")

        ui.draw("focused" if is_focused else "distracted", data.get("equipped_hat"))
        clock.tick(30)

    brain.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
