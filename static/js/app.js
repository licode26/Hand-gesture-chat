// Gesture Chat Application
class GestureChat {
    constructor() {
        this.socket = io();
        this.videoElement = document.getElementById('videoElement');
        this.overlayCanvas = document.getElementById('overlayCanvas');
        this.ctx = this.overlayCanvas.getContext('2d');
        this.stream = null;
        this.isRecording = false;
        this.collectedWords = [];
        this.currentGesture = null;
        this.currentWord = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.setupSocketListeners();
    }
    
    initializeElements() {
        this.startCameraBtn = document.getElementById('startCamera');
        this.stopCameraBtn = document.getElementById('stopCamera');
        this.gestureNameEl = document.getElementById('gestureName');
        this.gestureConfidenceEl = document.getElementById('gestureConfidence');
        this.wordDisplayEl = document.getElementById('wordDisplay');
        this.collectedWordsEl = document.getElementById('collectedWords');
        this.addWordBtn = document.getElementById('addWord');
        this.clearWordsBtn = document.getElementById('clearWords');
        this.predictSentenceBtn = document.getElementById('predictSentence');
        this.sentenceSuggestionsEl = document.getElementById('sentenceSuggestions');
        this.chatMessagesEl = document.getElementById('chatMessages');
        this.messageInputEl = document.getElementById('messageInput');
        this.sendMessageBtn = document.getElementById('sendMessage');
        this.connectionStatusEl = document.getElementById('connectionStatus');
        this.cameraStatusEl = document.getElementById('cameraStatus');

        // Camera size controls
        this.sizeSmallBtn = document.getElementById('sizeSmall');
        this.sizeMediumBtn = document.getElementById('sizeMedium');
        this.sizeLargeBtn = document.getElementById('sizeLarge');
        this.sizeFullscreenBtn = document.getElementById('sizeFullscreen');
        this.videoContainer = document.querySelector('.video-container');
    }
    
    setupEventListeners() {
        this.startCameraBtn.addEventListener('click', () => this.startCamera());
        this.stopCameraBtn.addEventListener('click', () => this.stopCamera());
        this.addWordBtn.addEventListener('click', () => this.addCurrentWord());
        this.clearWordsBtn.addEventListener('click', () => this.clearWords());
        this.predictSentenceBtn.addEventListener('click', () => this.predictSentences());
        this.sendMessageBtn.addEventListener('click', () => this.sendMessage());
        this.messageInputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Handle window resize to adjust canvas overlay
        window.addEventListener('resize', () => {
            if (this.isRecording) {
                setTimeout(() => this.setupCanvasOverlay(), 100);
            }
        });

        // Camera size controls
        this.sizeSmallBtn.addEventListener('click', () => this.setCameraSize('small'));
        this.sizeMediumBtn.addEventListener('click', () => this.setCameraSize('medium'));
        this.sizeLargeBtn.addEventListener('click', () => this.setCameraSize('large'));
        this.sizeFullscreenBtn.addEventListener('click', () => this.setCameraSize('fullscreen'));
    }
    
