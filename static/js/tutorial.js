// Interactive Tutorial JavaScript
class InteractiveTutorial {
    constructor() {
        this.socket = io();
        this.currentTest = null;
        this.testTimeout = null;
        this.testDuration = 5000; // 5 seconds to test gesture
        this.isTestingActive = false;
        
        this.initializeEventListeners();
        this.setupSocketListeners();
    }
    
    initializeEventListeners() {
        // Add click listeners to all "Try Gesture" buttons
        document.querySelectorAll('.try-gesture-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const gesture = e.target.dataset.gesture;
                const word = e.target.dataset.word;
                this.startGestureTest(gesture, word, btn);
            });
        });
    }
    
    setupSocketListeners() {
        // Listen for gesture recognition results
        this.socket.on('gesture_detected', (data) => {
            if (this.isTestingActive && this.currentTest) {
                this.handleGestureResult(data);
            }
        });
        
        // Handle connection events
        this.socket.on('connect', () => {
            console.log('Connected to tutorial server');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from tutorial server');
            this.stopCurrentTest();
        });
    }
    
    startGestureTest(gesture, word, buttonElement) {
        // Prevent multiple tests running simultaneously
        if (this.isTestingActive) {
            this.showFeedback(this.currentTest.gesture, 'Please wait for current test to finish', 'testing');
            return;
        }
        
        this.currentTest = {
            gesture: gesture,
            word: word,
            button: buttonElement,
            startTime: Date.now(),
            attempts: 0,
            maxAttempts: 3
        };
        
        this.isTestingActive = true;
        
        // Update button state
        buttonElement.classList.add('testing');
        buttonElement.innerHTML = '<i class="fas fa-camera"></i> Testing... Show the gesture!';
        
        // Show testing feedback
        this.showFeedback(gesture, 'Show the gesture now! You have 5 seconds...', 'testing');
        
        // Start camera if not already active
        this.requestCameraAccess();
        
        // Set timeout for test completion
        this.testTimeout = setTimeout(() => {
            this.handleTestTimeout();
        }, this.testDuration);
        
        // Emit test start event
        this.socket.emit('start_gesture_test', {
            target_gesture: gesture,
            target_word: word
        });
    }
    
    handleGestureResult(data) {
        if (!this.currentTest || !this.isTestingActive) return;
        
        const { gesture, word, confidence } = data;
        const targetGesture = this.currentTest.gesture;
        const targetWord = this.currentTest.word;
        
        // Check if detected gesture matches target
        const isCorrectGesture = (gesture === targetGesture) || (word === targetWord);
        const isHighConfidence = confidence >= 0.8;
        
        if (isCorrectGesture && isHighConfidence) {
            this.handleTestSuccess();
        } else if (confidence >= 0.6) {
            // Close but not quite right
            this.showFeedback(targetGesture, `Close! Detected "${word}" but looking for "${targetWord}". Try again!`, 'testing');
        }
    }
    
    handleTestSuccess() {
        if (!this.currentTest) return;
        
        clearTimeout(this.testTimeout);
        this.isTestingActive = false;
        
        const { gesture, button } = this.currentTest;
        
        // Update button state
        button.classList.remove('testing');
        button.classList.add('success');
        button.innerHTML = '<i class="fas fa-check"></i> Perfect! Well Done!';
        
        // Show success feedback
        this.showFeedback(gesture, '✅ Excellent! Gesture recognized correctly!', 'success');
        
        // Add success animation
        this.addSuccessAnimation(gesture);
        
        // Reset button after delay
        setTimeout(() => {
            button.classList.remove('success');
            button.innerHTML = '<i class="fas fa-camera"></i> Try This Gesture';
        }, 3000);
        
        // Emit success event
        this.socket.emit('gesture_test_completed', {
            gesture: gesture,
            success: true,
            attempts: this.currentTest.attempts + 1
        });
        
        this.currentTest = null;
    }
    
    handleTestTimeout() {
        if (!this.currentTest) return;
        
        this.currentTest.attempts++;
        
        if (this.currentTest.attempts < this.currentTest.maxAttempts) {
            // Allow retry
            this.showFeedback(this.currentTest.gesture, 
                `Time's up! Try again (${this.currentTest.attempts}/${this.currentTest.maxAttempts})`, 'testing');
            
            // Restart test
            this.testTimeout = setTimeout(() => {
                this.handleTestTimeout();
            }, this.testDuration);
        } else {
            // Max attempts reached
            this.handleTestFailure();
        }
    }
    
    handleTestFailure() {
        if (!this.currentTest) return;
        
        this.isTestingActive = false;
        const { gesture, button, word } = this.currentTest;
        
        // Update button state
        button.classList.remove('testing');
        button.classList.add('failed');
        button.innerHTML = '<i class="fas fa-times"></i> Try Again Later';
        
        // Show failure feedback with tips
        this.showFeedback(gesture, 
            `❌ Gesture not detected. Make sure your hand is clearly visible and try the "${word}" gesture as shown in the demo.`, 
            'error');
        
        // Reset button after delay
        setTimeout(() => {
            button.classList.remove('failed');
            button.innerHTML = '<i class="fas fa-camera"></i> Try This Gesture';
        }, 4000);
        
        // Emit failure event
        this.socket.emit('gesture_test_completed', {
            gesture: gesture,
            success: false,
            attempts: this.currentTest.attempts
        });
        
        this.currentTest = null;
    }
    
    showFeedback(gesture, message, type) {
        const feedbackElement = document.getElementById(`feedback-${gesture}`);
        if (feedbackElement) {
            feedbackElement.textContent = message;
            feedbackElement.className = `gesture-feedback ${type}`;
        }
    }
    
    addSuccessAnimation(gesture) {
        const gestureItem = document.querySelector(`[data-gesture="${gesture}"]`).closest('.gesture-item');
        if (gestureItem) {
            gestureItem.style.animation = 'success-bounce 0.6s ease';
            setTimeout(() => {
                gestureItem.style.animation = '';
            }, 600);
        }
    }
    
    requestCameraAccess() {
        // Emit request to start camera for testing
        this.socket.emit('request_camera_access');
    }
    
    stopCurrentTest() {
        if (this.testTimeout) {
            clearTimeout(this.testTimeout);
        }
        
        if (this.currentTest) {
            const { button } = this.currentTest;
            button.classList.remove('testing', 'success', 'failed');
            button.innerHTML = '<i class="fas fa-camera"></i> Try This Gesture';
        }
        
        this.isTestingActive = false;
        this.currentTest = null;
    }
}

// Initialize interactive tutorial when page loads
document.addEventListener('DOMContentLoaded', () => {
    const tutorial = new InteractiveTutorial();
    
    // Add global tutorial controls
    const tutorialControls = document.createElement('div');
    tutorialControls.className = 'tutorial-controls';
    tutorialControls.innerHTML = `
        <div class="tutorial-status">
            <h3><i class="fas fa-graduation-cap"></i> Interactive Tutorial Mode</h3>
            <p>Click "Try This Gesture" buttons to test your gestures with AI feedback!</p>
        </div>
    `;
    
    const gestureGuide = document.querySelector('.gesture-guide');
    if (gestureGuide) {
        gestureGuide.insertBefore(tutorialControls, gestureGuide.firstChild);
    }
});
