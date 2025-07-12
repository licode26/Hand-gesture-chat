import cv2
import mediapipe as mp
import numpy as np
import math

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.2
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Gesture mappings matching the tutorial exactly
        self.gesture_mappings = {
            # NUMBERS (7 gestures) - As shown in tutorial
            'zero': 'zero',
            'one': 'one',
            'two': 'two',
            'three': 'three',
            'four': 'four',
            'five': 'five',
            'peace': 'peace',
            'ok': 'okay',

            # EMOTIONS (8 gestures) - As shown in tutorial
            'thumbs_up': 'good',
            'thumbs_down': 'bad',
            'love_sign': 'love',
            'happy_palm': 'happy',
            'sad_fist': 'sad',
            'worried_forehead': 'worried',
            'tired_rub': 'tired',
            'grateful_bow': 'grateful',

            # BASIC NEEDS (8 gestures) - As shown in tutorial
            'help_wave': 'help',
            'stop_palm': 'stop',
            'eat_mouth': 'eat',
            'drink_cup': 'drink',
            'sleep_head': 'sleep',
            'bathroom_urgent': 'bathroom',
            'hot_fan': 'hot',
            'cold_shiver': 'cold',

            # SOCIAL (9 gestures) - Common interactions
            'hello_wave': 'hello',
            'bye_wave': 'bye',
            'yes_nod': 'yes',
            'no_shake': 'no',
            'please_pray': 'please',
            'thanks_bow': 'thanks',
            'you_point': 'you',
            'me_point': 'me',
            'call_phone': 'call'
        }
    
    def get_gesture_mappings(self):
        """Return all gesture mappings for tutorial"""
        return self.gesture_mappings
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_finger_extended(self, landmarks, finger_tip, finger_pip, finger_mcp):
        """Check if a finger is extended"""
        return landmarks[finger_tip].y < landmarks[finger_pip].y and landmarks[finger_pip].y < landmarks[finger_mcp].y

    def is_thumb_extended(self, landmarks):
        """Check if thumb is extended - special logic for thumb"""
        # Thumb tip (4) should be further from wrist (0) than thumb IP (3)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        wrist = landmarks[0]

        # Calculate distances from wrist
        tip_distance = math.sqrt((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)
        ip_distance = math.sqrt((thumb_ip.x - wrist.x)**2 + (thumb_ip.y - wrist.y)**2)

        return tip_distance > ip_distance
    
    def recognize_gesture(self, landmarks):
        """Recognize gesture based on hand landmarks"""
        if not landmarks:
            return None, 0.0
        
        # Get landmark positions
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        index_mcp = landmarks[5]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        middle_mcp = landmarks[9]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        ring_mcp = landmarks[13]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        pinky_mcp = landmarks[17]
        
        # Check which fingers are extended
        thumb_extended = self.is_thumb_extended(landmarks)
        index_extended = self.is_finger_extended(landmarks, 8, 6, 5)
        middle_extended = self.is_finger_extended(landmarks, 12, 10, 9)
        ring_extended = self.is_finger_extended(landmarks, 16, 14, 13)
        pinky_extended = self.is_finger_extended(landmarks, 20, 18, 17)
        
        extended_fingers = [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]
        num_extended = sum(extended_fingers)
        
        # Enhanced gesture recognition matching tutorial gestures
        base_confidence = 0.85

        # First try specific gesture detection
        specific_gesture, specific_confidence = self.detect_specific_gestures(landmarks, extended_fingers, num_extended)
        if specific_gesture:
            return specific_gesture, specific_confidence

        # Get hand position context for better recognition
        wrist = landmarks[0]
        middle_finger_mcp = landmarks[9]
        hand_height = wrist.y
        hand_center_x = wrist.x

        # NUMBERS - Basic counting gestures
        if num_extended == 0:
            return 'zero', base_confidence
        elif num_extended == 1 and index_extended and not thumb_extended:
            return 'one', base_confidence
        elif num_extended == 2 and index_extended and middle_extended and not thumb_extended:
            return 'peace', base_confidence  # Peace sign (also two)
        elif num_extended == 2 and index_extended and middle_extended:
            return 'two', base_confidence
        elif num_extended == 3 and index_extended and middle_extended and ring_extended and not thumb_extended:
            return 'three', base_confidence
        elif num_extended == 4 and not thumb_extended:
            return 'four', base_confidence
        elif num_extended == 5:
            return 'five', base_confidence

        # OK GESTURE - Special case (thumb and index forming circle)
        elif num_extended == 2 and thumb_extended and index_extended:
            distance = self.calculate_distance(thumb_tip, index_tip)
            if distance < 0.08:  # Close together = OK sign
                return 'ok', base_confidence

        # EMOTIONS - Specific patterns
        elif num_extended == 1 and thumb_extended and not index_extended:
            # Check thumb direction for thumbs up vs down
            if thumb_tip.y < landmarks[3].y:  # Thumb pointing up
                return 'thumbs_up', base_confidence  # "good"
            else:
                return 'thumbs_down', base_confidence  # "bad"

        elif num_extended == 2 and index_extended and pinky_extended and not thumb_extended:
            return 'love_sign', base_confidence  # "love"

        elif num_extended == 5 and thumb_extended:
            # Analyze hand position for different 5-finger gestures
            if hand_height < 0.3:  # High position
                return 'happy_palm', base_confidence  # "happy"
            elif hand_center_x < 0.3:  # Left side
                return 'help_wave', base_confidence  # "help"
            elif hand_center_x > 0.7:  # Right side
                return 'bye_wave', base_confidence  # "bye"
            else:
                return 'hello_wave', base_confidence  # "hello"

        elif num_extended == 0:
            # Closed fist - could be sad or other emotions based on context
            if hand_height > 0.7:  # Lower position
                return 'sad_fist', base_confidence  # "sad"
            else:
                return 'cold_shiver', base_confidence  # "cold"

        # BASIC NEEDS - Specific hand positions
        elif num_extended == 5 and not thumb_extended:
            # Open palm without thumb
            if hand_center_x > 0.6:  # Right side
                return 'stop_palm', base_confidence  # "stop"
            else:
                return 'help_wave', base_confidence  # "help"

        elif num_extended == 3 and thumb_extended and index_extended and middle_extended:
            # Three fingers including thumb - could be drink or other
            if hand_height < 0.4:  # Higher position
                return 'drink_cup', base_confidence  # "drink"
            else:
                return 'grateful_bow', base_confidence  # "grateful"

        elif num_extended == 1 and index_extended:
            # Single index finger - context dependent
            if hand_height < 0.3:  # High position
                return 'worried_forehead', base_confidence  # "worried"
            elif hand_center_x > 0.6:  # Pointing right
                return 'you_point', base_confidence  # "you"
            else:
                return 'bathroom_urgent', base_confidence  # "bathroom"

        # PHONE GESTURE - Thumb and pinky
        elif num_extended == 2 and thumb_extended and pinky_extended:
            return 'call_phone', base_confidence  # "call"

        # SPECIAL GESTURES - Context-based recognition
        elif num_extended == 4 and thumb_extended:
            # Four fingers plus thumb in specific positions
            if hand_height > 0.6:  # Lower position
                return 'hot_fan', base_confidence  # "hot"
            else:
                return 'sleep_head', base_confidence  # "sleep"

        return None, 0.0

    def analyze_hand_orientation(self, landmarks):
        """Analyze hand orientation and movement for better gesture recognition"""
        if not landmarks or len(landmarks) < 21:
            return {}

        wrist = landmarks[0]
        middle_finger_tip = landmarks[12]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        # Calculate hand orientation
        hand_vector_x = middle_finger_tip.x - wrist.x
        hand_vector_y = middle_finger_tip.y - wrist.y

        # Determine if hand is tilted
        is_tilted = abs(hand_vector_x) > 0.1

        # Determine if fingers are pointing up or down
        fingers_up = middle_finger_tip.y < wrist.y

        # Calculate hand center position
        hand_center_x = wrist.x
        hand_center_y = wrist.y

        return {
            'tilted': is_tilted,
            'fingers_up': fingers_up,
            'center_x': hand_center_x,
            'center_y': hand_center_y,
            'thumb_position': thumb_tip,
            'index_position': index_tip
        }

    def detect_specific_gestures(self, landmarks, extended_fingers, num_extended):
        """Detect specific gestures that require special analysis"""
        if not landmarks:
            return None, 0.0

        thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended = extended_fingers
        orientation = self.analyze_hand_orientation(landmarks)

        # PRAYER/BOW GESTURE - Hands together (simplified to specific finger pattern)
        if num_extended == 5 and orientation['center_x'] > 0.4 and orientation['center_x'] < 0.6:
            if not orientation['tilted']:
                return 'please_pray', 0.8  # "please"

        # TIRED GESTURE - Rubbing eyes (hand near face area)
        if num_extended == 3 and thumb_extended and index_extended and middle_extended:
            if orientation['center_y'] < 0.4:  # Higher on screen (near face)
                return 'tired_rub', 0.8  # "tired"

        # EAT GESTURE - Hand to mouth
        if num_extended == 3 and not thumb_extended:
            if orientation['center_y'] < 0.4 and orientation['center_x'] > 0.4:
                return 'eat_mouth', 0.8  # "eat"

        # POINTING GESTURES - More precise pointing detection
        if num_extended == 1 and index_extended:
            if orientation['center_x'] < 0.3:  # Pointing left (to self)
                return 'me_point', 0.8  # "me"
            elif orientation['center_x'] > 0.7:  # Pointing right (to others)
                return 'you_point', 0.8  # "you"

        # YES/NO GESTURES - Based on thumb direction and movement
        if num_extended == 1 and thumb_extended:
            thumb_tip = landmarks[4]
            thumb_base = landmarks[2]
            if thumb_tip.y < thumb_base.y:  # Thumb up
                return 'yes_nod', 0.8  # "yes"

        if num_extended == 1 and index_extended:
            if orientation['tilted']:  # Wagging motion
                return 'no_shake', 0.8  # "no"

        return None, 0.0
    
    def process_frame(self, frame):
        """Process a single frame and return gesture recognition results"""
        # Ensure frame is valid
        if frame is None or frame.size == 0:
            return {'gesture': None, 'confidence': 0.0, 'word': None, 'landmarks': []}

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with MediaPipe
        results = self.hands.process(rgb_frame)

        gesture = None
        confidence = 0.0
        word = None
        landmarks_data = []

        # Check if hands were detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Convert landmarks to list for JSON serialization
                landmarks_list = []
                for landmark in hand_landmarks.landmark:
                    landmarks_list.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                landmarks_data.append(landmarks_list)

                # Recognize gesture
                gesture, confidence = self.recognize_gesture(hand_landmarks.landmark)
                if gesture and gesture in self.gesture_mappings:
                    word = self.gesture_mappings[gesture]
                break  # Process only the first hand for now

        return {
            'gesture': gesture,
            'confidence': confidence,
            'word': word,
            'landmarks': landmarks_data
        }
