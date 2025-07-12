#!/usr/bin/env python3
"""
Simple test script to verify camera and gesture recognition
"""

import cv2
from gesture_recognition import GestureRecognizer
import time

def test_camera_and_gestures():
    """Test camera access and gesture recognition"""
    print("Testing camera and gesture recognition...")
    
    # Initialize gesture recognizer
    recognizer = GestureRecognizer()
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return False
    
    print("✅ Camera opened successfully")
    print("📋 Available gestures:", list(recognizer.gesture_mappings.keys()))
    print("\nPress 'q' to quit, 's' to save current frame")
    print("Try making these gestures:")
    print("- Hold up 1 finger (index) for 'one'")
    print("- Make peace sign for 'peace'")
    print("- Thumbs up for 'good'")
    print("- Closed fist for 'stop'")
    print("- Open palm for 'five'")
    
    frame_count = 0
    last_gesture = None
    gesture_count = {}
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not read frame")
            break
        
        frame_count += 1
        
        # Process every 5th frame to reduce load
        if frame_count % 5 == 0:
            result = recognizer.process_frame(frame)
            
            if result['gesture']:
                gesture = result['gesture']
                word = result['word']
                confidence = result['confidence']
                
                # Count gestures
                if gesture not in gesture_count:
                    gesture_count[gesture] = 0
                gesture_count[gesture] += 1
                
                # Only print if gesture changed or every 10 detections
                if gesture != last_gesture or gesture_count[gesture] % 10 == 0:
                    print(f"🎯 Detected: {gesture} → '{word}' (confidence: {confidence:.2f})")
                    last_gesture = gesture
        
        # Display frame
        cv2.imshow('Gesture Test - Press Q to quit', frame)
        
        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f'test_frame_{int(time.time())}.jpg', frame)
            print("📸 Frame saved")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n📊 Gesture detection summary:")
    for gesture, count in gesture_count.items():
        word = recognizer.gesture_mappings.get(gesture, 'unknown')
        print(f"  {gesture} → '{word}': {count} times")
    
    return True

if __name__ == "__main__":
    test_camera_and_gestures()
