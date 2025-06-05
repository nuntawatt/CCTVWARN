# camera.py - Improved camera handling and person detection

import cv2
import numpy as np
import threading
import time
import os
import subprocess as sp
from datetime import datetime, timedelta
import queue
import hashlib
import torch
from ultralytics import YOLO
from utils import send_telegram_alert, send_telegram_photo

class Camera:
    def __init__(self, camera_id, rtsp_url, images_dir, settings):
        self.camera_id = camera_id
        self.safe_camera_id = camera_id.replace(' ', '_').replace('/', '_')
        self.rtsp_url = rtsp_url
        self.images_dir = images_dir
        self.settings = settings
        
        # Detection interval (default 3 minutes)
        self.detection_interval = settings.get('detection_interval', 180)
        
        # Frame handling with higher frame rate
        self.frame = None
        self.annotated_frame = None
        self.running = False
        self.lock = threading.Lock()
        
        # Enhanced frame buffer for smoother video (increased buffer size)
        self.frame_buffer = []
        self.buffer_size = 5  # Increased from 3 to 5 for smoother playback
        
        # Optimized detection settings
        self.process_every_n_frames = 2  # Process every 2nd frame for better performance
        self.frame_count = 0
        self.detection_results = None
        
        # Enhanced person tracking to avoid duplicate detections
        self.detected_persons = {}  # Hash -> {'timestamp': datetime, 'bbox': tuple, 'notified': bool}
        self.detection_queue = queue.Queue()
        
        # Create directory for this camera
        self.today_dir = datetime.now().strftime("%Y%m%d")
        self.camera_image_dir = os.path.join(images_dir, self.today_dir, camera_id.replace(' | ', '_').replace(' ', '_'))
        os.makedirs(self.camera_image_dir, exist_ok=True)
        
        # Performance tracking
        self.last_fps_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0
    
    def start(self):
        """Start camera threads"""
        if not self.running:
            self.running = True
            threading.Thread(target=self.update_frame, daemon=True).start()
            threading.Thread(target=self.detect_objects, daemon=True).start()
            threading.Thread(target=self.process_detections, daemon=True).start()
            print(f"📷 Started camera: {self.camera_id}")
    
    def stop(self):
        """Stop camera threads"""
        self.running = False
    
    def update_frame(self):
        """Update camera frames using FFmpeg with optimized settings for high frame rate"""
        # Optimized frame settings for smooth video
        frame_width = 1280  # Increased resolution for better quality
        frame_height = 720
        frame_size = frame_width * frame_height * 3
        
        while self.running:
            try:
                # Enhanced FFmpeg settings for high frame rate and smooth video
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-rtsp_transport', 'tcp',
                    '-i', self.rtsp_url,
                    '-loglevel', 'error',
                    '-an',  # Disable audio
                    '-f', 'image2pipe',
                    '-pix_fmt', 'bgr24',
                    '-vcodec', 'rawvideo',
                    '-vf', f'scale={frame_width}:{frame_height}',
                    '-r', str(self.settings.get('frame_rate', 30)),  # High frame rate
                    '-probesize', '32',
                    '-analyzeduration', '0',
                    '-fflags', 'nobuffer',
                    '-flags', 'low_delay',
                    '-'
                ]
                
                pipe = sp.Popen(ffmpeg_cmd, stdout=sp.PIPE, bufsize=10**7)
                
                while self.running:
                    raw_image = pipe.stdout.read(frame_size)
                    if len(raw_image) != frame_size:
                        print(f"Cannot read data from camera {self.camera_id}")
                        break

                    frame = np.frombuffer(raw_image, dtype='uint8').reshape((frame_height, frame_width, 3))
                    
                    # Calculate FPS
                    self.fps_counter += 1
                    current_time = time.time()
                    if current_time - self.last_fps_time >= 1.0:
                        self.current_fps = self.fps_counter
                        self.fps_counter = 0
                        self.last_fps_time = current_time
                    
                    with self.lock:
                        self.frame = frame
                        
                        # Enhanced frame buffer for smoother processing
                        if len(self.frame_buffer) >= self.buffer_size:
                            self.frame_buffer.pop(0)
                        self.frame_buffer.append(frame.copy())
                
                pipe.terminate()
                
            except Exception as e:
                print(f"Error connecting to camera {self.camera_id}: {e}")
                time.sleep(1)
    
    def detect_objects(self):
        """Detect persons in camera frames with enhanced tracking"""
        # Set CUDA device if available
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        print(f"🖥️ Using device for detection: {device}")
        
        # Load optimized YOLO model
        model = YOLO("yolov8n.pt").to(device)
        
        # Person class ID in COCO dataset
        PERSON_CLASS_ID = 0
        
        # Check if directories are updated for today
        self._update_date_folders()
        
        while self.running:
            try:
                # Update directories if date changed
                self._update_date_folders()
                
                # Enhanced frame processing for smoother detection
                self.frame_count += 1
                if self.frame_count % self.process_every_n_frames != 0:
                    time.sleep(0.01)
                    continue
                
                with self.lock:
                    if self.frame is None or len(self.frame_buffer) == 0:
                        time.sleep(0.01)
                        continue
                    # Use latest frame from buffer
                    current_frame = self.frame_buffer[-1].copy()
                
                # Enhanced YOLO detection with optimized parameters
                results = model.predict(
                    source=current_frame,
                    imgsz=640,
                    conf=self.settings.get('confidence_threshold', 0.55),
                    classes=[PERSON_CLASS_ID],
                    max_det=15,  # Reasonable limit for performance
                    verbose=False,
                    device=device
                )
                
                result = results[0]
                boxes = result.boxes
                
                # Create enhanced annotated frame
                annotated = current_frame.copy()
                
                # Get current timestamp
                current_time = datetime.now()
                timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Enhanced annotation with better visualization
                new_detections = []
                
                for box in boxes:
                    # Get coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0].item())

                    # Enhanced person tracking with position and size
                    person_width = x2 - x1
                    person_height = y2 - y1
                    person_center_x = (x1 + x2) // 2
                    person_center_y = (y1 + y2) // 2
                    person_area = person_width * person_height
                    
                    # Create unique identifier based on position, size, and area
                    person_hash = hashlib.md5(
                        f"{person_center_x//50}_{person_center_y//50}_{person_area//1000}".encode()
                    ).hexdigest()
                    
                    # Enhanced bounding box with better colors
                    color = (0, 255, 0) if conf > 0.7 else (0, 165, 255)  # Green for high conf, orange for medium
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
                    
                    # Enhanced confidence text with background
                    conf_text = f"Person: {conf:.1%}"
                    text_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(annotated, (x1, y1 - text_size[1] - 10), 
                                 (x1 + text_size[0], y1), color, -1)
                    cv2.putText(annotated, conf_text, (x1, y1 - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Enhanced duplicate detection logic
                    is_new_detection = False
                    
                    if person_hash not in self.detected_persons:
                        is_new_detection = True
                        self.detected_persons[person_hash] = {
                            'timestamp': current_time,
                            'bbox': (x1, y1, x2, y2),
                            'notified': False
                        }
                    else:
                        last_detection = self.detected_persons[person_hash]
                        time_diff = (current_time - last_detection['timestamp']).total_seconds()
                        
                        # Check if detection interval has passed
                        if time_diff > self.detection_interval:
                            is_new_detection = True
                            self.detected_persons[person_hash] = {
                                'timestamp': current_time,
                                'bbox': (x1, y1, x2, y2),
                                'notified': False
                            }
                    
                    if is_new_detection:
                        # Add to detection queue for processing
                        detection_info = {
                            'camera_id': self.camera_id,
                            'timestamp': timestamp,
                            'confidence': round(conf * 100, 2),
                            'box': (x1, y1, x2, y2),
                            'frame': current_frame.copy(),
                            'person_hash': person_hash
                        }
                        
                        new_detections.append(detection_info)
                
                # Enhanced camera info overlay
                info_bg_height = 80
                cv2.rectangle(annotated, (0, 0), (annotated.shape[1], info_bg_height), (0, 0, 0, 180), -1)
                
                # Camera name and timestamp
                cv2.putText(annotated, f"{self.camera_id}",
                           (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(annotated, f"{timestamp}",
                           (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                
                # FPS and detection info
                cv2.putText(annotated, f"FPS: {self.current_fps}",
                           (annotated.shape[1] - 120, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                if len(new_detections) > 0:
                    cv2.putText(annotated, f"Detected: {len(new_detections)}",
                               (annotated.shape[1] - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # NT Telecom branding
                cv2.putText(annotated, "NT Telecom AI",
                           (annotated.shape[1] - 180, annotated.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                
                # Update annotated frame
                with self.lock:
                    self.annotated_frame = annotated
                    self.detection_results = result
                
                # Process new detections
                if new_detections:
                    for detection in new_detections:
                        self.detection_queue.put(detection)
                
                # Optimized sleep for high frame rate
                time.sleep(0.005)  # 5ms sleep for very smooth processing
                
            except Exception as e:
                print(f"❌ Error detecting objects from camera {self.camera_id}: {e}")
                time.sleep(0.2)
    
    def process_detections(self):
        """Process detections from the queue with enhanced notifications"""
        while self.running:
            try:
                # Get detection from queue
                try:
                    detection = self.detection_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Extract detection info
                camera_id = detection['camera_id']
                timestamp = detection['timestamp']
                confidence = detection['confidence']
                person_hash = detection['person_hash']
                frame = detection['frame']
                box = detection['box']
                
                # Enhanced filename generation
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
                filename = f"person_{timestamp_str}_{confidence:.0f}.jpg"
                image_path = os.path.join(self.camera_image_dir, filename)
                
                # Save the image with enhanced quality
                cv2.imwrite(image_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                # Create relative path for database
                date_str = datetime.now().strftime("%Y%m%d")
                rel_image_path = f"{date_str}/{camera_id.replace(' ', '_').replace('/', '_')}/{filename}"

                # Enhanced alert message
                alert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                alert_message = f"""
🚨 <b>Person Detected | ตรวจพบบุคคล</b>

<b>Camera | กล้อง:</b> {camera_id}
<b>Detection | การตรวจจับ:</b> Person
<b>Confidence | ความมั่นใจ:</b> {confidence:.0f}%
<b>Time | เวลา:</b> {alert_time}
<b>Location | ตำแหน่ง:</b> Zone {camera_id.split()[-1] if camera_id.split() else 'Unknown'}

✅ <b>Image saved | บันทึกภาพแล้ว</b>
"""
                
                # Send text alert first
                if send_telegram_alert(alert_message):
                    print(f"📱 Telegram alert sent for {camera_id}")
                
                # Send image alert with enhanced caption
                image_caption = f"""
📸 <b>Detection Image | ภาพการตรวจจับ</b>

{camera_id}
{alert_time}
{confidence:.0f}% confidence
"""
                
                if send_telegram_photo(image_path, image_caption):
                    print(f"📷 Telegram photo sent for {camera_id}")
                
                # Update detection info for API
                detection['image_path'] = rel_image_path
                
                # Make HTTP request to update detection in Flask app
                self._update_detection_in_app(detection)
                
                # Mark task as done
                self.detection_queue.task_done()
                
                # Mark person as notified
                if person_hash in self.detected_persons:
                    self.detected_persons[person_hash]['notified'] = True
                
            except Exception as e:
                print(f"Error processing detection: {e}")
    
    def _update_date_folders(self):
        today = datetime.now().strftime("%Y%m%d")
        if today != self.today_dir:
            self.today_dir = today
            safe_camera_id = camera_id.replace(' ', '_').replace('/', '_')
            self.camera_image_dir = os.path.join(images_dir, self.today_dir, safe_camera_id)
            os.makedirs(self.camera_image_dir, exist_ok=True)
            self.detected_persons = {}

    def _update_detection_in_app(self, detection):
        import requests
        try:
            # frame
            data = {k: v for k, v in detection.items() if k != 'frame'}

            response = requests.post('http://localhost:5000/update_detection', json=data, timeout=2)
            if response.status_code == 200:
                print(f"Detection update sent successfully for {data['camera_id']}")
            else:
                print(f"Failed to update detection - Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error sending detection update: {e}")
    
    def get_frame(self):
        """Get the current frame"""
        with self.lock:
            if self.annotated_frame is not None:
                return self.annotated_frame
            elif self.frame is not None:
                return self.frame
            return None

    def get_jpeg(self):
        """Get JPEG encoded frame with enhanced quality"""
        frame = self.get_frame()
        if frame is not None:
            # Enhanced JPEG encoding for better quality and smooth streaming
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 90]  # Increased quality
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            if ret:
                return buffer.tobytes()
        return None
    
    def reset_detection_tracking(self):
        """Reset person detection tracking"""
        self.detected_persons = {}
    
    def cleanup_old_detections(self):
        """Clean up old detection records to prevent memory issues"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=1)  # Keep only last hour
        
        self.detected_persons = {
            person_hash: info for person_hash, info in self.detected_persons.items()
            if info['timestamp'] > cutoff_time
        }


class CameraSystem:
    def __init__(self, camera_urls, images_dir, settings):
        self.cameras = {}
        self.images_dir = images_dir
        self.settings = settings
        self.start_time = None
        
        # Create camera instances with enhanced settings
        for camera_id, url in camera_urls.items():
            self.cameras[camera_id] = Camera(camera_id, url, images_dir, settings)
    
    def start_all(self):
        """Start all cameras"""
        self.start_time = time.time()
        for camera_id, camera in self.cameras.items():
            camera.start()
        
        # Start cleanup thread
        threading.Thread(target=self._periodic_cleanup, daemon=True).start()
    
    def stop_all(self):
        """Stop all cameras"""
        for camera_id, camera in self.cameras.items():
            camera.stop()
    
    def get_jpeg(self, camera_id):
        """Get JPEG frame from a specific camera"""
        if camera_id in self.cameras:
            return self.cameras[camera_id].get_jpeg()
        return None
    
    def reset_all_detection_tracking(self):
        """Reset detection tracking for all cameras"""
        for camera_id, camera in self.cameras.items():
            camera.reset_detection_tracking()
    
    def _periodic_cleanup(self):
        """Periodic cleanup to maintain system performance"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                for camera_id, camera in self.cameras.items():
                    camera.cleanup_old_detections()
                print("Performed periodic cleanup")
            except Exception as e:
                print(f"Error in periodic cleanup: {e}")
                time.sleep(60)  # Wait 1 minute before retry