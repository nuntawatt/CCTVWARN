# app.py - Main application file for the Person Detection System (Improved)

import os
import time
from datetime import datetime
from flask import Flask, Response, render_template, request, jsonify, send_from_directory, url_for
from camera import CameraSystem
from db import Database
from utils import ensure_dirs


timestamp = datetime.now()
# Define data directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "detection_data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
LOG_DIR = os.path.join(DATA_DIR, "logs")

# Ensure directories exist
ensure_dirs([DATA_DIR, IMAGES_DIR, LOG_DIR])

# Initialize Flask app
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# RTSP camera 
rtsp_cameras = {
    "Front Gate Camera": "rtsp://rsrc2:rsrc1234@7dd608e038a9.sn.mynetname.net/chID=9&streamType=main",
    "Main Entrance": "rtsp://rsrc2:rsrc1234@7dd608e038a9.sn.mynetname.net/chID=2&streamType=main", 
    "Parking Area": "rtsp://rsrc2:rsrc1234@608905d16e93.sn.mynetname.net/chID=1&streamType=sub",
    "Lobby Camera": "rtsp://rsrc2:rsrc1234@608905d16e93.sn.mynetname.net/chID=2&streamType=sub",
    "Test": "rtsp://rsrc2:rsrc@1234@7dd60820bd0e.sn.mynetname.net:554/unicast/c1/s1/live"
}

# Optimized settings
DETECTION_SETTINGS = {
    'confidence_threshold': 0.55,
    'detection_interval': 180,  
    'frame_rate': 30,              
    'enable_notifications': True,
    'save_images': True,
    'telegram_token': '8174302723:AAGhfjOKjkTYH4lj4VVko9tN9lNiojQJDJk',
    'telegram_chat_id': '-4815636892',
    'flask_host': 'http://localhost:5000'
}

# Initialize the camera system with optimized settings
camera_system = CameraSystem(rtsp_cameras, IMAGES_DIR, DETECTION_SETTINGS)

# Initialize the database
db = Database(
    host="localhost",
    user="root",
    password="",
    database="detect_db"
)

# Global variables
active_camera = list(rtsp_cameras.keys())[0]

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                         cameras=list(rtsp_cameras.keys()),
                         settings=DETECTION_SETTINGS)

@app.route('/video_feed')
def video_feed():
    """Video streaming route with optimized frame rate"""
    camera_id = request.args.get('camera_id', active_camera)
    
    def generate():
        while True:
            frame_bytes = camera_system.get_jpeg(camera_id)
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.03)  # ~33ms for smooth 30fps
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/switch_camera/<camera_id>')
def switch_camera(camera_id):
    """Switch the active camera"""
    global active_camera
    if camera_id in camera_system.cameras:
        active_camera = camera_id
        return jsonify({"status": "success", "message": f"Switched to {camera_id}"})
    return jsonify({"status": "error", "message": "Camera not found"})

@app.route('/get_all_detections')
def get_all_detections():
    total_counts = db.get_total_counts()
    recent_all = db.get_recent_detections_all(limit=30)

    for det in recent_all:
        if isinstance(det["timestamp"], datetime):
            det["timestamp"] = det["timestamp"].isoformat()
        if isinstance(det.get("created_at"), datetime):
            det["created_at"] = det["created_at"].isoformat()

    return jsonify({
        "total_counts": total_counts,
        "recent_detections": recent_all
    })

@app.route('/get_images/<date>/<camera_id>')
def get_images_list(date, camera_id):
    """Get list of saved images for a specific date and camera"""
    camera_image_dir = os.path.join(IMAGES_DIR, date, camera_id)
    
    if not os.path.exists(camera_image_dir):
        return jsonify({"images": []})
    
    images = [f for f in os.listdir(camera_image_dir) if f.endswith('.jpg')]
    images.sort(reverse=True)  # Newest first
    
    return jsonify({"images": images})

@app.route('/image/<path:image_path>')
def serve_image(image_path):
    directory = os.path.dirname(image_path)
    filename = os.path.basename(image_path)
    return send_from_directory(os.path.join(IMAGES_DIR, directory), filename)

