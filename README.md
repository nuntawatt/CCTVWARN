# 🎯 NT Telecom - AI Person Detection System

ระบบตรวจจับบุคคลอัจฉริยะจากกล้องวงจรปิดแบบเรียลไทม์  
ใช้ YOLOv8 ตรวจจับ "บุคคล (person)" พร้อมส่งแจ้งเตือนผ่าน Telegram และแสดงข้อมูลผ่านแดชบอร์ดแบบโต้ตอบ

---

## ฟีเจอร์หลัก

- รองรับกล้องหลายตัวผ่าน RTSP (ทั้งแสดงสดและบันทึก)
- ตรวจจับบุคคลแบบเรียลไทม์ด้วย YOLOv8
- บันทึกภาพและเวลา พร้อมเก็บลงฐานข้อมูล MySQL/MariaDB
- แจ้งเตือนผ่าน Telegram พร้อมแนบรูปภาพ
- แดชบอร์ดกราฟิกแบบโต้ตอบ แสดงสถิติและรายงาน
- ป้องกันการแจ้งเตือนซ้ำภายในเวลาที่กำหนด

---

## โครงสร้างระบบ

| ไฟล์/โฟลเดอร์        | หน้าที่ |
|----------------------|---------|
| `app.py`             | แอปหลัก Flask, จัดการ route และกล้อง RTSP |
| `camera.py`          | จัดการกล้อง, จับภาพ, ตรวจจับด้วย YOLOv8 |
| `db.py`              | เชื่อมต่อและจัดการฐานข้อมูล (MySQL/MariaDB) |
| `utils.py`           | ฟังก์ชันเสริม เช่น ส่ง Telegram, ล้างข้อมูลเก่า |
| `static/`, `templates/` | HTML, CSS, JavaScript สำหรับแดชบอร์ด |
| `detection_data/`    | เก็บภาพที่ตรวจจับและ log ที่เกี่ยวข้อง |

---

## วิธีเริ่มต้นใช้งานของระบบ

1. **ติดตั้งไลบรารีที่จำเป็น**  
pip install -r requirements.txt

2. **ดาวน์โหลดโมเดล YOLOv8**

wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

3. **ตั้งค่า Telegram Bot**

- สร้างบอทผ่าน BotFather
- ตั้งค่า TELEGRAM_BOT_TOKEN และ TELEGRAM_CHAT_ID ที่ utils.py หรือ app.py

4. **เริ่มระบบ Flask**
python app.py

---

```markdown
## วิธีเพิ่มกล้อง RTSP
**เพิ่มชื่อกล้องและลิงก์ใน 3 จุดหลัก**

1. `app.py`

rtsp_cameras = {
    "Front Gate": "rtsp://user:pass@ip:port/stream1",
    "Lobby": "rtsp://user:pass@ip:port/stream2",
    "ชื่อกล้องใหม่": "rtsp://..."
}

2. `main.js → ภายใน NTVisionDashboard constructor`

this.cameras = {
    "Front Gate": "Front Gate",
    "Lobby": "Lobby",
    "ชื่อกล้องใหม่": "ชื่อกล้องใหม่"
};

3. `main.js → ภายใน formatCameraName()`

"ชื่อกล้องใหม่": "ชื่อที่แสดงบนหน้าจอ"

--- 

## ฟีเจอร์แดชบอร์ด
- แสดงภาพสดจากกล้องทุกตัว
- ตารางประวัติการตรวจจับ (พร้อมดู/ดาวน์โหลดภาพ)
- กราฟสถิติรายวัน / รายสัปดาห์ / รายเดือน
- รายงานแยกตามกล้อง / เวลา / ความถี่

---