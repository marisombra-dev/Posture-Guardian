"""
Posture Guardian Desktop App 🌿
A gentle companion that watches your posture and sends overlay alerts
"""

import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
import math

class PostureGuardian:
    def __init__(self):
        # MediaPipe setup
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # State
        self.good_posture = None
        self.bad_posture_counter = 0
        self.sensitivity = 8  # degrees (more sensitive by default)
        self.alert_duration = 3  # seconds
        self.last_alert_time = 0
        self.monitoring = False
        self.calibrating = False
        
        # Camera
        self.cap = None
        
        # GUI
        self.root = None
        self.video_label = None
        self.status_label = None
        self.alert_window = None
        
    def calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points"""
        radians = math.atan2(p3.y - p2.y, p3.x - p2.x) - \
                  math.atan2(p1.y - p2.y, p1.x - p2.x)
        angle = abs(radians * 180.0 / math.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def check_posture(self, landmarks):
        """Analyze posture from landmarks"""
        try:
            # Get key landmarks
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
            right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            
            # Calculate shoulder slope
            shoulder_slope = abs(
                math.atan2(right_shoulder.y - left_shoulder.y, 
                          right_shoulder.x - left_shoulder.x) * 180 / math.pi
            )
            
            # Calculate neck angle
            avg_ear = type('obj', (object,), {
                'x': (left_ear.x + right_ear.x) / 2,
                'y': (left_ear.y + right_ear.y) / 2
            })()
            avg_shoulder = type('obj', (object,), {
                'x': (left_shoulder.x + right_shoulder.x) / 2,
                'y': (left_shoulder.y + right_shoulder.y) / 2
            })()
            avg_hip = type('obj', (object,), {
                'x': (left_hip.x + right_hip.x) / 2,
                'y': (left_hip.y + right_hip.y) / 2
            })()
            
            neck_angle = self.calculate_angle(avg_hip, avg_shoulder, avg_ear)
            
            # Forward head posture
            head_forward = avg_ear.x > avg_shoulder.x + 0.05
            
            return {
                'shoulder_slope': shoulder_slope,
                'neck_angle': neck_angle,
                'head_forward': head_forward
            }
        except:
            return None
    
    def show_alert(self):
        """Show system-wide overlay alert"""
        current_time = time.time()
        if current_time - self.last_alert_time < self.alert_duration:
            return
        
        self.last_alert_time = current_time
        
        # Create overlay window
        if self.alert_window:
            try:
                self.alert_window.destroy()
            except:
                pass
        
        self.alert_window = tk.Toplevel()
        self.alert_window.title("Posture Alert")
        
        # Make it appear over everything
        self.alert_window.attributes('-topmost', True)
        self.alert_window.attributes('-alpha', 0.95)
        
        # Remove window decorations
        self.alert_window.overrideredirect(True)
        
        # Center on screen
        screen_width = self.alert_window.winfo_screenwidth()
        screen_height = self.alert_window.winfo_screenheight()
        
        width = 500
        height = 200
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.alert_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Style
        self.alert_window.configure(bg='#FF3B30')
        
        # Content
        frame = tk.Frame(self.alert_window, bg='#FF3B30')
        frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        warning_label = tk.Label(
            frame,
            text="⚠️ Check Your Posture ⚠️",
            font=('Helvetica', 24, 'bold'),
            bg='#FF3B30',
            fg='white'
        )
        warning_label.pack()
        
        message_label = tk.Label(
            frame,
            text="Sit up straight 💚",
            font=('Helvetica', 16),
            bg='#FF3B30',
            fg='white'
        )
        message_label.pack(pady=10)
        
        # Auto-close after duration
        self.alert_window.after(int(self.alert_duration * 1000), 
                               lambda: self.alert_window.destroy() if self.alert_window else None)
    
    def update_status(self, text, color='white'):
        """Update status label"""
        if self.status_label:
            self.status_label.config(text=text, fg=color)
    
    def calibrate_posture(self):
        """Calibrate good posture"""
        self.calibrating = True
        self.good_posture = None
        self.update_status("📸 Sit with good posture... capturing in 3 seconds!", "yellow")
        
        def finish_calibration():
            time.sleep(3)
            self.calibrating = False
            if self.good_posture:
                self.update_status("✓ Good posture calibrated! Monitoring...", "lightgreen")
                self.monitoring = True
        
        threading.Thread(target=finish_calibration, daemon=True).start()
    
    def process_frame(self):
        """Process camera frame and check posture"""
        if not self.cap or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # Flip frame horizontally for mirror view
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.pose.process(rgb_frame)
        
        # Draw landmarks
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
            
            # Check posture
            posture = self.check_posture(results.pose_landmarks.landmark)
            
            if posture:
                # Calibration mode
                if self.calibrating and not self.good_posture:
                    self.good_posture = posture.copy()
                
                # Monitoring mode
                elif self.monitoring and self.good_posture:
                    shoulder_diff = abs(posture['shoulder_slope'] - 
                                      self.good_posture['shoulder_slope'])
                    neck_diff = abs(posture['neck_angle'] - 
                                   self.good_posture['neck_angle'])
                    
                    # Debug: print values
                    print(f"Shoulder diff: {shoulder_diff:.1f}° | Neck diff: {neck_diff:.1f}° | Sensitivity: {self.sensitivity}°")
                    
                    is_bad_posture = (shoulder_diff > self.sensitivity or 
                                    neck_diff > self.sensitivity or
                                    (posture['head_forward'] and 
                                     not self.good_posture['head_forward']))
                    
                    if is_bad_posture:
                        self.bad_posture_counter += 1
                        print(f"Bad posture counter: {self.bad_posture_counter}")
                        if self.bad_posture_counter > 5:  # ~1 second instead of 2
                            self.show_alert()
                            self.update_status("⚠️ Poor posture detected!", "red")
                    else:
                        self.bad_posture_counter = 0
                        self.update_status("✓ Good posture! Keep it up 💚", "lightgreen")
        else:
            self.update_status("👤 No person detected", "white")
        
        # Display frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))
        
        # Convert to PhotoImage
        from PIL import Image, ImageTk
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        
        if self.video_label:
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        # Schedule next frame
        if self.root:
            self.root.after(33, self.process_frame)  # ~30 FPS
    
    def create_gui(self):
        """Create the main GUI window"""
        self.root = tk.Tk()
        self.root.title("Posture Guardian 🌿")
        self.root.geometry("700x700")
        self.root.configure(bg='#667eea')
        
        # Title
        title = tk.Label(
            self.root,
            text="Posture Guardian 🌿",
            font=('Helvetica', 28, 'bold'),
            bg='#667eea',
            fg='white'
        )
        title.pack(pady=20)
        
        # Video frame
        video_frame = tk.Frame(self.root, bg='black')
        video_frame.pack(pady=10)
        
        self.video_label = tk.Label(video_frame, bg='black')
        self.video_label.pack()
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="🎯 Click 'Calibrate' to start",
            font=('Helvetica', 14),
            bg='#667eea',
            fg='white',
            pady=15
        )
        self.status_label.pack()
        
        # Controls
        controls_frame = tk.Frame(self.root, bg='#667eea')
        controls_frame.pack(pady=10)
        
        calibrate_btn = tk.Button(
            controls_frame,
            text="Calibrate Good Posture",
            command=self.calibrate_posture,
            font=('Helvetica', 12, 'bold'),
            bg='white',
            fg='#667eea',
            padx=20,
            pady=10,
            relief='raised',
            cursor='hand2'
        )
        calibrate_btn.pack()
        
        # Settings
        settings_frame = tk.LabelFrame(
            self.root,
            text="Settings",
            font=('Helvetica', 12, 'bold'),
            bg='#667eea',
            fg='white',
            padx=20,
            pady=20
        )
        settings_frame.pack(pady=20, padx=20, fill='x')
        
        # Sensitivity slider
        sens_frame = tk.Frame(settings_frame, bg='#667eea')
        sens_frame.pack(fill='x', pady=5)
        
        tk.Label(
            sens_frame,
            text="Alert Sensitivity (lower = stricter):",
            bg='#667eea',
            fg='white',
            font=('Helvetica', 10)
        ).pack(side='left')
        
        self.sens_value = tk.Label(
            sens_frame,
            text="12°",
            bg='#667eea',
            fg='white',
            font=('Helvetica', 10, 'bold')
        )
        self.sens_value.pack(side='right')
        
        sens_slider = ttk.Scale(
            settings_frame,
            from_=5,
            to=20,
            value=12,
            orient='horizontal',
            command=lambda v: self.update_sensitivity(float(v))
        )
        sens_slider.pack(fill='x', pady=5)
        
        # Duration slider
        dur_frame = tk.Frame(settings_frame, bg='#667eea')
        dur_frame.pack(fill='x', pady=5)
        
        tk.Label(
            dur_frame,
            text="Alert Duration:",
            bg='#667eea',
            fg='white',
            font=('Helvetica', 10)
        ).pack(side='left')
        
        self.dur_value = tk.Label(
            dur_frame,
            text="3s",
            bg='#667eea',
            fg='white',
            font=('Helvetica', 10, 'bold')
        )
        self.dur_value.pack(side='right')
        
        dur_slider = ttk.Scale(
            settings_frame,
            from_=1,
            to=10,
            value=3,
            orient='horizontal',
            command=lambda v: self.update_duration(float(v))
        )
        dur_slider.pack(fill='x', pady=5)
        
        # Start camera
        self.cap = cv2.VideoCapture(0)
        self.process_frame()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()
    
    def update_sensitivity(self, value):
        """Update sensitivity setting"""
        self.sensitivity = int(value)
        self.sens_value.config(text=f"{self.sensitivity}°")
    
    def update_duration(self, value):
        """Update alert duration setting"""
        self.alert_duration = int(value)
        self.dur_value.config(text=f"{self.alert_duration}s")
    
    def on_closing(self):
        """Clean up on window close"""
        self.monitoring = False
        if self.cap:
            self.cap.release()
        if self.root:
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.create_gui()

if __name__ == "__main__":
    app = PostureGuardian()
    app.run()
