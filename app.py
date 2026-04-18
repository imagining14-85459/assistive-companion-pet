from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import subprocess
import os
import threading
import time
import socket
import numpy as np
import sys

# Optional imports for Focus mode/webcam
try:
    import cv2
    import mediapipe as mp
    FOCUS_MODE_AVAILABLE = True
except ImportError:
    FOCUS_MODE_AVAILABLE = False

app = Flask(__name__)
CORS(app)

def send_to_overlay(message):
    """Send message to overlay via IPC socket"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1.0)  # Timeout after 1 second
        client.connect(('localhost', 5002))
        client.send(message.encode('utf-8'))
        client.close()
    except Exception:
        pass  # Overlay not running or connection failed

# Global variables for webcam feed
webcam_thread = None
webcam_active = False
latest_frame = None
face_mesh = None

def get_pet_data():
    """Load pet data from JSON"""
    try:
        with open("pet_data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_pet_data(data):
    """Save pet data to JSON"""
    with open("pet_data.json", "w") as f:
        json.dump(data, f, indent=4)

def webcam_feed_thread():
    """Capture webcam feed for focus detection"""
    global latest_frame, webcam_active
    
    if not FOCUS_MODE_AVAILABLE:
        print("⚠️  Focus mode not available (missing cv2/mediapipe)")
        return
    
    try:
        face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        cap = cv2.VideoCapture(0)
        
        while webcam_active:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Detect faces
            results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Draw face detection on frame
            if results.multi_face_landmarks:
                for landmarks in results.multi_face_landmarks:
                    # Draw dots on face for visualization
                    for lm in landmarks.landmark[::5]:  # Every 5th landmark for performance
                        h, w, c = frame.shape
                        x, y = int(lm.x * w), int(lm.y * h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            latest_frame = frame
            time.sleep(0.03)  # ~30 FPS
        
        cap.release()
    except Exception as e:
        print(f"⚠️  Webcam error: {e}")

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get player stats"""
    data = get_pet_data()
    return jsonify({
        'level': data.get('level', 1),
        'xp': data.get('xp', 0),
        'currency': data.get('currency', 0),
        'mode': data.get('mode', 'default'),
        'total_study_time': data.get('total_study_time', 0),
        'equipped_hat': data.get('equipped_hat', None),
        'overlay_enabled': data.get('overlay_enabled', True),
        'learning_topics': get_learning_topics()
    })

@app.route('/api/mode', methods=['POST'])
def toggle_mode():
    """Toggle between Default and Focus mode"""
    data = get_pet_data()
    current_mode = data.get('mode', 'default')
    new_mode = 'focus' if current_mode == 'default' else 'default'
    data['mode'] = new_mode
    save_pet_data(data)
    return jsonify({'mode': new_mode, 'message': f'Switched to {new_mode} mode'})

@app.route('/api/shop/buy', methods=['POST'])
def buy_item():
    """Buy item from shop"""
    item = request.json.get('item')
    prices = {
        'Top Hat': 150,
        'Monocle': 200,
        'Crown': 500,
        'Sunglasses': 100
    }
    
    data = get_pet_data()
    price = prices.get(item, 0)
    
    if data['currency'] >= price:
        data['currency'] -= price
        data['equipped_hat'] = item
        save_pet_data(data)
        return jsonify({'success': True, 'message': f'Bought {item}!', 'currency': data['currency']})
    else:
        return jsonify({'success': False, 'message': 'Not enough coins!'})

@app.route('/api/webcam/start', methods=['POST'])
def start_webcam():
    """Start webcam feed for Focus mode"""
    global webcam_thread, webcam_active
    
    if not webcam_active:
        webcam_active = True
        webcam_thread = threading.Thread(target=webcam_feed_thread, daemon=True)
        webcam_thread.start()
    
    return jsonify({'status': 'Webcam started'})

