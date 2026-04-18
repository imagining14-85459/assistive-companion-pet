import subprocess
import time
import sys
import os
import webbrowser
import json

def main():
    """Launch both Flask web dashboard and desktop overlay"""
    print("Starting Aether Assistant...")
    print("Hybrid Architecture: Web Dashboard + Desktop Overlay")
    print(f"Using Python: {sys.executable}")
    
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    
    # Start Flask app in a separate process
    print("\nStarting Web Dashboard on http://localhost:5000...")
    try:
        flask_process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=script_dir,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Flask process started")
    except Exception as e:
        print(f"Failed to start Flask: {e}")
        return
    
    # Give Flask time to start
    time.sleep(2)
    
    # Check if Flask is running
    if flask_process.poll() is None:
        print("Flask is running")
    else:
        stdout, stderr = flask_process.communicate()
        print(f"Flask failed to start:")
        print(f"stdout: {stdout.decode()}")
        print(f"stderr: {stderr.decode()}")
        return
    
    # Open web browser to dashboard
    try:
        webbrowser.open("http://localhost:5000")
        print("Dashboard opened in browser")
    except:
        print("Could not open browser. Visit http://localhost:5000 manually")
    
    # Start overlay (only if enabled)
    data = {}
    try:
        with open("pet_data.json", "r") as f:
            data = json.load(f)
    except:
        pass
    
    overlay_enabled = data.get('overlay_enabled', True)
    
    if overlay_enabled:
        print("\nStarting Desktop Overlay...")
        try:
            overlay_process = subprocess.Popen(
                [sys.executable, "main_overlay.py"],
                cwd=script_dir,
                env=os.environ.copy()
                # Removed stdout/stderr pipes to prevent blocking
            )
            print("Overlay process started")
            
            # Give it a moment to initialize
            time.sleep(1)
            
            # Check if overlay is still running
            if overlay_process.poll() is None:
                print("Overlay is running. Copy text to see the menu!")
            else:
                print("Overlay failed to start (process exited early)")
                return
                
        except Exception as e:
            print(f"Failed to start overlay: {e}")
            return
    else:
        print("\nDesktop Overlay disabled (can be enabled in dashboard)")
        overlay_process = None
    
    print("\nAether Assistant is running!")
    print("Web Dashboard: http://localhost:5000")
    if overlay_enabled:
        print("Desktop Overlay: Active on screen")
        print("Copy text to trigger AI study prompts")
    else:
        print("Desktop Overlay: Disabled")
    
    try:
        # Keep main process alive
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if flask_process.poll() is not None:
                print("Flask process died")
                break
            if overlay_enabled and overlay_process and overlay_process.poll() is not None:
                print("Overlay process died, restarting...")
                try:
                    overlay_process = subprocess.Popen(
                        [sys.executable, "main_overlay.py"],
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                except Exception as e:
                    print(f"Failed to restart overlay: {e}")
                    overlay_process = None
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        try:
            flask_process.terminate()
            if overlay_process:
                overlay_process.terminate()
            print("Processes terminated")
        except:
            pass

if __name__ == "__main__":
    main()
