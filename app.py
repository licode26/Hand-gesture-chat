from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import base64
import json
import time
from gesture_recognition import GestureRecognizer
from word_predictor import WordPredictor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gesture_chat_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize gesture recognition and word prediction
gesture_recognizer = GestureRecognizer()
word_predictor = WordPredictor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/api/gestures')
def get_gestures():
    """Get all available gestures and their corresponding words"""
    return jsonify(gesture_recognizer.get_gesture_mappings())

@socketio.on('process_frame')
def handle_frame(data):
    """Process video frame for gesture recognition"""
    try:
        # Decode base64 image
        if 'frame' not in data:
            emit('error', {'message': 'No frame data received'})
            return

        frame_data = data['frame']
        if ',' not in frame_data:
            emit('error', {'message': 'Invalid frame format'})
            return

        image_data = base64.b64decode(frame_data.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            emit('error', {'message': 'Failed to decode frame'})
            return

        # print(f"Processing frame of size: {frame.shape}")

        # Process gesture
        result = gesture_recognizer.process_frame(frame)

        # print(f"Gesture result: {result['gesture']}, Word: {result['word']}, Confidence: {result['confidence']}")

        emit('gesture_result', {
            'gesture': result['gesture'],
            'confidence': result['confidence'],
            'word': result['word'],
            'landmarks': result['landmarks']
        })
    except Exception as e:
        # print(f"Error processing frame: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('predict_sentence')
def handle_sentence_prediction(data):
    """Predict sentences based on collected words"""
    words = data['words']
    sentences = word_predictor.predict_sentences(words)
    emit('sentence_suggestions', {'sentences': sentences})

@socketio.on('send_message')
def handle_message(data):
    """Handle chat message sending"""
    message = data['message']
    # Broadcast message to all connected clients
    emit('new_message', {
        'message': message,
        'timestamp': data.get('timestamp'),
        'user': data.get('user', 'Anonymous')
    }, broadcast=True)

# Interactive Tutorial Events
@socketio.on('start_gesture_test')
def handle_start_gesture_test(data):
    """Handle start of gesture test in tutorial"""
    target_gesture = data.get('target_gesture')
    target_word = data.get('target_word')
    print(f"Starting gesture test for: {target_gesture} -> {target_word}")

    # Store test info in session (you could use a database for persistence)
    session['current_test'] = {
        'target_gesture': target_gesture,
        'target_word': target_word,
        'start_time': time.time()
    }

@socketio.on('gesture_test_completed')
def handle_gesture_test_completed(data):
    """Handle completion of gesture test"""
    gesture = data.get('gesture')
    success = data.get('success')
    attempts = data.get('attempts')

    print(f"Gesture test completed: {gesture}, Success: {success}, Attempts: {attempts}")

    # Clear test from session
    if 'current_test' in session:
        del session['current_test']

    # You could store test results in a database here
    emit('test_result_saved', {
        'gesture': gesture,
        'success': success,
        'attempts': attempts
    })

@socketio.on('request_camera_access')
def handle_camera_request():
    """Handle camera access request from tutorial"""
    print("Camera access requested for tutorial")
    emit('camera_access_granted', {'status': 'granted'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
