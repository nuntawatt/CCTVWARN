# utils.py - Enhanced utility functions for the person detection system

import os
import requests
import time
from datetime import datetime

# Telegram Configuration (Fixed optimal values)
TELEGRAM_BOT_TOKEN = '8174302723:AAGhfjOKjkTYH4lj4VVko9tN9lNiojQJDJk'
TELEGRAM_CHAT_ID = '-4815636892'

# Rate limiting for notifications
last_notification_time = {}
NOTIFICATION_COOLDOWN = 30  # 30 seconds between notifications from same camera

def ensure_dirs(directory_list):
    """Ensure directories exist"""
    for directory in directory_list:
        os.makedirs(directory, exist_ok=True)

def send_telegram_alert(message):
    """Send alert message to Telegram with rate limiting"""
    try:
        # Basic rate limiting to prevent spam
        current_time = time.time()
        camera_key = "general"
        
        if camera_key in last_notification_time:
            time_diff = current_time - last_notification_time[camera_key]
            if time_diff < NOTIFICATION_COOLDOWN:
                print(f"Skipping notification due to rate limit ({time_diff:.1f}s < {NOTIFICATION_COOLDOWN}s)")
                return False
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            last_notification_time[camera_key] = current_time
            return True
        else:
            print(f"Telegram Error ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
        return False

def send_telegram_photo(image_path, caption):
    """Send photo with caption to Telegram with enhanced error handling"""
    try:
        # Check if file exists and is readable
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False
        
        if os.path.getsize(image_path) == 0:
            print(f"Image file is empty: {image_path}")
            return False
        
        # Rate limiting for photo notifications
        current_time = time.time()
        photo_key = "photo"
        
        if photo_key in last_notification_time:
            time_diff = current_time - last_notification_time[photo_key]
            if time_diff < NOTIFICATION_COOLDOWN:
                print(f"⏰ Skipping photo notification due to rate limit")
                return False
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        # Send photo with enhanced error handling
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            last_notification_time[photo_key] = current_time
            return True
        else:
            print(f"Telegram Photo Error ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"Failed to send Telegram photo: {e}")
        return False

def get_datetime_str(format="%Y-%m-%d %H:%M:%S"):
    """Get current datetime as string"""
    return datetime.now().strftime(format)

def get_date_str(format="%Y-%m-%d"):
    """Get current date as string"""
    return datetime.now().strftime(format)

def format_time_diff(seconds):
    """Format time difference in seconds to human-readable string (Thai/English)"""
    if seconds < 60:
        return f"{seconds:.0f} seconds | วินาที"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f} minutes | นาที"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f} hours | ชั่วโมง"
    else:
        days = seconds / 86400
        return f"{days:.1f} days | วัน"

def is_gpu_available():
    """Check if GPU is available for processing"""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

def get_gpu_info():
    """Get GPU information"""
    try:
        import torch
        if not torch.cuda.is_available():
            return "GPU not available | GPU ไม่พร้อมใช้งาน"
        
        gpu_count = torch.cuda.device_count()
        gpu_info = []
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory // (1024**3)
            gpu_info.append(f"GPU {i}: {gpu_name} ({gpu_memory}GB)")
        
        return "\n".join(gpu_info)
    except:
        return "Could not retrieve GPU information | ไม่สามารถดึงข้อมูล GPU ได้"

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def get_system_info():
    """Get comprehensive system information"""
    try:
        import psutil
        
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = format_bytes(memory.used)
        memory_total = format_bytes(memory.total)
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = format_bytes(disk.used)
        disk_total = format_bytes(disk.total)
        
        return {
            "cpu": {
                "usage": cpu_percent,
                "cores": cpu_count
            },
            "memory": {
                "usage_percent": memory_percent,
                "used": memory_used,
                "total": memory_total
            },
            "disk": {
                "usage_percent": disk_percent,
                "used": disk_used,
                "total": disk_total
            },
            "gpu": get_gpu_info()
        }
    except Exception as e:
        print(f"Error getting system info: {e}")
        return {
            "cpu": {"usage": 0, "cores": 0},
            "memory": {"usage_percent": 0, "used": "0 B", "total": "0 B"},
            "disk": {"usage_percent": 0, "used": "0 B", "total": "0 B"},
            "gpu": "Error retrieving GPU info"
        }

def test_telegram_connection():
    """Test Telegram bot connection"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result'].get('username', 'Unknown')
                return True, f"Connected to bot: @{bot_name}"
            else:
                return False, "Bot authentication failed"
        else:
            return False, f"HTTP Error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def clean_old_images(images_dir, days_to_keep=7):
    """Clean up old images to save disk space"""
    try:
        import time
        from pathlib import Path
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        deleted_count = 0
        
        for root, dirs, files in os.walk(images_dir):
            for file in files:
                if file.endswith('.jpg'):
                    file_path = os.path.join(root, file)
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
        
        print(f"Cleaned up {deleted_count} old images")
        return deleted_count
        
    except Exception as e:
        print(f"Error cleaning old images: {e}")
        return 0