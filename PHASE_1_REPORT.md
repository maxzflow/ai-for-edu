# รายงานการวิเคราะห์และออกแบบระบบ (PHASE 1)
## โครงการ: TikTok Studio Scheduled Product Video Automation (Desktop App)

**วันที่จัดทำ:** 26 ตุลาคม 2026  
**สถานะ:** เสร็จสิ้น Phase 1 (รอคำสั่งเพื่อเริ่ม Phase 2)  
**ทีมงาน:** Senior Software Engineer & Browser Automation Specialist

---

## 1. สภาพแวดล้อมระบบที่พบ (Environment Audit)

### 1.1 ข้อมูลสภาพแวดล้อมการพัฒนา
* **ระบบปฏิบัติการ:** Windows 11 (x64)
* **Node.js:** `v22.15.0`
* **npm:** `10.9.2`
* **Git:** `2.51.0.windows.1`
* **Workspace Path:** `c:\Users\nutta\Desktop\Lab\ttpost`

### 1.2 การตรวจสอบไฟล์อ้างอิง (Reference Screenshots)
พบไฟล์ภาพหน้าจออ้างอิงจาก TikTok Studio ครบทั้ง 8 ภาพในโฟลเดอร์ `img/` โดยมีผลการวิเคราะห์ขั้นตอนและโครงสร้างเชิงลึกดังนี้:

| ไฟล์ | หน้าจออ้างอิง | การวิเคราะห์ขั้นตอนและโครงสร้างจากภาพ |
| :--- | :--- | :--- |
| **`001.jpg`** | รายการเนื้อหา (Content Dashboard) | หน้าแรกหลังเข้าสู่ระบบ (`/tiktokstudio/content`) แสดงรายการคลิปที่โพสต์ไปแล้ว แท็บแบบร่าง (`แบบร่าง 0`) ตัวชี้วัดยอดวิว ยอดไลก์ และปุ่มเมนูจัดการโพสต์เดิม |
| **`002.jpg`** | หน้าอัปโหลดวิดีโอ (Upload Landing) | แสดงพื้นที่ Drag & Drop และปุ่ม `"เลือกวิดีโอ"` (มี `<input type="file">` ซ่อนอยู่ภายใน) ระบุเงื่อนไขรองรับไฟล์ `.mp4` ขนาดไม่เกิน 30 GB |
| **`003.jpg`** | ฟอร์มรายละเอียดโพสต์ (Post Form) | แสดงแถบสถานะการอัปโหลด (`อัปโหลดแล้ว 3.66MB`), กล่องข้อความ `"คำอธิบาย"` (รองรับพิมพ์แฮชแท็กและ Mention), ปุ่ม `"+ เพิ่ม"` ในหัวข้อ `"เพิ่มลิงก์"`, ตัวเลือกเวลาโพสต์ (`ตอนนี้` vs `ตั้งเวลา`) และระบบสแกนลิขสิทธิ์เพลง |
| **`004.jpg`** | ป๊อปอัปเลือกประเภทลิงก์ (Add Link Modal) | แสดง Modal `"เพิ่มลิงก์"` มีดรอปดาวน์เลือก `"ประเภทของลิงก์"` ระบุค่าเป็น `"สินค้า"` (ไอคอนตะกร้าส้ม) พร้อมปุ่ม `"ถัดไป"` |
| **`005.jpg`** | หน้าต่างเลือกแหล่งสินค้า (Product Tabs) | มี 2 แท็บ: `"ร้านของฉัน"` (TikTok Shop ของเจ้าของช่อง) และ `"นำเสนอสินค้า"` (Showcase / ครีเอเตอร์ปักตะกร้าพันธมิตร) |
| **`006.jpg`** | ตารางค้นหาและเลือกสินค้า (Product Table) | แท็บ `"นำเสนอสินค้า"` มีช่อง `"ค้นหาสินค้า"`, ตารางสินค้าพร้อมคอลัมน์สำคัญ: **Radio เลือกสินค้า**, **ชื่อสินค้า**, **ID สินค้า (19 หลัก)**, **ราคา**, **สต็อก**, **สถานะ**, และแถบเลขหน้า Pagination |
| **`007.jpg`** | หน้ากดยืนยันชื่อแสดงผลสินค้า (Confirm Name) | ป๊อปอัปให้ตรวจสอบและแก้ไขชื่อสินค้าที่จะปรากฏบนคลิป (จำกัดความยาวสูงสุดไม่เกิน 30 ตัวอักษร) พร้อมปุ่มยืนยัน `"+ เพิ่ม"` |
| **`008.jpg`** | การกำหนดวัน-เวลาเผยแพร่ (Schedule & Confirmation) | เมื่อเลือก Radio `"ตั้งเวลา"` จะมี Date Picker (ปฏิทินเดือน/ปี ค.ศ.) และ Time Picker (เวลา 24 ชม.), ในพรีวิวคลิปฝั่งขวาจะปรากฏแถบปักตะกร้าสินค้าสีส้ม, และปุ่มหลักด้านล่างจะเปลี่ยนข้อความจาก `"โพสต์"` เป็น `"ตั้งเวลา"` |