@app.route('/download_images/<date>/<camera_id>')
def download_images(date, camera_id):
    import zipfile
    from io import BytesIO
    
    camera_image_dir = os.path.join(IMAGES_DIR, date, camera_id)
    
    if not os.path.exists(camera_image_dir):
        return jsonify({"status": "error", "message": "No images found"}), 404
    
    # Create a zip file in memory
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for image in os.listdir(camera_image_dir):
            if image.endswith('.jpg'):
                image_path = os.path.join(camera_image_dir, image)
                zf.write(image_path, image)
    
    memory_file.seek(0)
    
    return Response(
        memory_file,
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename={camera_id}_{date}_detections.zip'
        }
    )

@app.route('/export_csv')
def export_csv():
    """Export detection data to CSV"""
    import csv
    from io import StringIO
    
    # Get all detections from database
    all_detections = db.get_all_detections()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Camera', 'Timestamp', 'Confidence', 'Image Path'])
    
    # Write data
    for detection in all_detections:
        writer.writerow([
            detection['id'],
            detection['camera_id'],
            detection['timestamp'],
            detection['confidence'],
            detection.get('image_path', '')
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=detections_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

@app.route('/start_all_cameras')
def start_all_cameras():
    """Start all cameras"""
    camera_system.start_all()
    return jsonify({"status": "success", "message": "All cameras started successfully"})

@app.route('/get_system_stats')
def get_system_stats():
    """Get system statistics"""
    import psutil
    
    stats = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "active_cameras": len([cam for cam in camera_system.cameras.values() if cam.running]),
        "total_cameras": len(camera_system.cameras),
        "uptime": time.time() - camera_system.start_time if hasattr(camera_system, 'start_time') else 0
    }
    
    return jsonify(stats)

from datetime import datetime

@app.route('/update_detection', methods=['POST'])
def update_detection():
    data = request.json
    
    if not data:
        print("No data received in /update_detection")
        return jsonify({"status": "error", "message": "No data provided"}), 400

    print("Received detection data:", data)
    
    try:
        db.add_detection(
            camera_id=data['camera_id'],
            timestamp=datetime.now().isoformat(),
            confidence=data['confidence'],
            image_path=data.get('image_path', '')
        )

        print(f"Detection from {data['camera_id']} saved to DB")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Error in /update_detection: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_detection', methods=['DELETE'])
def delete_detection():
    detection_id = request.args.get('id', type=int)
    if detection_id is None:
        return jsonify({'status': 'error', 'message': 'Missing detection ID'}), 400

    try:
        db._connect()
        db.cursor.execute("SELECT id, camera_id FROM detections WHERE id = %s", (detection_id,))
        row = db.cursor.fetchone()
        db._disconnect()

        if row is None:
            return jsonify({'status': 'error', 'message': 'Detection not found'}), 404

        db._connect()
        db.cursor.execute("DELETE FROM detections WHERE id = %s", (detection_id,))
        db.conn.commit()
        db._disconnect()

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Debug route to check paths
@app.route('/debug_paths')
def debug_paths():
    """Debug route to check paths"""
    paths = {
        "base_dir": BASE_DIR,
        "data_dir": DATA_DIR,
        "images_dir": IMAGES_DIR,
        "static_url": url_for('static', filename='js/main.js'),
        "css_url": url_for('static', filename='css/style.css'),
        "static_folder": app.static_folder,
        "template_folder": app.template_folder,
    }
    
    # Check if files exist
    paths["main_js_exists"] = os.path.exists(os.path.join(app.static_folder, 'js/main.js'))
    paths["style_css_exists"] = os.path.exists(os.path.join(app.static_folder, 'css/style.css'))
    paths["index_html_exists"] = os.path.exists(os.path.join(app.template_folder, 'index.html'))

    return jsonify(paths)

if __name__ == '__main__':
    try:
        print("Starting NT Telecom Person Detection System...")
        print(f"Detection Settings: {DETECTION_SETTINGS}")
        
        # Initialize database tables
        db.initialize()
        
        # Set start time
        camera_system.start_time = time.time()

        # Start all cameras
        camera_system.start_all()
        
        print("🎥 System running at http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=False) 
    except KeyboardInterrupt:
        print("Shutting down...")
        camera_system.stop_all()
    except Exception as e:
        print(f"Error: {e}")
        camera_system.stop_all()