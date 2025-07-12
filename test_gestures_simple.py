#!/usr/bin/env python3
"""
Simple test script to verify gesture recognition without GUI
"""

import cv2
from gesture_recognition import GestureRecognizer
import time
import numpy as np

def test_gesture_recognition():
    """Test gesture recognition with camera"""
    print("Testing gesture recognition...")
    
    # Initialize gesture recognizer
    recognizer = GestureRecognizer()
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return False
    
    print("✅ Camera opened successfully")
    print("📋 Available gestures:", list(recognizer.gesture_mappings.keys()))
    print("\nTesting for 30 seconds...")
    print("Try making these gestures:")
    print("- Hold up 1 finger (index) for 'one'")
    print("- Make peace sign for 'peace'") 
    print("- Thumbs up for 'good'")
    print("- Closed fist for 'stop'")
    print("- Open palm for 'five'")
    
    start_time = time.time()
    frame_count = 0
    gesture_detections = {}
    
    while time.time() - start_time < 30:  # Run for 30 seconds
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not read frame")
            break
        
        frame_count += 1
        
        # Process every 10th frame
        if frame_count % 10 == 0:
            try:
                result = recognizer.process_frame(frame)
                
                if result['gesture']:
                    gesture = result['gesture']
                    word = result['word']
                    confidence = result['confidence']
                    
                    # Track detections
                    if gesture not in gesture_detections:
                        gesture_detections[gesture] = []
                    gesture_detections[gesture].append(confidence)
                    
                    print(f"🎯 Frame {frame_count}: {gesture} → '{word}' (confidence: {confidence:.2f})")
                
                elif frame_count % 50 == 0:  # Print status every 50 frames
                    print(f"📷 Frame {frame_count}: No gesture detected")
                    
            except Exception as e:
                print(f"❌ Error processing frame {frame_count}: {e}")
        
        # Small delay
        time.sleep(0.1)
    
    # Cleanup
    cap.release()
    
    print(f"\n📊 Test completed! Processed {frame_count} frames")
    print("Gesture detection summary:")
    
    if gesture_detections:
        for gesture, confidences in gesture_detections.items():
            word = recognizer.gesture_mappings.get(gesture, 'unknown')
            avg_confidence = np.mean(confidences)
            count = len(confidences)
            print(f"  {gesture} → '{word}': {count} detections, avg confidence: {avg_confidence:.2f}")
    else:
        print("  No gestures detected")
        print("\n🔧 Troubleshooting tips:")
        print("  - Make sure your hand is clearly visible")
        print("  - Try better lighting")
        print("  - Hold gestures steady for 2-3 seconds")
        print("  - Make sure camera is working properly")
    
    return True

def test_single_frame():
    """Test with a single frame"""
    print("\n🔍 Testing single frame capture...")
    
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera not available")
        return False
    
    # Capture a frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Could not capture frame")
        return False
    
    print(f"✅ Captured frame: {frame.shape}")
    
    # Test processing
    try:
        result = recognizer.process_frame(frame)
        print(f"📊 Processing result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error processing frame: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Gesture Recognition Test")
    print("=" * 50)
    
    # Test single frame first
    if test_single_frame():
        print("\n" + "=" * 50)
        # Test continuous recognition
        test_gesture_recognition()
    
    print("\n" + "=" * 50)
    print("Test completed!")
