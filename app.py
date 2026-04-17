from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import subprocess
import os
import cv2
import mediapipe as mp
import threading
import time
import sys

app = Flask(__name__)
CORS(app)

# Global variables for webcam feed
webcam_thread = None
webcam_active = False
latest_frame = None

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
        'equipped_hat': data.get('equipped_hat', None)
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

@app.route('/api/webcam/stop', methods=['POST'])
def stop_webcam():
    """Stop webcam feed"""
    global webcam_active
    webcam_active = False
    return jsonify({'status': 'Webcam stopped'})

@app.route('/api/webcam/frame')
def get_webcam_frame():
    """Get current webcam frame (placeholder for live streaming)"""
    if latest_frame is None:
        return jsonify({'frame': None})
    
    # In production, encode frame as base64 and send
    # For now, just return status
    return jsonify({'status': 'Webcam active', 'frame_available': True})

if __name__ == '__main__':
    port = 5001 if sys.platform == "darwin" else 5000
    app.run(port=port, debug=True)
