import pygame
import json
import time
import threading
import socket
from pet_ui import PetUI
from pet_brain import PetBrain

def create_brain(mode="default"):
    try:
        return PetBrain(mode=mode)
    except Exception as e:
        print(f"⚠️ Failed to initialize PetBrain ({mode}): {e}")
        return None


def safe_bionic_reading(text):
    words = text.split()
    bionic_text = []
    for word in words:
        if len(word) <= 2:
            bionic_text.append(f"**{word}**")
        else:
            bionic_text.append(f"**{word[:2]}**{word[2:]}")
    return " ".join(bionic_text)


def main():
    """Lightweight desktop overlay with clipboard monitoring"""
    ui = PetUI()
    brain = create_brain(mode="default")
    if brain is None:
        print("⚠️ AI engine unavailable, running overlay in offline mode.")
    
    clock = pygame.time.Clock()
    
    # Clipboard monitoring
    last_clipboard_check = 0
    clipboard_check_interval = 0.5  # Check every 0.5 seconds
    current_clipboard_text = None
    
    def start_ai_task(label, task_fn):
        ui.show_loading(label)
        def worker():
            nonlocal brain
            try:
                if brain is None:
                    brain = create_brain(mode="default")
                if brain is None:
                    raise RuntimeError("AI unavailable. Check your configuration.")
                result = task_fn(brain)
            except Exception as e:
                result = f"❌ {label} failed: {str(e)}"
                print(result)
                if brain:
                    brain.stop()
                brain = create_brain(mode="default")
            print(f"✅ {label} completed")
            ui.show_speech_bubble(result, duration=10)
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
                data_chunks = []
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data_chunks.append(chunk)
                data = b''.join(data_chunks).decode('utf-8')
                if data:
                    print(f"Received IPC message: {data[:50]}...")
                    ui.show_speech_bubble(data, duration=10)
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
    ui.show_speech_bubble("Hello! I'm your AI study assistant. Copy some text and click me to access AI tools!", duration=5)
    
    # Focus monitoring
    focus_check_interval = 2.0  # Check focus every 2 seconds
    last_focus_check = 0
    was_focusing = True  # Assume initially focused
    focus_alert_cooldown = 0  # Prevent spam alerts
    
    running = True
    dragging = False
    drag_moved = False
    while running:
        current_time = time.time()
        
        # Check clipboard periodically
        if current_time - last_clipboard_check >= clipboard_check_interval:
            last_clipboard_check = current_time
            new_clipboard_text = brain.check_clipboard() if brain else None
            
            if new_clipboard_text:
                current_clipboard_text = new_clipboard_text
                ui.toggle_menu(True)
                print(f"📋 Copied text: {current_clipboard_text[:50]}...")
        
        # Check focus status periodically (Focus mode only)
        current_time = time.time()
        if current_time - last_focus_check >= focus_check_interval:
            last_focus_check = current_time
            
            # Load current mode
            try:
                with open("pet_data.json", "r") as f:
                    data = json.load(f)
                mode = data.get("mode", "default")
            except:
                mode = "default"
            
            if mode == "focus":
                is_focusing_now = brain.is_focusing() if brain else True
                
                # Alert when focus is lost (but not too frequently)
                if was_focusing and not is_focusing_now and current_time > focus_alert_cooldown:
                    ui.show_speech_bubble("⚠️ Focus lost! Look back at the screen to maintain focus mode.", duration=4)
                    focus_alert_cooldown = current_time + 10  # Don't alert again for 10 seconds
                    print("⚠️ Focus lost - user not looking at screen")
                
                # Alert when focus is regained
                elif not was_focusing and is_focusing_now:
                    ui.show_speech_bubble("✅ Focus regained! Keep studying!", duration=3)
                    print("✅ Focus regained")
                
                was_focusing = is_focusing_now
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Mouse click detection for pet interaction and drag support
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pet_center_x, pet_center_y = 125, 110
                distance = ((mouse_x - pet_center_x) ** 2 + (mouse_y - pet_center_y) ** 2) ** 0.5
                if distance < 80:  # Pet radius + some margin
                    dragging = ui.begin_drag()
                    drag_moved = False
                    if dragging:
                        print("🐾 Started dragging pet overlay.")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    if not drag_moved:
                        ui.toggle_menu()
                        print("🐾 Pet clicked! AI tools menu toggled.")
                    dragging = False
                    ui.end_drag()
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    ui.drag_to()
                    drag_moved = True
            
            # Mouse wheel for speech bubble scrolling
            if event.type == pygame.MOUSEWHEEL and ui.is_speech_bubble_active():
                # Calculate how many lines to scroll
                scroll_amount = -event.y  # Negative because pygame wheel is inverted
                max_scroll = max(0, len(ui._get_wrapped_lines()) - ui.max_visible_lines)
                ui.speech_scroll_offset = max(0, min(max_scroll, ui.speech_scroll_offset + scroll_amount))
                print(f"📜 Scrolled speech bubble to offset {ui.speech_scroll_offset}")
            
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
                                if not current_clipboard_text:
                                    import pyperclip
                                    current_clipboard_text = pyperclip.paste()
                                    if not current_clipboard_text or not current_clipboard_text.strip():
                                        print("⚠ No text in clipboard")
                                        ui.show_speech_bubble("Please copy some text first!", duration=3)
                                        ui.toggle_translate_menu(False)
                                        continue
                                
                                target_language = language_option['language']
                                print(f"🤖 Translating to {target_language}...")
                                
                                try:
                                    clipboard_input = current_clipboard_text
                                    start_ai_task(f"Translating to {target_language}...", lambda b: b.analyze_clipboard_text(clipboard_input, 'translate', target_language))
                                except Exception as e:
                                    error_msg = f"Translation error: {str(e)[:100]}"
                                    print(f"❌ {error_msg}")
                                    ui.show_speech_bubble(error_msg, duration=5)
                            
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
                                    start_ai_task("Analyzing screen...", lambda b: b.study_the_screen("Explain this study material for a student with ADHD."))
                                else:
                                    # Check if clipboard is required
                                    requires_clipboard = option.get('requires_clipboard', True)
                                    if requires_clipboard and not current_clipboard_text:
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
                                        response = brain.bionic_reading(clipboard_input) if brain else safe_bionic_reading(clipboard_input)
                                        print(f"✨ Bionic format:\n{response[:100]}...")
                                        ui.show_speech_bubble(response, duration=10)
                                    else:
                                        start_ai_task(f"Running {option['label']}...", lambda b: b.analyze_clipboard_text(clipboard_input, intent))
                        elif event.key == pygame.K_ESCAPE:
                            ui.toggle_menu(False)
                
                # Global hotkeys
                if event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                    # Ctrl+C - Already handled by OS, but we can trigger menu
                    pass
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_ALT:
                    # Alt+A - Show AI tools menu
                    ui.toggle_menu(True)
                    print("🎯 Alt+A pressed - AI tools menu activated")
                elif event.key == pygame.K_ESCAPE and ui.show_menu:
                    # ESC - Close menu
                    ui.toggle_menu(False)
                    print("❌ Menu closed with ESC")
        
        # Load pet data for stats/cosmetics
        try:
            with open("pet_data.json", "r") as f:
                data = json.load(f)
        except:
            data = {}
        
        # Hide/show overlay based on enabled state
        overlay_enabled = data.get("overlay_enabled", True)
        if not overlay_enabled:
            # Hide the window when disabled
            if ui.hwnd:
                try:
                    import win32con, win32gui
                    win32gui.ShowWindow(ui.hwnd, win32con.SW_HIDE)
                except:
                    pass
            pygame.time.wait(100)  # Small delay to prevent busy waiting
            continue
        else:
            # Show the window when enabled
            if ui.hwnd:
                try:
                    import win32con, win32gui
                    win32gui.ShowWindow(ui.hwnd, win32con.SW_SHOW)
                except:
                    pass
        
        # If the dashboard has been fully closed and the overlay is enabled, shut down the desktop pet.
        last_seen = data.get('dashboard_last_seen', 0)
        dashboard_closed = data.get('dashboard_tab_count', 0) <= 0
        if overlay_enabled and dashboard_closed and last_seen > 0:
            ui.show_speech_bubble("Dashboard window closed. Ending desktop pet.", duration=3)
            print("🏁 Dashboard window closed, shutting down overlay.")
            break
        
        # Synchronize focus mode with the background brain
        current_mode = data.get("mode", "default")
        if brain is None or current_mode != getattr(brain, 'mode', None):
            if brain:
                brain.stop()
            brain = create_brain(mode=current_mode)
        
        # Draw pet overlay
        focus_indicator = "lost" if (data.get("mode", "default") == "focus" and not was_focusing) else None
        ui.draw(data.get("equipped_hat"), focus_indicator)
        
        clock.tick(30)  # 30 FPS
    
    brain.stop()
    try:
        pygame.quit()
    except NameError:
        # pygame might not be defined if import failed
        pass

if __name__ == "__main__":
    main()
