import pygame
import json
import time
import pyautogui
import threading
import random
import socket
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

    def start_ai_task(label, task_fn):
        ui.show_loading(label)
        def worker():
            try:
                result = task_fn()
            except Exception as e:
                result = f"❌ {label} failed: {str(e)}"
                print(result)
            print(f"✅ {label} completed")
            ui.pet_speaks(pet, result, duration=10)
        threading.Thread(target=worker, daemon=True).start()

    # IPC server for real-time AI results from dashboard
    def ipc_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('localhost', 5002))
            server.listen(1)
            print("IPC server listening on port 5002")
            while True:
                conn, addr = server.accept()
                d = conn.recv(1024).decode('utf-8')
                if d:
                    print(f"Received IPC message: {data[:50]}...")
                    ui.pet_speaks(pet, data, duration=10)
                conn.close()
        except Exception as e:
            print(f"IPC server error: {e}")
        finally:
            server.close()

    # Start IPC server thread
    ipc_thread = threading.Thread(target=ipc_server, daemon=True)
    ipc_thread.start()

    # Study Session Tracker
    session_start = time.time()

    # Show welcome message
    ui.pet_speaks(pet, "Hello! I'm your AI study assistant. Copy some text and click me to access AI tools!", duration=5)

    # Focus monitoring
    focus_check_interval = 2.0  # Check focus every 2 seconds
    last_focus_check = 0
    was_focusing = True  # Assume initially focused
    focus_alert_cooldown = 0  # Prevent spam alerts

    running = True
    current_destination = pyautogui.position()
    idle = 0
    prev_mouse_pos = current_destination
    while running:
        # Update pet data for stats/cosmetics
        try:
            with open("pet_data.json", "r") as f: # updates json data
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            # failed to open, skip for the frame
            pass
        pet.shown = data["overlay_enabled"]
        pet.update_hat(data["equipped_hat"])
        current_time = time.time()
        if prev_mouse_pos == pyautogui.position():
            idle += 1
        else:
            prev_mouse_pos = pyautogui.position()
            idle = 0
        if idle > 30 * 10:
            pet.state = "follow"
            ui.pet_speaks(pet, "Give me attention!", 5)

        if pet.state == "follow":
            current_destination = pyautogui.position()

        # load mode
        mode = data.get("mode", "default")
        is_focusing_now = None
        if mode == "focus":
            is_focusing_now = brain.is_focusing()
            # Alert when focus is lost (but not too frequently)
        if was_focusing and not is_focusing_now and current_time > focus_alert_cooldown:
            ui.pet_speaks(pet, "⚠️ Focus lost! Look back at the screen to maintain focus mode.", duration=4)
            focus_alert_cooldown = current_time + 10  # Don't alert again for 10 seconds
            print("⚠️ Focus lost - user not looking at screen")

        # Alert when focus is regained
        elif not was_focusing and is_focusing_now:
            ui.pet_speaks(pet, "✅ Focus regained! Keep studying!", duration=3)
            print("✅ Focus regained")

        was_focusing = is_focusing_now
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
                        ui.pet_speaks(pet,r_greeting, 3)
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
                    if ui.show_translate_menu:
                        # Navigate translate language menu
                        if event.key == pygame.K_UP:
                            ui.selected_option = (ui.selected_option - 1) % len(ui.translate_options)
                        elif event.key == pygame.K_DOWN:
                            ui.selected_option = (ui.selected_option + 1) % len(ui.translate_options)
                        elif event.key == pygame.K_RETURN:
                            # Execute translate with selected language
                            language_option = ui.select_translate_option()
                            if language_option:
                                # Get clipboard content if we don't have it
                                import pyperclip
                                current_clipboard_text = pyperclip.paste()
                                if not current_clipboard_text or not current_clipboard_text.strip():
                                    print("⚠ No text in clipboard")
                                    ui.pet_speaks(pet, "Please copy some text first!", duration=3)
                                    ui.toggle_translate_menu(False)
                                target_language = language_option['language']
                                print(f"🤖 Translating to {target_language}...")

                                try:
                                    clipboard_input = current_clipboard_text
                                    start_ai_task(f"Translating to {target_language}...", lambda: brain.analyze_clipboard_text(clipboard_input, 'translate', target_language))
                                except Exception as e:
                                    error_msg = f"Translation error: {str(e)[:100]}"
                                    print(f"❌ {error_msg}")
                                    ui.pet_speaks(pet, error_msg, duration=5)

                            ui.toggle_translate_menu(False)
                            # Keep main menu open after translation
                            # ui.toggle_menu(False)
                        elif event.key == pygame.K_ESCAPE:
                            ui.toggle_translate_menu(False)
                    else:
                        # Navigate main menu
                        if event.key == pygame.K_UP:
                            ui.selected_option = (ui.selected_option - 1) % len(ui.menu_options)
                        elif event.key == pygame.K_DOWN:
                            ui.selected_option = (ui.selected_option + 1) % len(ui.menu_options)
                        elif event.key == pygame.K_RETURN:
                            # Execute selected action
                            option = ui.select_menu_option()
                            if option:
                                if option['intent'] == 'translate':
                                    # Show translate language submenu
                                    ui.toggle_translate_menu(True)
                                elif option['intent'] == 'screen_study':
                                    # Study screen content
                                    print("🤖 Analyzing screen...")
                                    start_ai_task("Analyzing screen...", lambda: brain.study_the_screen("Explain this study material for a student with ADHD."))
                                else:
                                    # Check if clipboard is required
                                    requires_clipboard = option.get('requires_clipboard', True)
                                    if requires_clipboard:
                                        import pyperclip
                                        current_clipboard_text = pyperclip.paste()
                                        if not current_clipboard_text or not current_clipboard_text.strip():
                                            print("⚠ No text in clipboard")
                                            ui.show_speech_bubble("Please copy some text first!", duration=3)
                                            ui.toggle_menu(False)
                                            continue

                                    intent = option['intent']
                                    clipboard_input = current_clipboard_text
                                    print(f"🤖 Processing with '{intent}' intent...")

                                    if intent == "bionic":
                                        # Bionic reading is immediate and does not require AI thread
                                        response = brain.bionic_reading(clipboard_input)
                                        print(f"✨ Bionic format:\n{response[:100]}...")
                                        ui.show_speech_bubble(response, duration=10)
                                    else:
                                        start_ai_task(f"Running {option['label']}...", lambda: brain.analyze_clipboard_text(clipboard_input, intent))
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
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_ALT:
                    # Alt+A - Show AI tools menu
                    ui.toggle_menu(True)
                    print("🎯 Alt+A pressed - AI tools menu activated")
                elif event.key == pygame.K_ESCAPE and ui.show_menu:
                    # ESC - Close menu
                    ui.toggle_menu(False)
                    print("❌ Menu closed with ESC")

        # Movement logic
        if abs(current_destination[0] - pet.x) > pet.size or abs(current_destination[1] - pet.y) > pet.size:
            pet.take_step(current_destination[0], current_destination[1])

        # Synchronize focus mode with the background brain
        current_mode = data.get("mode", "default")
        if current_mode != brain.mode:
            brain.stop()
            try:
                brain = PetBrain(mode=current_mode)
            except Exception as e:
                print(f"⚠️ Failed to switch Brain mode: {e}")
                brain = PetBrain(mode="default")

        # Draw pet overlay
        ui.draw(pet)
        clock.tick(30)  # 30 FPS
    
    brain.stop()
    try:
        pygame.quit()
    except NameError:
        # pygame might not be defined if import failed
        pass

if __name__ == "__main__":
    main()
