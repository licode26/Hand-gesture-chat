#!/usr/bin/env python3
"""
Gesture Chat Setup Script
This script helps set up the Gesture Chat application.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 3.7 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def check_camera_access():
    """Check if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Camera access verified")
            cap.release()
            return True
        else:
            print("⚠ Camera not accessible - please check camera permissions")
            return False
    except ImportError:
        print("⚠ OpenCV not installed - will be installed with dependencies")
        return True

def main():
    """Main setup function"""
    print("=" * 50)
    print("Gesture Chat Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Setup failed during dependency installation")
        sys.exit(1)
    
    # Check camera access
    check_camera_access()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print("\nTo start the application:")
    print("1. Run: python app.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Click 'Tutorial' to learn the gestures")
    print("4. Start the camera and begin communicating!")
    print("\nNote: Make sure your camera is connected and permissions are granted.")

if __name__ == "__main__":
    main()
