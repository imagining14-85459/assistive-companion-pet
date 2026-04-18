import pygame
import json
import time
import pyautogui
import threading
import random
from pet_ui import PetUI
from pet_brain import PetBrain
from pet_body import Pet
def main():
    """Lightweight desktop overlay with clipboard monitoring"""
    # Load pet data for stats/cosmetics
    try:
        with open("pet_data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        with open("default_pet_info.json", "r") as f:
            data=json.load(f)
            with open("pet_data.json", "w") as g:
                json.dump(data, g)

    ui = PetUI(size = pyautogui.size())
    brain = PetBrain(mode="default")  # Default mode for overlay
    clock = pygame.time.Clock()

    pet = Pet(pyautogui.size()[0]/2, pyautogui.size()[1]/2, 10, data["equipped_hat"])
    # Clipboard monitoring

    # Study Session Tracker
    session_start = time.time()

    running = True
    current_destination = pyautogui.position()
    idle = 0
    prev_mouse_pos = pyautogui.position()
    while running:
        # Update pet data for stats/cosmetics
        with open("pet_data.json", "r") as f: # updates json data
            data = json.load(f)
        current_time = time.time()
        if prev_mouse_pos == pyautogui.position():
            idle += 1
        else:
            prev_mouse_pos = pyautogui.position()
            idle = 0
        if idle > 30 * 10:
            pet.state = "follow"
            ui.show_speech_bubble("Give me attention!", 5)

        if pet.state == "follow":
            current_destination = pyautogui.position()
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION and pet.held_down:
                current_destination = pyautogui.position()
                dx,dy = event.rel
                pet.speed = (dx**2 + dy**2)**0.5
                pet.take_step(current_destination[0], current_destination[1])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pet.collide(event.pos): # Pet is clicked on
                    pet.held_down = True
                    if event.button == 1:
                        r_greeting = random.choice(["Hello!", "Hey!", "Stop..."])
                        ui.show_speech_bubble(r_greeting, 3)
                    # Additional left click events
                    if event.button == 3:
                        ui.toggle_menu()

            if event.type == pygame.MOUSEBUTTONUP:
                if pet.held_down: # lets the pet go
                    pet.held_down = False
                    pet.speed = 10
                    current_destination = pyautogui.position()
                    pet.state = "stay"

            if event.type == pygame.KEYDOWN:
                # Menu navigation
                if ui.show_menu:
                    if event.key == pygame.K_UP:
                        ui.selected_option = (ui.selected_option - 1) % len(ui.menu_options)
                    elif event.key == pygame.K_DOWN:
                        ui.selected_option = (ui.selected_option + 1) % len(ui.menu_options)
                    elif event.key == pygame.K_RETURN:
                        # Execute selected action
                        option = ui.select_menu_option()
                        if option:
                            clipboard_text = brain.check_clipboard()
                            if not clipboard_text:
                                # Restore from last copied text
                                import pyperclip
                                clipboard_text = pyperclip.paste()
                            
                            intent = option['intent']
                            print(f"🤖 Processing with '{intent}' intent...")
                            
                            # Get AI response
                            if intent == "bionic":
                                response = brain.bionic_reading(clipboard_text)
                                print(f"✨ Bionic format:\n{response[:100]}...")
                            else:
                                response = brain.analyze_clipboard_text(clipboard_text, intent)
                                print(f"🐾 {option['label']}:\n{response[:100]}...")
                            
                            # Show response in speech bubble
                            ui.show_speech_bubble(response, duration=8)
                            
                            # Also read aloud if not bionic
                            if intent != "bionic":
                                brain.text_to_speech(response)
                        
                        ui.toggle_menu(False)
                    elif event.key == pygame.K_ESCAPE:
                        ui.toggle_menu(False)
                
                # Global hotkeys
                if event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                    # Ctrl+C - Already handled by OS, but we can trigger menu
                    clipboard_text = brain.check_clipboard()
                    if clipboard_text:
                        # Text copied! Show menu
                        ui.toggle_menu(True)
                        print(f"📋 Copied text: {clipboard_text[:50]}...")

        # Movement logic
        if abs(current_destination[0] - pet.x) > pet.size or abs(current_destination[1] - pet.y) > pet.size:
            pet.take_step(current_destination[0], current_destination[1])
        
        # Draw pet overlay
        ui.draw(pet)

        clock.tick(30)  # 30 FPS
    
    brain.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