@app.route('/api/webcam/detect', methods=['POST'])
def detect_faces():
    """Process webcam frame for face detection"""
    try:
        if not FOCUS_MODE_AVAILABLE:
            return jsonify({'face_detected': False, 'error': 'Focus mode not available'})
        
        if 'frame' not in request.files:
            return jsonify({'face_detected': False, 'error': 'No frame provided'})
        
        frame_file = request.files['frame']
        if frame_file.filename == '':
            return jsonify({'face_detected': False, 'error': 'Empty frame'})
        
        # Read the frame data
        frame_data = frame_file.read()
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'face_detected': False, 'error': 'Invalid frame'})
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Initialize face mesh if not already done
        global face_mesh
        if face_mesh is None:
            try:
                import mediapipe as mp
                mp_face_mesh = mp.solutions.face_mesh
                face_mesh = mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.1,  # Lower threshold for better detection
                    min_tracking_confidence=0.1   # Lower threshold
                )
            except ImportError:
                return jsonify({'face_detected': False, 'error': 'MediaPipe not available'})
        
        # Process the frame
        results = face_mesh.process(rgb_frame)
        
        # Check if face is detected
        face_detected = results.multi_face_landmarks is not None and len(results.multi_face_landmarks) > 0
        
        return jsonify({'face_detected': face_detected})
        
    except Exception as e:
        print(f"Face detection error: {e}")
        return jsonify({'face_detected': False, 'error': str(e)})

@app.route('/api/webcam/frame')
def get_webcam_frame():
    """Get current webcam frame (placeholder for live streaming)"""
    if latest_frame is None:
        return jsonify({'frame': None})
    
    # In production, encode frame as base64 and send
    # For now, just return status
    return jsonify({'status': 'Webcam active', 'frame_available': True})

@app.route('/api/overlay/toggle', methods=['POST'])
def toggle_overlay():
    """Toggle desktop overlay on/off"""
    data = get_pet_data()
    current_state = data.get('overlay_enabled', True)
    new_state = not current_state
    data['overlay_enabled'] = new_state
    save_pet_data(data)
    return jsonify({'overlay_enabled': new_state, 'message': f'Overlay {"enabled" if new_state else "disabled"}'})

def get_learning_topics():
    """Get learning topics summary"""
    try:
        if os.path.exists("pet_data.json"):
            with open("pet_data.json", "r") as f:
                data = json.load(f)
            
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
        print(f"Error getting learning topics: {e}")
        return []

@app.route('/api/focus/metrics', methods=['GET'])
def get_focus_metrics():
    """Get detailed focus metrics for Focus mode
    
    Returns focus state, time away, attention level, and nudge/mad status
    """
    try:
        from pet_brain import PetBrain
        
        data = get_pet_data()
        current_mode = data.get('mode', 'default')
        
        # Create a PetBrain instance to get focus metrics
        pet_brain = PetBrain(mode=current_mode)
        metrics = pet_brain.get_focus_metrics()
        
        # Update pet data with focus tracking
        if current_mode == 'focus':
            if 'focus_metrics' not in data:
                data['focus_metrics'] = {}
            
            data['focus_metrics'].update({
                'time_away_seconds': metrics['time_away_seconds'],
                'attention_state': metrics['attention_state'],
                'last_check': time.time()
            })
            
            # Track if we should show pet reactions
            if metrics['should_be_mad']:
                data['focus_metrics']['pet_reaction'] = 'mad'
            elif metrics['should_nudge']:
                data['focus_metrics']['pet_reaction'] = 'nudge'
            else:
                data['focus_metrics']['pet_reaction'] = 'normal'
            
            save_pet_data(data)
        
        # Clean up resources
        pet_brain.stop()
        
        return jsonify({
            'mode': current_mode,
            'metrics': metrics,
            'pet_should_react': metrics['should_nudge'] or metrics['should_be_mad'],
            'pet_reaction': data.get('focus_metrics', {}).get('pet_reaction', 'normal')
        })
    
    except ImportError:
        return jsonify({
            'error': 'PetBrain not available',
            'mode': 'default'
        }), 400
    except Exception as e:
        print(f"Error getting focus metrics: {e}")
        return jsonify({
            'error': str(e),
            'metrics': {
                'is_focused': True,
                'time_away_seconds': 0,
                'attention_state': 'focused',
                'should_nudge': False,
                'should_be_mad': False,
                'session_time_seconds': 0
            }
        }), 400

