import subprocess
import time
import sys
import os
import webbrowser

def main():
    """Launch both Flask web dashboard and desktop overlay"""
    print("🐾 Starting Aether Assistant...")
    print("📚 Hybrid Architecture: Web Dashboard + Desktop Overlay")
    
    port = 5001 if sys.platform == "darwin" else 5000

    print(f"\n🌐 Starting Web Dashboard on http://localhost:{port}...")
    flask_process = subprocess.Popen([sys.executable, "app.py"])

    time.sleep(2)

    try:
        webbrowser.open(f"http://localhost:{port}")
        print("✅ Dashboard opened in browser")
    except:
        print(f"⚠️  Could not open browser. Visit http://localhost:{port} manually")
    
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

if __name__ == "__main__":
    main()