---

## 2. โครงสร้างโปรเจกต์ที่เสนอ (Proposed Architecture)

ออกแบบระบบตามหลักการ **Separation of Concerns (SoC)** เพื่อแยกการทำงานของ UI, ฐานข้อมูล, คิวงาน และ Browser Automation ให้เป็นอิสระต่อกัน:

```text
ttpost/
├── img/                               # ภาพหน้าจออ้างอิงจาก TikTok Studio (001.jpg - 008.jpg)
├── src/
│   ├── main/                          # Electron Main Process
│   │   ├── index.ts                   # วงจรชีวิตแอปพลิเคชันและการเปิดหน้าต่าง
│   │   ├── ipc/                       # Type-safe IPC Handlers เชื่อมต่อกับ Renderer
│   │   └── preload.ts                 # Secure ContextBridge API (ไม่เปิด nodeIntegration ตรงๆ)
│   │
│   ├── renderer/                      # React Frontend UI (Vite + TypeScript + Tailwind CSS)
│   │   ├── src/
│   │   │   ├── components/            # Reusable UI Primitives (Button, Modal, Table, Badge, Card)
│   │   │   ├── views/
│   │   │   │   ├── VideoLibrary/      # เลือกโฟลเดอร์/ไฟล์, Thumbnail, แคปชันรายคลิป
│   │   │   │   ├── ProductLibrary/    # แคตตาล็อกสินค้า, Product ID, ค้นหา/จับคู่
│   │   │   │   ├── ScheduleQueue/     # รายการคิว, เวลา Asia/Bangkok, สถานะ, ปุ่มควบคุม
│   │   │   │   └── Settings/          # ที่อยู่ Browser Profile, กำหนดเวลาหน่วง, ปรับแต่งทั่วไป
│   │   │   └── store/                 # Global State Management
│   │
│   ├── database/                      # SQLite Persistence Layer
│   │   ├── index.ts                   # SQLite Connection & Migration Runner
│   │   ├── schema.sql                 # โครงสร้างตารางฐานข้อมูล
│   │   └── repositories/              # VideoRepo, ProductRepo, JobRepo, SettingsRepo
│   │
│   ├── queue/                         # Job Queue State Machine
│   │   ├── job-queue.ts               # คิวประมวลผลวิดีโอแบบทีละรายการ (Start, Pause, Resume, Stop)
│   │   └── job-states.ts              # จัดการ State: Draft -> Ready -> Processing -> Product Selected
│   │                                  #        -> Scheduling -> Scheduled (หรือ Failed / Requires Manual Action)
│   │
│   └── automation/                    # Playwright Browser Automation Engine
│       ├── browser-manager.ts         # ควบคุม User Data Directory (จำ Session ล็อกอิน ไม่เก็บรหัสผ่าน)
│       ├── session-checker.ts         # ตรวจสอบสถานะการล็อกอินและแจ้งเตือนเมื่อ Session หมดอายุ
│       ├── studio-workflow.ts         # ลำดับการทำงานตั้งแต่ Step 1 ถึง Step 9
│       ├── locators/                  # คลัง Selector ที่ผ่านการตรวจสอบจาก DOM จริง
│       └── guards/                    # ระบบตรวจจับ CAPTCHA, MFA, Pop-up แทรกซ้อนเพื่อหยุดรอผู้ใช้
│
├── tests/
│   ├── mocks/                         # Mock TikTok Studio HTML Pages (จำลอง 8 หน้าจอเพื่อทดสอบแบบ Offline)
│   ├── unit/                          # Unit tests (Database, Timezone Asia/Bangkok, Queue logic)
│   └── automation-mock/               # Playwright tests สำหรับรันกับ Mock Pages เพื่อการันตี Workflow
│
├── PHASE_1_REPORT.md                  # เอกสารสรุปผล Phase 1 ฉบับนี้
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

### โครงสร้างฐานข้อมูล SQLite
1. **`videos`**:
   * `id`: รหัสคลิป (UUID/Auto-increment)
   * `file_path`: ตำแหน่งไฟล์ในเครื่อง (ตรวจสอบการมีอยู่ของไฟล์เสมอ)
   * `file_name`: ชื่อไฟล์
   * `file_size`: ขนาดไฟล์
   * `duration`: ความยาวคลิป
   * `thumbnail_path`: พาธรูปปก Thumbnail
   * `caption`: แคปชันเริ่มต้นของวิดีโอ
   * `created_at`, `updated_at`: วันเวลาสร้างและแก้ไข
2. **`products`**:
   * `id`: รหัสสินค้าในระบบ
   * `product_id_tiktok`: ID สินค้า 19 หลักจาก TikTok Studio (หัวใจสำคัญในการจับคู่สินค้าไม่ให้ผิดตัว)
   * `title`: ชื่อเต็มของสินค้า
   * `display_title`: ชื่อย่อที่ต้องการให้โชว์ในคลิป (ความยาวสูงสุด 30 ตัวอักษร)
   * `price`: ราคา
   * `stock`: จำนวนสต็อก
   * `notes`: หมายเหตุเพิ่มเติม
   * `verified`: สถานะยืนยันความถูกต้องของสินค้า
3. **`publishing_jobs`**:
   * `id`: รหัสงานโพสต์
   * `video_id`: อ้างอิงวิดีโอ
   * `product_id`: อ้างอิงสินค้าที่ต้องการปักตะกร้า
   * `caption_override`: แคปชันเฉพาะสำหรับคิวนี้
   * `scheduled_time`: วันเวลาที่ต้องการเผยแพร่ (Timezone `Asia/Bangkok` ISO-8601)
   * `status`: สถานะงาน (`Draft`, `Ready`, `Processing`, `Product Selected`, `Scheduling`, `Scheduled`, `Failed`, `Requires Manual Action`, `Cancelled`)
   * `error_message`: รายละเอียดข้อผิดพลาดเมื่อเกิดปัญหา
   * `evidence_screenshot`: พาธภาพหน้าจอหลักฐานที่ระบบ TikTok Studio รับการตั้งเวลาแล้ว
   * `created_at`, `updated_at`
4. **`job_events`**:
   * บันทึก Log ของแต่ละงานในแต่ละ Step (Audit Trail)
5. **`settings`**:
   * ค่ากำหนดต่างๆ เช่น Chrome Profile Path, Delay Intervals, Default Timezone

---

## 3. สิ่งที่สามารถพัฒนาได้ทันที (Immediate Implementations)

ไม่ต้องรอเชื่อมต่อกับ TikTok จริง สามารถสร้างส่วนประกอบเหล่านี้ให้พร้อมใช้งานได้ทันที:

1. **Project Scaffolding:** ตั้งค่า Electron + Vite + React + TypeScript + Tailwind CSS พร้อมระบบ IPC ที่ปลอดภัย
2. **Database Layer (SQLite):** สร้าง Schema ตารางทั้ง 5 ตาราง พร้อม Repository Pattern รองรับการเปิดแอปใหม่แล้วกู้คืนคิวงานที่ยังค้างอยู่
3. **Video Library Module:** พัฒนาระบบเลือกไฟล์/โฟลเดอร์ ตรวจสอบว่าไฟล์ยังอยู่ในตำแหน่งเดิม ดึงขนาด และสร้าง Thumbnail
4. **Product Library Module:** หน้าจัดการแคตตาล็อกสินค้า จัดเก็บ Product ID (19 หลัก) และชื่อสั้นแสดงผล พร้อมระบบค้นหา/กรอง
5. **Scheduling Queue Management UI:** หน้าจอจัดคิวงาน จัดเรียงตามวัน-เวลาในเขตเวลา `Asia/Bangkok`, การเปลี่ยนสถานะงาน, ปุ่ม Start, Pause, Stop, Retry, Cancel
6. **Playwright Browser Manager (Local User Data Dir):** ระบบเปิดเบราว์เซอร์ Chromium พร้อมบันทึก User Data Directory ในเครื่อง เพื่อให้ผู้ใช้เข้าสู่ระบบด้วยตนเอง 1 ครั้ง โดยไม่ต้องเก็บรหัสผ่านในฐานข้อมูล
7. **Mock TikTok Studio Server & Test Harness:** สร้าง Local Web Server ที่จำลองหน้าตาและพฤติกรรม DOM ของหน้า 001–008 สำหรับทดสอบ Script Automation ในระดับทดสอบ

---

## 4. สิ่งที่ต้องตรวจสอบบน TikTok Studio จริง (Live Verification Checklist)

ต้องตรวจสอบกับหน้าเว็บ TikTok Studio จริงก่อนสรุป Selector เพื่อความแม่นยำ 100%:

1. **โครงสร้าง DOM และ Selector ของฟอร์มอัปโหลด:**
   * ตรวจสอบว่าปุ่ม `"เลือกวิดีโอ"` มี `<input type="file">` ที่สามารถใช้ `setInputFiles()` ได้โดยตรงหรือไม่
   * ตรวจสอบว่ากล่อง `"คำอธิบาย"` เป็น `<textarea>`, `contenteditable` หรือ Rich-text Framework เพื่อให้การป้อนข้อมูลจำลอง Event แฮชแท็กได้สมบูรณ์
2. **การทำงานของตารางค้นหาสินค้า (006.jpg):**
   * ตรวจสอบว่าการพิมพ์ค้นหาด้วย Product ID 19 หลัก สามารถค้นหาเจอได้ตรงตัวทันทีหรือไม่
   * ตรวจสอบการโหลดข้อมูลในตารางว่าเป็นแบบ Debounce Search หรือ Infinite Scroll / Pagination
3. **ข้อจำกัดการตั้งเวลา (Scheduling Constraints):**
   * ตรวจสอบระยะเวลาล่วงหน้าขั้นต่ำและสูงสุดที่ระบบ TikTok Studio ยอมรับ (เช่น ล่วงหน้าขั้นต่ำ 15 นาที หรือสูงสุดไม่เกิน 10 วัน)
   * ตรวจสอบการแสดงผลปีใน Date Picker (ปี ค.ศ. หรือ พ.ศ. เมื่อระบบปฏิบัติการหรือเบราว์เซอร์ใช้ภาษาไทย)
4. **การตรวจสอบผลลัพธ์เพื่อยืนยันสถานะ `Scheduled`:**
   * สัญญาณยืนยันความสำเร็จ: ข้อความแจ้งเตือน (Toast), การเปลี่ยนหน้า URL หรือการมีรายการปรากฏในแท็บ "โพสต์ที่ตั้งเวลาไว้"
   * ต้องมีกลไกตรวจสอบหลักฐานนี้ก่อนอัปเดตสถานะเป็น `Scheduled` เสมอ หากไม่พบหลักฐานจะปรับเป็น `Requires Manual Action`
5. **การรับมือ Security Checkpoints:**
   * ตรวจจับการปรากฏของ CAPTCHA Slider หรือ SMS Verification เพื่อสั่งหยุด Automation ทันที และส่งสัญญาณแจ้งเตือนผู้ใช้ในแอป Desktop

---

## 5. แผนการทดสอบ (Testing Strategy)

* **ระดับที่ 1: Unit & Integration Testing (Offline)**
  * ทดสอบ CRUD และ State Transitions ใน SQLite
  * ทดสอบตรรกะการแปลงเวลาและการจัดเรียงคิว (Timezone Asia/Bangkok)
  * ทดสอบการกู้คืนคิวงานค้างหลังแอปปิดกะทันหัน
* **ระดับที่ 2: Mock DOM Automation Testing (Playwright vs Mock Pages)**
  * ทดสอบ Playwright กับ Mock Server ที่จำลองขั้นตอน 001–008
  * ทดสอบกรณี Error: สินค้าค้นหาไม่พบ, สินค้าชื่อซ้ำแต่คนละ ID, วิดีโอไฟล์หาย, เวลาที่ตั้งไม่อยู่ในช่วงที่อนุญาต
* **ระดับที่ 3: Live Verification (Human-in-the-Loop)**
  * เริ่มต้นด้วยโหมด Headful Browser ให้ผู้ใช้ล็อกอิน
  * ทดสอบ Dry-run ตรวจสอบ Selector บนหน้าเว็บจริง
  * ทดสอบสร้าง 1 รายการเพื่อตรวจสอบความถูกต้องของการปักตะกร้าและการตั้งเวลา ก่อนเปิดใช้งานระบบประมวลผลเป็นชุด (Batch)

---

## 6. ข้อตกลงความปลอดภัยและการปฏิบัติตามมาตรฐาน (Security & Reliability Principles)

1. **ไม่เก็บรหัสผ่าน:** ใช้ Persistent Browser Context ของ Playwright จัดเก็บ Cookie และ Local Storage เท่านั้น ผู้ใช้เป็นผู้ล็อกอินเอง
2. **ไม่ใช้พิกัดตายตัว (No Fixed Coordinates):** ทุกการคลิกหรือพิมพ์ต้องผ่าน Semantic Locator เช่น `getByRole`, `getByLabel`, `getByPlaceholder`, `getByText`
3. **ตรวจสอบหลักฐานก่อนบันทึกสถานะ:** ห้ามถือว่างานสำเร็จเพียงเพราะคลิกปุ่ม "ตั้งเวลา" แล้ว ต้องตรวจจับผลตอบรับจริงจากระบบ TikTok เสมอ
4. **Human-in-the-loop เมื่อไม่แน่นอน:** กรณีสินค้ามีชื่อคล้ายกันหรือค้นหาไม่พบ ระบบจะเปลี่ยนสถานะเป็น `Requires Manual Action` เพื่อความปลอดภัยสูงสุด

---
*เอกสารนี้ถูกบันทึกไว้ใน Workspace เรียบร้อยแล้ว พร้อมสำหรับการดำเนินงานใน Phase ต่อไป*
