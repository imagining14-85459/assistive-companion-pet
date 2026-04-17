import pygame
import json
import subprocess
import time
import winsound
from pet_ui import PetUI
from pet_brain import PetBrain

def play_alert_sound(alert_type="focus_lost"):
    """Play system alert sounds (Focus mode only)"""
    try:
        if alert_type == "focus_lost":
            winsound.Beep(800, 200)  # 800 Hz for 200ms
        elif alert_type == "focus_regained":
            winsound.Beep(600, 100)  # 600 Hz for 100ms
    except Exception as e:
        print(f"Sound error: {e}")

def main():
    # Load initial data to get mode
    with open("pet_data.json", "r") as f: 
        data = json.load(f)
    mode = data.get("mode", "default")
    
    ui = PetUI()
    brain = PetBrain(mode=mode)
    clock = pygame.time.Clock()
    
    # Secret Code Tracker
    input_buffer = ""
    
    # Study Session Tracker
    session_start = time.time()
    frame_count = 0
    
    # Focus state tracking (for Focus mode alerts)
    was_focused = True
    focus_alert_cooldown = 0
    
    running = True
    while running:
        frame_count += 1
        with open("pet_data.json", "r") as f: data = json.load(f)
        
        # Check current focus state
        is_focused = brain.is_focusing()
        
        # Reward Logic - Earn XP/Currency based on mode
        if mode == "focus":
            # In Focus mode, only reward when focused
            if is_focused:
                data["currency"] += 0.02
                data["xp"] += 0.05
            
            # Alert on focus loss (with cooldown to avoid spam)
            if not is_focused and was_focused and focus_alert_cooldown == 0:
                play_alert_sound("focus_lost")
                print("⚠️ Focus lost! Get back to it! 📚")
                focus_alert_cooldown = 60  # 2 second cooldown at 30 FPS
            elif is_focused and not was_focused:
                play_alert_sound("focus_regained")
                print("✅ Great! Back on track! 🎯")
                focus_alert_cooldown = 0
        else:
            # In Default mode, always earn currency (no focus requirement)
            data["currency"] += 0.01
            data["xp"] += 0.05
        
        # Decrease cooldown
        if focus_alert_cooldown > 0:
            focus_alert_cooldown -= 1
        
        was_focused = is_focused
        
        # Level Up Logic
        if data["xp"] >= (data["level"] * 100):
            data["level"] += 1
            data["xp"] = 0
        
        # Track study session time
        current_session_time = time.time() - session_start
        data["current_session_time"] = current_session_time
        
        with open("pet_data.json", "w") as f: json.dump(data, f)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                # End session, save session stats
                data["last_session_duration"] = current_session_time
                if "total_study_time" not in data:
                    data["total_study_time"] = 0
                data["total_study_time"] += current_session_time
                with open("pet_data.json", "w") as f: json.dump(data, f)
                running = False
                
            if event.type == pygame.KEYDOWN:
                # Secret Code "posturegod"
                input_buffer += event.unicode
                if "posturegod" in input_buffer:
                    data["currency"] += 1000
                    input_buffer = ""
                
                if event.key == pygame.K_m: # M key opens Dashboard
                    subprocess.Popen(["python", "dashboard.py"])
                
                if event.key == pygame.K_f: # F key - Toggle Focus/Default mode
                    if mode == "default":
                        mode = "focus"
                        brain = PetBrain(mode="focus")
                        print("🎯 Switched to FOCUS mode (focus detection ON)")
                    else:
                        mode = "default"
                        brain = PetBrain(mode="default")
                        print("📚 Switched to DEFAULT mode (focus detection OFF)")
                    data["mode"] = mode
                    with open("pet_data.json", "w") as f: json.dump(data, f)
                
                if event.key == pygame.K_SPACE: # SPACE key asks AI
                    print("📚 AI is analyzing your screen...")
                    res = brain.study_the_screen("Simplify what is on my screen.")
                    print(f"🐾 PET: {res}")
                
                if event.key == pygame.K_t: # T key - Text to Speech
                    print("🔊 Reading screen content aloud...")
                    res = brain.study_the_screen("Simplify what is on my screen for accessibility.")
                    brain.text_to_speech(res)
                    print(f"🐾 PET (spoken): {res}")
                
                if event.key == pygame.K_l: # L key - Translate for ESL
                    print("🌍 Translating screen content...")
                    res = brain.study_the_screen("Simplify what is on my screen.")
                    translated = brain.translate_text(res, target_language='es')
                    print(f"🐾 PET (Spanish): {translated}")

        ui.draw(data.get("equipped_hat"))
        clock.tick(30)

    brain.stop()
    pygame.quit()

if __name__ == "__main__":
    main()

