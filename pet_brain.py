import pyautogui
import os
import pyttsx3
import pyperclip
import google.generativeai as genai
from dotenv import load_dotenv

# Optional imports for Focus mode
try:
    import cv2
    import mediapipe as mp
    FOCUS_MODE_AVAILABLE = True
except ImportError:
    FOCUS_MODE_AVAILABLE = False

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file")

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)

class PetBrain:
    def __init__(self, mode="default"):
        self.mode = mode
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Slower for accessibility
        
        # Clipboard tracking
        self.last_clipboard_content = ""
        
        # Learning tracking
        self.current_session_topics = []
        
        # Initialize focus detection if in Focus mode
        self.face_mesh = None
        self.cap = None
        self.last_seen = None
        
        if mode == "focus":
            if not FOCUS_MODE_AVAILABLE:
                raise ImportError("Focus mode requires opencv-python and mediapipe. Install with: pip install -r requirements.txt")
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
            self.cap = cv2.VideoCapture(0)
            self.last_seen = __import__('time').time()

    def check_clipboard(self):
        """Check if clipboard content has changed"""
        try:
            current_content = pyperclip.paste()
            if current_content != self.last_clipboard_content and current_content.strip():
                self.last_clipboard_content = current_content
                return current_content
        except:
            pass
        return None

    def bionic_reading(self, text):
        """Apply bionic reading formatting for dyslexia/ADHD
        Bolds first 1-2 letters of each word for faster reading"""
        words = text.split()
        bionic_text = []
        
        for word in words:
            if len(word) <= 2:
                bionic_text.append(f"**{word}**")
            else:
                # Bold first 2 characters
                bolded = f"**{word[:2]}**{word[2:]}"
                bionic_text.append(bolded)
        
        return " ".join(bionic_text)

    def is_focusing(self):
        """Check if user is focused (Focus mode only)"""
        if self.mode != "focus" or not self.face_mesh:
            return True  # Always return True in Default mode
        
        import time
        ret, frame = self.cap.read()
        if not ret: return False
        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            self.last_seen = time.time()
            return True
        return (time.time() - self.last_seen) < 3

    def study_the_screen(self, question="Explain this study material for a student with ADHD."):
        """Analyze screen for study assistance"""
        pyautogui.screenshot("study_session.png")
        try:
            response = self.model.generate_content([question, "study_session.png"])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                return "🤖 AI service temporarily unavailable due to high usage. Please try again in a few minutes, or use the web dashboard for screen analysis."
            elif "403" in error_str or "forbidden" in error_str.lower():
                return "🤖 AI service access denied. Please check your API key configuration."
            else:
                return f"🤖 Error analyzing screen: {error_str[:80]}{'...' if len(error_str) > 80 else ''}"

    def analyze_clipboard_text(self, text, intent, target_language=None):
        """Analyze copied text with specific intent
        intent options: 'simplify', 'translate', 'bionic', 'explain'
        """
        try:
            if intent == "simplify":
                prompt = "Review and explain this text for a student with ADHD. Provide a clear summary, key concepts, and helpful study tips."
            elif intent == "translate":
                if target_language:
                    prompt = f"Translate this to {target_language} and keep it concise."
                else:
                    # Default to Spanish if no language specified
                    prompt = "Translate this to Spanish and keep it concise."
            elif intent == "bionic":
                return self.bionic_reading(text)
            elif intent == "explain":
                prompt = "Explain the key concepts in this text clearly and simply."
            else:
                prompt = "Analyze this text and provide helpful information."
            
            response = self.model.generate_content(prompt + "\n\nText to analyze:\n" + text)
            result = response.text
            
            # Track learning for simplify/translate intents
            if intent in ['simplify', 'translate']:
                self.track_learning_topic(text, intent)
            
            return result
        except Exception as e:
            error_str = str(e)
            # Handle common API errors with user-friendly messages
            if "429" in error_str or "quota" in error_str.lower():
                return "🤖 AI service temporarily unavailable due to high usage. Please try again in a few minutes, or use the web dashboard for AI tools."
            elif "403" in error_str or "forbidden" in error_str.lower():
                return "🤖 AI service access denied. Please check your API key configuration."
            elif "network" in error_str.lower() or "connection" in error_str.lower():
                return "🤖 Network error. Please check your internet connection and try again."
            else:
                # Generic error with truncated message
                return f"🤖 Error: {error_str[:100]}{'...' if len(error_str) > 100 else ''}"

    def explain_image(self, image_path, question="What is this?"):
        """Explain a specific image or diagram"""
        try:
            response = self.model.generate_content([question, image_path])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                return "🤖 AI service temporarily unavailable due to high usage. Please try again in a few minutes."
            elif "403" in error_str or "forbidden" in error_str.lower():
                return "🤖 AI service access denied. Please check your API key configuration."
            else:
                return f"🤖 Error analyzing image: {error_str[:80]}{'...' if len(error_str) > 80 else ''}"

    def text_to_speech(self, text):
        """Read text aloud for accessibility (helpful for ESL learners)"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False

    def track_learning_topic(self, text, intent):
        """Track topics that student struggled with (simplify/translate)"""
        if intent in ['simplify', 'translate']:
            # Extract key topics/words from the text
            try:
                # Use AI to identify key learning topics
                prompt = f"Extract the main topic or key term from this text that a student might need help with: '{text[:200]}...'"
                response = self.model.generate_content(prompt)
                topic = response.text.strip()
                
                # Add to current session
                self.current_session_topics.append({
                    'topic': topic,
                    'original_text': text[:100] + '...' if len(text) > 100 else text,
                    'intent': intent,
                    'timestamp': __import__('time').time()
                })
                
                # Save to persistent data
                self.save_learning_data()
                
            except Exception as e:
                print(f"Error tracking learning topic: {e}")

    def save_learning_data(self):
        """Save learning data to pet_data.json"""
        try:
            # Load existing data
            data = {}
            if os.path.exists("pet_data.json"):
                with open("pet_data.json", "r") as f:
                    data = __import__('json').load(f)
            
            # Initialize learning data if not exists
            if 'learning_history' not in data:
                data['learning_history'] = []
            
            # Add current session topics
            data['learning_history'].extend(self.current_session_topics)
            
            # Keep only last 100 entries to prevent file from growing too large
            data['learning_history'] = data['learning_history'][-100:]
            
            # Save back to file
            with open("pet_data.json", "w") as f:
                __import__('json').dump(data, f, indent=4)
                
        except Exception as e:
            print(f"Error saving learning data: {e}")

    def get_learning_summary(self):
        """Get summary of learning topics for dashboard"""
        try:
            if os.path.exists("pet_data.json"):
                with open("pet_data.json", "r") as f:
                    data = __import__('json').load(f)
                
                history = data.get('learning_history', [])
                
                # Group by topic and count frequency
                topic_counts = {}
                for item in history:
                    topic = item['topic']
                    if topic in topic_counts:
                        topic_counts[topic] += 1
                    else:
                        topic_counts[topic] = 1
                
                # Sort by frequency (most struggled with first)
                sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
                
                return sorted_topics[:10]  # Top 10 topics
                
        except Exception as e:
            print(f"Error getting learning summary: {e}")
            return []

    def stop(self):
        """Cleanup TTS engine, webcam, and focus resources"""
        try:
            self.tts_engine.stop()
        except Exception:
            pass
        if self.cap:
            self.cap.release()
        if self.face_mesh:
            try:
                self.face_mesh.close()
            except Exception:
                pass

    def translate_text(self, text, target_language='es'):
        """Translate text to help ESL learners (default: Spanish)"""
        try:
            result = self.model.generate_content(f"Translate this to {target_language} and keep it concise: {text}")
            return result.text
        except Exception as e:
            return f"Translation error: {e}"

    def get_focus_metrics(self):
        """Get focus tracking metrics for Focus mode"""
        import time
        
        if self.mode != "focus":
            return {
                'is_focused': True,
                'time_away_seconds': 0,
                'attention_state': 'focused',
                'should_nudge': False,
                'should_be_mad': False,
                'session_time_seconds': 0
            }
        
        # Check if face is currently detected
        is_focused = self.is_focusing()
        
        # Calculate time away
        time_away = 0
        if not is_focused and self.last_seen:
            time_away = time.time() - self.last_seen
        
        # Determine attention state
        if is_focused:
            attention_state = 'focused'
        elif time_away < 10:
            attention_state = 'briefly_away'
        else:
            attention_state = 'away'
        
        # Determine if we should nudge or be mad
        should_nudge = time_away > 5 and time_away < 30
        should_be_mad = time_away > 30
        
        # Session time (placeholder - would need session start time)
        session_time_seconds = 0  # This would be calculated from session start
        
        return {
            'is_focused': is_focused,
            'time_away_seconds': time_away,
            'attention_state': attention_state,
            'should_nudge': should_nudge,
            'should_be_mad': should_be_mad,
            'session_time_seconds': session_time_seconds
        }

    def stop(self):
        """Cleanup TTS engine and webcam if Focus mode"""
        self.tts_engine.stop()
        if self.cap:
            self.cap.release()