    setupSocketListeners() {
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('gesture_result', (data) => {
            this.handleGestureResult(data);
        });
        
        this.socket.on('sentence_suggestions', (data) => {
            this.displaySentenceSuggestions(data.sentences);
        });
        
        this.socket.on('new_message', (data) => {
            this.displayMessage(data);
        });
        
        this.socket.on('error', (data) => {
            console.error('Socket error:', data.message);
            this.showNotification('Error: ' + data.message, 'error');
        });
    }
    
    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });

            this.videoElement.srcObject = this.stream;

            // Wait for video to load and set canvas dimensions
            this.videoElement.onloadedmetadata = () => {
                this.videoElement.play();
                this.setupCanvasOverlay();
            };

            // Also setup canvas when video starts playing
            this.videoElement.onplaying = () => {
                this.setupCanvasOverlay();
            };

            this.isRecording = true;
            this.startCameraBtn.disabled = true;
            this.stopCameraBtn.disabled = false;
            this.addWordBtn.disabled = false;

            this.updateCameraStatus(true);

            // Start gesture recognition after a short delay
            setTimeout(() => {
                this.startGestureRecognition();
            }, 500);

        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showNotification('Error accessing camera. Please check permissions.', 'error');
        }
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.videoElement.srcObject = null;
        this.isRecording = false;
        this.startCameraBtn.disabled = false;
        this.stopCameraBtn.disabled = true;
        this.addWordBtn.disabled = true;
        
        this.updateCameraStatus(false);
        this.clearGestureDisplay();
    }
    
    startGestureRecognition() {
        if (!this.isRecording) return;

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        const captureFrame = () => {
            if (!this.isRecording) return;

            // Ensure video is ready and has dimensions
            if (this.videoElement.videoWidth === 0 || this.videoElement.videoHeight === 0) {
                setTimeout(captureFrame, 100);
                return;
            }

            // Set canvas size if not already set
            if (canvas.width !== this.videoElement.videoWidth) {
                canvas.width = this.videoElement.videoWidth;
                canvas.height = this.videoElement.videoHeight;
                console.log(`Capture canvas size: ${canvas.width}x${canvas.height}`);
            }

            try {
                ctx.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
                const frameData = canvas.toDataURL('image/jpeg', 0.7);

                this.socket.emit('process_frame', { frame: frameData });
            } catch (error) {
                console.error('Error capturing frame:', error);
            }

            setTimeout(captureFrame, 200); // Process every 200ms for better performance
        };

        captureFrame();
    }
    
    handleGestureResult(data) {
        this.currentGesture = data.gesture;
        this.currentWord = data.word;
        
        if (data.gesture) {
            this.gestureNameEl.textContent = data.gesture;
            this.gestureConfidenceEl.textContent = `(${(data.confidence * 100).toFixed(1)}%)`;
            this.wordDisplayEl.textContent = data.word || 'Unknown';
            
            // Draw landmarks on overlay canvas
            this.drawLandmarks(data.landmarks);
        } else {
            this.gestureNameEl.textContent = 'None';
            this.gestureConfidenceEl.textContent = '';
            this.wordDisplayEl.textContent = 'None';
            this.clearOverlay();
        }
    }
    
    drawLandmarks(landmarksArray) {
        this.clearOverlay();
        
        if (!landmarksArray || landmarksArray.length === 0) return;
        
        const landmarks = landmarksArray[0]; // Use first hand
        const canvasWidth = this.overlayCanvas.width;
        const canvasHeight = this.overlayCanvas.height;
        
        this.ctx.fillStyle = '#FF0000';
        this.ctx.strokeStyle = '#00FF00';
        this.ctx.lineWidth = 2;
        
        // Draw landmarks
        landmarks.forEach((landmark, index) => {
            const x = landmark.x * canvasWidth;
            const y = landmark.y * canvasHeight;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 3, 0, 2 * Math.PI);
            this.ctx.fill();
        });
        
        // Draw connections between landmarks
        const connections = [
            [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
            [0, 5], [5, 6], [6, 7], [7, 8], // Index
            [0, 9], [9, 10], [10, 11], [11, 12], // Middle
            [0, 13], [13, 14], [14, 15], [15, 16], // Ring
            [0, 17], [17, 18], [18, 19], [19, 20] // Pinky
        ];
        
        connections.forEach(([start, end]) => {
            const startPoint = landmarks[start];
            const endPoint = landmarks[end];
            
            this.ctx.beginPath();
            this.ctx.moveTo(startPoint.x * canvasWidth, startPoint.y * canvasHeight);
            this.ctx.lineTo(endPoint.x * canvasWidth, endPoint.y * canvasHeight);
            this.ctx.stroke();
        });
    }
    
    clearOverlay() {
        this.ctx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    }
    
    clearGestureDisplay() {
        this.gestureNameEl.textContent = 'None';
        this.gestureConfidenceEl.textContent = '';
        this.wordDisplayEl.textContent = 'None';
        this.clearOverlay();
    }

    setupCanvasOverlay() {
        if (!this.videoElement.videoWidth || !this.videoElement.videoHeight) {
            // Video not ready yet, try again later
            setTimeout(() => this.setupCanvasOverlay(), 100);
            return;
        }

        // Get the actual displayed video dimensions
        const videoRect = this.videoElement.getBoundingClientRect();
        const videoAspectRatio = this.videoElement.videoWidth / this.videoElement.videoHeight;
        const containerAspectRatio = videoRect.width / videoRect.height;

        let displayWidth, displayHeight;

        if (videoAspectRatio > containerAspectRatio) {
            // Video is wider than container
            displayWidth = videoRect.width;
            displayHeight = videoRect.width / videoAspectRatio;
        } else {
            // Video is taller than container
            displayHeight = videoRect.height;
            displayWidth = videoRect.height * videoAspectRatio;
        }

        // Set canvas size to match the actual video stream resolution
        this.overlayCanvas.width = this.videoElement.videoWidth;
        this.overlayCanvas.height = this.videoElement.videoHeight;

        // Set canvas display size to match the displayed video
        this.overlayCanvas.style.width = displayWidth + 'px';
        this.overlayCanvas.style.height = displayHeight + 'px';

        // Center the canvas overlay
        const offsetX = (videoRect.width - displayWidth) / 2;
        const offsetY = (videoRect.height - displayHeight) / 2;
        this.overlayCanvas.style.left = offsetX + 'px';
        this.overlayCanvas.style.top = offsetY + 'px';

        console.log(`Video: ${this.videoElement.videoWidth}x${this.videoElement.videoHeight}`);
        console.log(`Display: ${displayWidth}x${displayHeight}`);
        console.log(`Canvas: ${this.overlayCanvas.width}x${this.overlayCanvas.height}`);
    }

    setCameraSize(size) {
        // Remove all size classes
        this.videoContainer.classList.remove('size-small', 'size-medium', 'size-large', 'size-fullscreen');

        // Add the selected size class
        this.videoContainer.classList.add(`size-${size}`);

        // Update button states
        document.querySelectorAll('.size-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`size${size.charAt(0).toUpperCase() + size.slice(1)}`).classList.add('active');

        // Readjust canvas overlay after size change
        if (this.isRecording) {
            setTimeout(() => this.setupCanvasOverlay(), 200);
        }

        this.showNotification(`Camera size set to ${size}`, 'info');
    }

    autoGenerateSentences() {
        // Auto-generate sentences when we have words
        if (this.collectedWords.length > 0) {
            setTimeout(() => {
                this.socket.emit('predict_sentence', { words: this.collectedWords });
            }, 500); // Small delay to let the UI update
        }
    }

    addCurrentWord() {
        if (this.currentWord && !this.collectedWords.includes(this.currentWord)) {
            this.collectedWords.push(this.currentWord);
            this.updateWordDisplay();
            this.showNotification(`Added word: "${this.currentWord}"`, 'success');

            // Auto-generate sentences when words are added
            this.autoGenerateSentences();
        } else if (this.collectedWords.includes(this.currentWord)) {
            this.showNotification(`Word "${this.currentWord}" already added`, 'warning');
        } else {
            this.showNotification('No word to add', 'warning');
        }
    }

    clearWords() {
        this.collectedWords = [];
        this.updateWordDisplay();
        this.sentenceSuggestionsEl.innerHTML = '';
        this.showNotification('Cleared all words', 'info');
    }

    updateWordDisplay() {
        this.collectedWordsEl.innerHTML = '';

        this.collectedWords.forEach((word, index) => {
            const wordTag = document.createElement('span');
            wordTag.className = 'word-tag';
            wordTag.innerHTML = `
                ${word}
                <button class="remove-word" onclick="gestureChat.removeWord(${index})">×</button>
            `;
            this.collectedWordsEl.appendChild(wordTag);
        });

        if (this.collectedWords.length === 0) {
            this.collectedWordsEl.innerHTML = '<span style="color: #718096; font-style: italic;">No words collected yet</span>';
        }
    }

    removeWord(index) {
        const removedWord = this.collectedWords.splice(index, 1)[0];
        this.updateWordDisplay();
        this.showNotification(`Removed word: "${removedWord}"`, 'info');
    }

    predictSentences() {
        if (this.collectedWords.length === 0) {
            this.showNotification('Add some words first', 'warning');
            return;
        }

        this.socket.emit('predict_sentence', { words: this.collectedWords });
    }

    displaySentenceSuggestions(sentences) {
        this.sentenceSuggestionsEl.innerHTML = '';

        if (sentences.length === 0) {
            this.sentenceSuggestionsEl.innerHTML = '<p style="color: #718096; font-style: italic;">No suggestions available</p>';
            return;
        }

        // Add header with count
        const headerEl = document.createElement('div');
        headerEl.className = 'suggestions-header';
        headerEl.innerHTML = `
            <p style="color: #4a5568; font-weight: 500; margin-bottom: 10px;">
                <i class="fas fa-magic"></i> ${sentences.length} AI-Generated Suggestions:
            </p>
        `;
        this.sentenceSuggestionsEl.appendChild(headerEl);

        sentences.forEach((sentence, index) => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'suggestion-item';
            suggestionItem.innerHTML = `
                <div class="suggestion-content">
                    <span class="suggestion-text">${sentence}</span>
                    <small class="suggestion-meta">Suggestion ${index + 1}</small>
                </div>
                <div class="suggestion-actions">
                    <button class="btn btn-primary btn-sm" onclick="gestureChat.selectSentence('${sentence.replace(/'/g, "\\'")}')">
                        <i class="fas fa-check"></i> Select
                    </button>
                    <button class="btn btn-success btn-sm" onclick="gestureChat.sendSentenceDirectly('${sentence.replace(/'/g, "\\'")}')">
                        <i class="fas fa-paper-plane"></i> Send
                    </button>
                </div>
            `;
            this.sentenceSuggestionsEl.appendChild(suggestionItem);
        });
    }

    selectSentence(sentence) {
        this.messageInputEl.value = sentence;
        this.showNotification('Sentence selected', 'success');
    }

    sendSentenceDirectly(sentence) {
        this.messageInputEl.value = sentence;
        this.sendMessage();
        this.showNotification('Message sent!', 'success');
    }

    sendMessage() {
        const message = this.messageInputEl.value.trim();
        if (!message) {
            this.showNotification('Please enter a message', 'warning');
            return;
        }

        const messageData = {
            message: message,
            timestamp: new Date().toLocaleTimeString(),
            user: 'You'
        };

        this.socket.emit('send_message', messageData);
        this.messageInputEl.value = '';
    }

    displayMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${data.user === 'You' ? 'sent' : 'received'}`;

        const timeSpan = document.createElement('small');
        timeSpan.style.opacity = '0.7';
        timeSpan.textContent = ` (${data.timestamp})`;

        messageDiv.innerHTML = `
            <strong>${data.user}:</strong> ${data.message}
            ${timeSpan.outerHTML}
        `;

        this.chatMessagesEl.appendChild(messageDiv);
        this.chatMessagesEl.scrollTop = this.chatMessagesEl.scrollHeight;
    }

    updateConnectionStatus(connected) {
        const icon = this.connectionStatusEl.querySelector('i');
        const text = this.connectionStatusEl.querySelector('span') || this.connectionStatusEl;

        if (connected) {
            icon.className = 'fas fa-circle text-success';
            text.textContent = ' Connected';
        } else {
            icon.className = 'fas fa-circle text-danger';
            text.textContent = ' Disconnected';
        }
    }

    updateCameraStatus(active) {
        const icon = this.cameraStatusEl.querySelector('i');
        const text = this.cameraStatusEl.querySelector('span') || this.cameraStatusEl;

        if (active) {
            icon.className = 'fas fa-video text-success';
            text.textContent = ' Camera On';
        } else {
            icon.className = 'fas fa-video-slash text-danger';
            text.textContent = ' Camera Off';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        // Set background color based on type
        const colors = {
            success: '#48bb78',
            error: '#f56565',
            warning: '#ed8936',
            info: '#4299e1'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        notification.textContent = message;
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gestureChat = new GestureChat();
});
