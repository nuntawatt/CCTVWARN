# 🎯 NT Telecom - AI Person Detection System

ระบบตรวจจับบุคคลอัจฉริยะจากกล้องวงจรปิดแบบเรียลไทม์ ใช้ YOLOv8 ตรวจจับ "บุคคล (person)" พร้อมส่งแจ้งเตือนผ่าน Telegram และแสดงข้อมูลผ่านแดชบอร์ดแบบโต้ตอบ

---

## ฟีเจอร์หลัก

- รองรับกล้องหลายตัวผ่าน RTSP (แสดงสดและบันทึก)
- ตรวจจับบุคคลแบบเรียลไทม์ด้วย YOLOv8
- บันทึกภาพ-เวลา พร้อมลงฐานข้อมูล MySQL/MariaDB
- แจ้งเตือนผ่าน Telegram พร้อมภาพ
- แดชบอร์ดกราฟิกพร้อมสถิติและรายงาน
- ป้องกันการแจ้งเตือนซ้ำภายในช่วงเวลาที่กำหนด

---

## 🛠 โครงสร้างระบบ

- `app.py` – แอปหลัก Flask, จัดการ route และ RTSP กล้อง
- `camera.py` – ควบคุมกล้อง, การจับภาพ, ตรวจจับด้วย YOLOv8
- `db.py` – จัดการฐานข้อมูล (MySQL/MariaDB)
- `utils.py` – ฟังก์ชันเสริม: ส่ง Telegram, ทำความสะอาดข้อมูล  
- `static/`, `templates/` – ส่วนหน้าเว็บ (HTML, CSS, JS)  
- `detection_data/` – ภาพตรวจจับและ log ที่เก็บไว้

---

## เริ่มต้นใช้งาน

1. ติดตั้งไลบรารีที่ต้องใช้  
```bash
pip install -r requirements.txt

2. ดาวน์โหลดโมเดล YOLOv8 
```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

3. ตั้งค่า Telegram Bot (ผ่าน BotFather)
ใส่ TELEGRAM_BOT_TOKEN และ TELEGRAM_CHAT_ID ที่ utils.py, app.py

4. เริ่มต้นระบบ
```bash
python app.py

---

## เพิ่มกล้อง RTSP
ให้เพิ่มชื่อกล้องและลิงก์ใน 3 จุด

1. app.py
rtsp_cameras = {
    "Front Gate": "rtsp://user:pass@ip:port/stream1",
    "Lobby": "rtsp://user:pass@ip:port/stream2",
    "ชื่อกล้องใหม่": "rtsp://..."
}

2. main.js > ใน constructor ของ NTVisionDashboard
this.cameras = {
    "Front Gate": "Front Gate",
    "Lobby": "Lobby",
    "ชื่อกล้องใหม่": "ชื่อกล้องใหม่"
};

3. main.js > formatCameraName() เพื่อชื่อแสดงผลให้เรียบร้อย
"ชื่อกล้องใหม่": "ชื่อย่อที่ต้องการแสดง"

---

## ฟีเจอร์แดชบอร์ด

- ดูภาพสดจากทุกกล้องพร้อมกัน
- ตารางประวัติการตรวจจับ + ดาวน์โหลดภาพ
- กราฟสถิติรายวัน/สัปดาห์/เดือน
- รายงานแยกตามกล้อง

--- 
