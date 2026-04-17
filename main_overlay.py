import pygame
import json
import time
import pyautogui
import threading
from pet_ui import PetUI
from pet_brain import PetBrain
from pet_body import Pet
def main():
    """Lightweight desktop overlay with clipboard monitoring"""
    ui = PetUI(size = pyautogui.size())
    brain = PetBrain(mode="default")  # Default mode for overlay
    clock = pygame.time.Clock()
    pet = Pet(pyautogui.size()[0]/2, pyautogui.size()[1]/2, 10)
    # Clipboard monitoring
    last_clipboard_check = 0
    clipboard_check_interval = 0.5  # Check every 0.5 seconds
    
    # Study Session Tracker
    session_start = time.time()
    
    running = True
    while running:
        current_time = time.time()
        
        # Check clipboard periodically
        if current_time - last_clipboard_check >= clipboard_check_interval:
            last_clipboard_check = current_time
            clipboard_text = brain.check_clipboard()
            
            if clipboard_text:
                # Text copied! Show menu
                ui.toggle_menu(True)
                print(f"📋 Copied text: {clipboard_text[:50]}...")
        current_destination = pyautogui.position() # TODO: right now it just follows, change to move cmd
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
                    pass

        # Movement logic
        if abs(current_destination[0] - pet.x) > pet.size*1.5 or abs(current_destination[1] - pet.y) > pet.size*1.5:
            pet.take_step(current_destination[0], current_destination[1])

        # Load pet data for stats/cosmetics
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
        except:
            data = {}
        
        # Draw pet overlay
        ui.draw(pet, data.get("equipped_hat"))
        
        clock.tick(30)  # 30 FPS
    
    brain.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
