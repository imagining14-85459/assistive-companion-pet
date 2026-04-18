import os
import pyautogui
import pyttsx3
import pyperclip
from dotenv import load_dotenv

# Gemini SDK (correct import for google-genai)
from google import genai

# Optional Focus Mode imports
try:
    import cv2
    import mediapipe as mp
    FOCUS_MODE_AVAILABLE = True
except ImportError:
    FOCUS_MODE_AVAILABLE = False


# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file")


class PetBrain:
    def __init__(self, mode="default"):
        self.mode = mode

        # Gemini client
        self.client = genai.Client(api_key=GEMINI_KEY)

        # Text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty("rate", 150)

        # Clipboard tracking
        self.last_clipboard_content = ""

        # Focus mode setup
        self.face_mesh = None
        self.cap = None
        self.last_seen = None

        if mode == "focus":
            if not FOCUS_MODE_AVAILABLE:
                raise ImportError(
                    "Focus mode requires opencv-python and mediapipe. "
                    "Run: pip install opencv-python mediapipe"
                )

            self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
            self.cap = cv2.VideoCapture(0)
            self.last_seen = __import__("time").time()

    # ----------------------------
    # Clipboard detection
    # ----------------------------
    def check_clipboard(self):
        try:
            current = pyperclip.paste()
            if current != self.last_clipboard_content and current.strip():
                self.last_clipboard_content = current
                return current
        except:
            pass
        return None

    # ----------------------------
    # Bionic reading
    # ----------------------------
    def bionic_reading(self, text):
        words = text.split()
        out = []

        for w in words:
            if len(w) <= 2:
                out.append(f"**{w}**")
            else:
                out.append(f"**{w[:2]}**{w[2:]}")

        return " ".join(out)

    # ----------------------------
    # Focus detection (optional)
    # ----------------------------
    def is_focusing(self):
        if self.mode != "focus" or not self.face_mesh:
            return True

        import time

        ret, frame = self.cap.read()
        if not ret:
            return False

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            self.last_seen = time.time()
            return True

        return (time.time() - self.last_seen) < 3

    # ----------------------------
    # Gemini helper (safe wrapper)
    # ----------------------------
    def _ask_gemini(self, prompt, image=None):
        try:
            if image:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, image],
                )
            else:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )

            return response.text
        except Exception as e:
            return f"[Gemini Error] {e}"

    # ----------------------------
    # Screen analysis
    # ----------------------------
    def study_the_screen(self, question="Explain this for an ADHD student."):
        screenshot_path = "study_session.png"
        pyautogui.screenshot(screenshot_path)

        return self._ask_gemini(question, screenshot_path)

    # ----------------------------
    # Clipboard AI tools
    # ----------------------------
    def analyze_clipboard_text(self, text, intent="simplify"):
        if intent == "bionic":
            return self.bionic_reading(text)

        if intent == "simplify":
            prompt = "Simplify this for a student with ADHD. Be clear and concise."
        elif intent == "translate":
            prompt = "Translate this to Spanish clearly and concisely."
        elif intent == "explain":
            prompt = "Explain this in simple terms."
        else:
            prompt = "Analyze this text and summarize it."

        return self._ask_gemini(f"{prompt}\n\nTEXT:\n{text}")

    # ----------------------------
    # Image explanation
    # ----------------------------
    def explain_image(self, image_path, question="What is this?"):
        return self._ask_gemini(question, image_path)

    # ----------------------------
    # TTS
    # ----------------------------
    def text_to_speech(self, text):
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print("TTS Error:", e)
            return False

    # ----------------------------
    # Translation
    # ----------------------------
    def translate_text(self, text, target_language="es"):
        prompt = f"Translate this to {target_language} concisely:\n{text}"
        return self._ask_gemini(prompt)

    # ----------------------------
    # Cleanup
    # ----------------------------
    def stop(self):
        try:
            self.tts_engine.stop()
        except:
            pass

        if self.cap:
            self.cap.release()