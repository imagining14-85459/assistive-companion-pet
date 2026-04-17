import subprocess
import time
import sys
import os
import webbrowser

import pygame


def main():
    """Launch both Flask web dashboard and desktop overlay"""
    print("🐾 Starting Aether Assistant...")
    print("📚 Hybrid Architecture: Web Dashboard + Desktop Overlay")
    
    # Start Flask app in a separate process
    print("\n🌐 Starting Web Dashboard on http://localhost:5000...")
    flask_process = subprocess.Popen([sys.executable, "app.py"])
    
    # Give Flask time to start
    time.sleep(2)
    
    # Open web browser to dashboard
    try:
        webbrowser.open("http://localhost:5000")
        print("✅ Dashboard opened in browser")
    except:
        print("⚠️  Could not open browser. Visit http://localhost:5000 manually")
    
    # Start overlay
    print("\n🐾 Starting Desktop Overlay...")
    try:
        overlay_process = subprocess.Popen([sys.executable, "main_overlay.py"])
        print("✅ Overlay started. Copy text to see the menu!")
        
        # Wait for overlay to finish
        overlay_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Cleanup
        flask_process.terminate()
        overlay_process.terminate()
        print("✅ Aether Assistant closed")

if __name__ == "__main__":
    main()
    pygame.quit()
