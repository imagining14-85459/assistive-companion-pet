from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import cv2
import mediapipe as mp
import numpy as np
import sys

app = Flask(__name__)
CORS(app)

# Global variable for webcam
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
    return jsonify({'status': 'started'})

@app.route('/api/webcam/stop', methods=['POST'])
def stop_webcam():
    return jsonify({'status': 'stopped'})

@app.route('/api/webcam/detect', methods=['POST'])
def detect_faces():
    """Process webcam frame for face detection"""
    try:
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
                    min_detection_confidence=0.3,  # Lower threshold
                    min_tracking_confidence=0.3   # Lower threshold
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

if __name__ == '__main__':
    port = 5001 if sys.platform == "darwin" else 5000
    app.run(port=port, debug=True)