@app.route('/api/focus/session/start', methods=['POST'])
def start_focus_session():
    """Start a focus tracking session"""
    data = get_pet_data()
    
    data['focus_session'] = {
        'start_time': time.time(),
        'mode': 'focus'
    }
    
    save_pet_data(data)
    
    return jsonify({
        'success': True,
        'message': 'Focus session started',
        'start_time': data['focus_session']['start_time']
    })

@app.route('/api/focus/session/end', methods=['POST'])
def end_focus_session():
    """End a focus tracking session and save statistics"""
    data = get_pet_data()
    
    if 'focus_session' not in data or 'start_time' not in data['focus_session']:
        return jsonify({
            'success': False,
            'message': 'No active focus session'
        })
    
    session_duration = time.time() - data['focus_session']['start_time']
    
    # Update statistics
    data['total_study_time'] = data.get('total_study_time', 0) + session_duration
    data['focus_session'] = {}
    
    save_pet_data(data)
    
    return jsonify({
        'success': True,
        'message': 'Focus session ended',
        'session_duration_seconds': session_duration,
        'total_study_time': data['total_study_time']
    })

@app.route('/api/ai/analyze_clipboard', methods=['POST'])
def analyze_clipboard():
    """Analyze clipboard text with AI"""
    try:
        data = request.json
        text = data.get('text', '')
        intent = data.get('intent', 'simplify')
        target_language = data.get('target_language')
        
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        from pet_brain import PetBrain
        brain = PetBrain()
        result = brain.analyze_clipboard_text(text, intent, target_language)
        brain.stop()
        
        pet_data = get_pet_data()
        pet_data['last_ai_output'] = result
        pet_data['last_ai_time'] = time.time()
        save_pet_data(pet_data)
        
        # Send to overlay immediately
        send_to_overlay(result)
        
        return jsonify({'result': result})
    except Exception as e:
        print(f"AI analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/study_screen', methods=['POST'])
def study_screen():
    """Analyze screen content with AI"""
    try:
        data = request.json
        question = data.get('question', 'Explain this study material for a student with ADHD.')
        
        from pet_brain import PetBrain
        brain = PetBrain()
        result = brain.study_the_screen(question)
        brain.stop()
        
        pet_data = get_pet_data()
        pet_data['last_ai_output'] = result
        pet_data['last_ai_time'] = time.time()
        save_pet_data(pet_data)
        
        # Send to overlay immediately
        send_to_overlay(result)
        
        return jsonify({'result': result})
    except Exception as e:
        print(f"Screen study error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/translate', methods=['POST'])
def translate_text():
    """Translate text using AI"""
    try:
        data = request.json
        text = data.get('text', '')
        target_language = data.get('target_language', 'es')
        
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        from pet_brain import PetBrain
        brain = PetBrain()
        result = brain.translate_text(text, target_language)
        brain.stop()
        
        pet_data = get_pet_data()
        pet_data['last_ai_output'] = result
        pet_data['last_ai_time'] = time.time()
        save_pet_data(pet_data)
        
        # Send to overlay immediately
        send_to_overlay(result)
        
        return jsonify({'result': result})
    except Exception as e:
        print(f"Translation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/explain_image', methods=['POST'])
def explain_image():
    """Explain an image using AI"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        question = request.form.get('question', 'What is this?')
        
        # Save temporarily
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image_file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            from pet_brain import PetBrain
            brain = PetBrain()
            result = brain.explain_image(tmp_path, question)
            brain.stop()
            
            pet_data = get_pet_data()
            pet_data['last_ai_output'] = result
            pet_data['last_ai_time'] = time.time()
            save_pet_data(pet_data)
            
            # Send to overlay immediately
            send_to_overlay(result)
            
            return jsonify({'result': result})
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        print(f"Image explanation error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = 5001 if sys.platform == "darwin" else 5000
    app.run(port=port, debug=True)
