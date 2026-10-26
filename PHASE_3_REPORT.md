# รายงานผลการดำเนินงาน (PHASE 3)
## โครงการ: TikTok Studio Scheduled Product Video Automation (Desktop App)
### หัวข้อ: VIDEO, PRODUCT & QUEUE ENGINE

**วันที่จัดทำ:** 26 ตุลาคม 2026  
**สถานะ:** เสร็จสิ้น Phase 3 สมบูรณ์ 100% (ผ่านการทดสอบทุกฟังก์ชัน พร้อมเริ่ม Phase 4)  
**ทีมงาน:** Senior Software Engineer & Browser Automation Specialist

---

## 1. สรุปภาพรวมความสำเร็จ (Executive Summary)

ใน **PHASE 3** ทีมวิศวกรได้พัฒนาความสามารถระดับ Core Engine ทั้ง 3 ด้านหลักของแอปพลิเคชัน Desktop สำเร็จเรียบร้อย:

1. **Video Engine & Media Extraction:** เชื่อมต่อระบบกับ `ffprobe` และ `ffmpeg` บนระบบปฏิบัติการ Windows สำหรับการสกัดข้อมูล Metadata แท้จริงจากไฟล์วิดีโอ (ความละเอียด, สัดส่วน 9:16/16:9, FPS, ความยาวคลิป, Codec) สร้างภาพตัวอย่าง (Thumbnail) จากเฟรมจริงที่ 1.0 วินาทีลงในโฟลเดอร์ `data/thumbnails/` ป้องกันการสร้างภาพซ้ำซ้อน และมีระบบตรวจสอบการมีอยู่จริงของไฟล์บนฮาร์ดดิสก์แบบ Real-time พร้อมฟังก์ชันแยกการลบข้อมูลในระบบออกจากการลบไฟล์ต้นฉบับบนดิสก์
2. **Product Library & Transfer Engine:** รองรับการนำเข้า (Import) และส่งออก (Export) แคตตาล็อกสินค้าทั้งรูปแบบ **CSV** และ **JSON** โดยมีกลไกป้องกันการสูญเสียความแม่นยำของ **TikTok Product ID 19 หลัก** (เก็บเป็น `string` 100% ป้องกันเลขอันตรายจากการถูกแปลงเป็น Floating-point Number ใน JavaScript), รองรับภาษาไทยสมบูรณ์ด้วยการฝัง **UTF-8 BOM (`\uFEFF`)** สำหรับเปิดบน Microsoft Excel, ระบบ Pre-import Validation ตรวจจับข้อมูลซ้ำ ข้อความชื่อในคลิปยาวเกิน 30 ตัวอักษร และแยกแท็บชัดเจนระหว่าง `"นำเสนอสินค้า"` (Showcase) และ `"ร้านของฉัน"` (My Shop)
3. **Queue State Engine & Readiness Validator:** พัฒนาระบบตรวจสอบความพร้อมของคิวงานก่อนอนุญาตให้เข้าสถานะ `Ready` อย่างเคร่งครัด โดยตรวจสอบไฟล์วิดีโอ, ความสมบูรณ์ของรหัสสินค้า 19 หลัก, แคปชัน, และวันเวลาในอนาคตตามเขตเวลา **Asia/Bangkok (UTC+7)** พร้อมแสดงรายการข้อผิดพลาดละเอียดครบทุกข้อ, ระบบควบคุมสถานะงาน (State Machine) 9 สถานะ, การบันทึก Audit Log ลงในตาราง `job_events`, และระบบกู้คืนสถานะงานค้างอัตโนมัติ (Crash Recovery) เพื่อป้องกันการโพสต์ซ้ำ

---

## 2. ไฟล์ที่สร้างและแก้ไขในระบบ (Files Created & Modified)

### 2.1 ไฟล์ที่สร้างใหม่:
* **`src/main/services/media.service.ts`**: บริการจัดการสื่อวิดีโอ ค้นหาไบนารี `ffprobe`/`ffmpeg`, ตรวจสอบสุขภาพไฟล์ดิสก์, สกัด Metadata (ความกว้าง, ความสูง, FPS, Duration, Codec) และสร้าง Thumbnail บันทึกเป็น JPEG
* **`src/main/services/product-transfer.service.ts`**: บริการนำเข้าและส่งออกสินค้า CSV/JSON, ตรวจสอบโครงสร้าง, รักษาเลข 19 หลัก, ป้องกันข้อมูลซ้ำ, และส่งออกไฟล์ CSV พร้อม UTF-8 BOM
* **`src/queue/queue-engine.ts`**: เครื่องยนต์คิวงาน ตรวจสอบเงื่อนไขความพร้อม (Readiness Check), ควบคุม State Machine ป้องกันการเปลี่ยนสถานะผิดลำดับ, ตรวจสอบเวลา Asia/Bangkok และบันทึก Audit Log
* **`tests/unit/media.test.ts`**: ชุดทดสอบ Unit Test สำหรับ Metadata และ Thumbnail จากไฟล์จริง
* **`tests/unit/product-transfer.test.ts`**: ชุดทดสอบ Unit Test สำหรับการนำเข้า/ส่งออก และรักษาเลข 19 หลัก
* **`tests/unit/queue-engine.test.ts`**: ชุดทดสอบ Unit Test สำหรับ Readiness Validator, State Machine และเขตเวลา Asia/Bangkok
* **`tests/integration/crash-recovery.test.ts`**: ชุดทดสอบ Integration Test สำหรับ Crash Auto-recovery และการคงอยู่ของข้อมูลเมื่อเปิดแอปใหม่

### 2.2 ไฟล์ที่ได้รับการปรับปรุง:
* **`src/database/schema.sql`**: เพิ่มเอกสาร DDL สำหรับ Migration Version 2
* **`src/database/index.ts`**: เพิ่มโค้ด **Migration Version 2** ปรับปรุงโครงสร้างตาราง `videos`, `products` และ `publishing_jobs` โดยไม่กระทบข้อมูลเดิม
* **`src/database/repositories/video.repository.ts`**: เพิ่มฟิลด์ Metadata (`width`, `height`, `resolution`, `fps`, `format_name`, `codec_name`, `file_status`) และฟังก์ชันค้นหา/เรียงลำดับ (`search`, `getByFilePath`)
* **`src/database/repositories/product.repository.ts`**: เพิ่มฟิลด์ `source_type` ('showcase' vs 'my_shop') และฟังก์ชันค้นหาแยกตามแท็บ
* **`src/database/repositories/job.repository.ts`**: เพิ่มการจัดเก็บ `validation_errors` (JSON array) และฟังก์ชัน `recoverInterruptedJobs()` บันทึก Audit Log อัตโนมัติ
* **`src/shared/types.ts`**: เพิ่ม Type Definition ครอบคลุม VideoMetadata, ProductSourceType, ProductImportPreview, ProductImportRow และ ElectronAPI
* **`src/main/ipc/index.ts`**: ลงทะเบียน IPC Handlers ใหม่ครบทุกฟังก์ชัน (นำเข้าวิดีโอพร้อมสกัด Metadata/ปก, สแกนไฟล์บนดิสก์, นำเข้า/ส่งออกสินค้า, ตรวจความพร้อมคิว และกู้คืนงานค้าง)
* **`src/preload/index.ts`**: เชื่อมโยง Method ผ่าน ContextBridge ให้ Renderer ใช้งานอย่างปลอดภัย
* **`src/renderer/src/views/VideoLibrary/index.tsx`**: ปรับหน้าตา แสดงภาพ Thumbnail จริง, แถบสถานะไฟล์ดิสก์, ข้อมูลเทคนิคของคลิป, ช่องค้นหาและตัวเรียงลำดับ, หน้าต่างยืนยันการลบที่แยกการลบในระบบออกจากการลบไฟล์จริง
* **`src/renderer/src/views/ProductLibrary/index.tsx`**: เพิ่มแท็บเลือกแหล่งสินค้า `"ทั้งหมด"`, `"นำเสนอสินค้า"`, `"ร้านของฉัน"`, หน้าต่างนำเข้าไฟล์ CSV/JSON พร้อมพรีวิวสรุปความถูกต้อง, ปุ่มส่งออกไฟล์ CSV (Excel Thai)/JSON, และการตรวจ Product ID 19 หลักแบบ Real-time
* **`src/renderer/src/views/ScheduleQueue/index.tsx`**: แสดงวันเวลาเผยแพร่ในเขตเวลาไทย Asia/Bangkok, กล่องแสดงรายละเอียดข้อผิดพลาดที่ต้องแก้ไขก่อนเข้าสถานะ Ready, ปุ่มเปลี่ยนสถานะตาม State Machine, ปุ่มดูประวัติ Audit Log, และปุ่มกู้คืนงานค้าง

---

## 3. รายละเอียดการทำงานของแต่ละฟังก์ชัน (Core Capabilities)

### 3.1 การจัดการวิดีโอ (Video Engine)
* **การนำเข้าไฟล์:** รองรับนามสกุล `.mp4`, `.mov`, `.webm` ผ่าน Native Dialog ของ Windows
* **การตรวจสอบสุขภาพไฟล์ (File Health Check):** ตรวจสอบว่าไฟล์มีอยู่จริงบนดิสก์และสามารถอ่านได้ (`fs.constants.R_OK`) หากไฟล์ถูกย้ายหรือลบในภายหลัง ระบบจะมีปุ่ม **"ตรวจเช็คไฟล์บนดิสก์" (Rescan)** และแสดงป้ายเตือนสีแดง `"ไม่พบไฟล์บนดิสก์"` ทันที
* **การป้องกันไฟล์ซ้ำ:** คำนวณ Canonical Absolute Path (`path.resolve`) และตรวจสอบกับฐานข้อมูล หากพบว่าไฟล์เดิมถูกนำเข้าแล้ว จะปฏิเสธพร้อมแจ้งเตือนผู้ใช้
* **การอ่าน Metadata จริง:** ใช้ `ffprobe -show_entries ... -of json` ดึงความกว้าง/ความสูง คำนวณความละเอียด (`1080x1920 (9:16)`, `1080p`, `720p`), คำนวณ Frame rate (FPS) จากอัตราส่วน `r_frame_rate` (เช่น 30 fps), ความยาววิดีโอ และ Codec วิดีโอ (`h264`, `hevc` ฯลฯ)
* **การสร้าง Thumbnail จริง:** ใช้ `ffmpeg -ss 1.00 -i ... -vframes 1 -q:v 2` จับภาพตัวอย่างแท้จริงจากเฟรมของวิดีโอ บันทึกลงใน `data/thumbnails/${videoId}.jpg` โดยระบบจะตรวจสอบก่อนว่ามีไฟล์ภาพอยู่แล้วหรือไม่ หากมีอยู่แล้วจะไม่ประมวลผลซ้ำเพื่อประหยัดทรัพยากร CPU
* **การลบวิดีโออย่างปลอดภัย:** มีตัวเลือกระหว่าง "ลบเฉพาะในระบบ (เก็บไฟล์วิดีโอบนเครื่องไว้)" กับ "ลบไฟล์ต้นฉบับบนดิสก์ด้วย" พร้อมข้อความเตือนความปลอดภัย

### 3.2 การจัดการสินค้า (Product Library & Transfer Engine)
* **การรักษาความถูกต้องของ Product ID 19 หลัก:**
  * ปัญหาสำคัญของ JavaScript คือเลขจำนวนเต็มที่มีขนาดเกิน 16 หลัก (`Number.MAX_SAFE_INTEGER = 9007199254740991`) จะถูกปัดเศษ ทำให้เลขหลักท้ายๆ เพี้ยน (เช่น `1730707644017641525` กลายเป็น `...500`)
  * ระบบจึงประมวลผล Product ID เป็น `string` เสมอ ทั้งใน Parser, ตัวแปลง JSON (ใช้ Regex คลุมตัวเลขยาวเกิน 15 หลักก่อน Parse), และการบันทึกลง SQLite
* **การนำเข้าสินค้า (CSV & JSON):**
  * มีระบบ Pre-import Validator สรุปจำนวนรายการทั้งหมด, รายการที่ถูกต้อง, รายการที่ไม่ผ่าน, และรายการที่ซ้ำ
  * ตรวจสอบว่าชื่อสินค้า (title) ต้องไม่ว่างเปล่า
  * ตรวจสอบ Product ID ต้องเป็นตัวเลข 19 หลักพอดี
  * ตรวจสอบชื่อที่จะปรากฏในคลิป (displayTitle) ต้องยาวไม่เกิน 30 ตัวอักษร
  * ให้ผู้ใช้เลือกนโยบายกรณีพบข้อมูลซ้ำ: "ข้ามรายการซ้ำ (Skip)" หรือ "เขียนทับข้อมูลเดิม (Overwrite)"
* **การส่งออกสินค้า (CSV & JSON):**
  * ส่งออกเป็น CSV พร้อม **UTF-8 BOM (`\uFEFF`)** ทำให้เปิดบนโปรแกรม Microsoft Excel บน Windows ได้โดยตัวหนังสือภาษาไทยไม่เป็นภาษาต่างดาว (Mojibake)
  * ส่งออกเป็น JSON จัดรูปแบบสวยงามและคง Product ID เป็นสตริง
  * เลือกว่าจะส่งออกทั้งหมด หรือส่งออกเฉพาะแท็บ `"นำเสนอสินค้า"` หรือ `"ร้านของฉัน"`
* **การแยกสถานะข้อมูล:**
  * มีการระบุชัดเจนระหว่างสินค้าที่ผู้ใช้กรอกเอง (ป้ายสีส้ม: "บันทึกโดยผู้ใช้ (รอตรวจ)") กับสินค้าที่ผ่านการตรวจยืนยันจาก TikTok จริง (ป้ายสีเขียว: "ยืนยันบน TikTok แล้ว")

### 3.3 เครื่องยนต์คิวงาน (Queue State Engine)
* **การตรวจสอบความพร้อมก่อนเข้าสถานะ Ready (Pre-Ready Validator):**
  ระบบจะไม่อนุญาตให้เปลี่ยนสถานะเป็น `Ready` จนกว่าจะผ่านเงื่อนไขต่อไปนี้ทั้งหมด:
  1. มีการเลือกวิดีโอสำหรับงานนั้น
  2. ไฟล์วิดีโอยังคงมีอยู่จริงบนดิสก์และอ่านได้ (ขนาดไฟล์มากกว่า 0 ไบต์)
  3. ไฟล์วิดีโอผ่านการตรวจสอบความสมบูรณ์และมีความยาวมากกว่า 0 วินาที
  4. หากมีการระบุสินค้า ต้องมี TikTok Product ID ที่ถูกต้อง 19 หลัก และ Display Title ยาวไม่เกิน 30 ตัวอักษร
  5. มีแคปชันวิดีโอ (จากงานหรือดึงจากแคปชันเริ่มต้นของวิดีโอ)
  6. วันและเวลาเผยแพร่ต้องเป็นเวลาในอนาคต
  7. เวลาที่ตั้งไว้ต้องล่วงหน้าอย่างน้อยตามเกณฑ์ที่กำหนด (ดึงจากตั้งค่า `min_schedule_lead_minutes` เช่น 15 นาที)
  * หากไม่ผ่าน ระบบจะแสดงรายการข้อผิดพลาดทั้งหมดในตารางคิวงานแบบละเอียด ไม่ใช่เพียงแค่บอกว่าไม่พร้อม
* **State Machine & กฎการเปลี่ยนสถานะ:**
  ควบคุมลำดับขั้นตอนที่อนุญาตอย่างเข้มงวด:
  * `Draft` $\rightarrow$ `Ready`, `Cancelled`
  * `Ready` $\rightarrow$ `Draft`, `Processing`, `Cancelled`
  * `Processing` $\rightarrow$ `Product Selected`, `Failed`, `Requires Manual Action`
  * `Product Selected` $\rightarrow$ `Scheduling`, `Failed`, `Requires Manual Action`
  * `Scheduling` $\rightarrow$ `Scheduled`, `Failed`, `Requires Manual Action`
  * `Scheduled` $\rightarrow$ `Draft`, `Cancelled`
  * `Failed` $\rightarrow$ `Ready`, `Draft`, `Cancelled`
  * `Requires Manual Action` $\rightarrow$ `Ready`, `Draft`, `Cancelled`
  * `Cancelled` $\rightarrow$ `Draft`
  * การพยายามข้ามสถานะที่ไม่ได้รับอนุญาต (เช่น จาก `Draft` ข้ามไป `Scheduled` โดยตรง) จะถูกปฏิเสธทันที และบันทึกข้อผิดพลาดลง Audit Log
* **การจัดการเวลา Asia/Bangkok (UTC+7):**
  * จัดเก็บเป็นมาตรฐาน ISO 8601 string ที่มี Timezone Offset (`+07:00`) อย่างสม่ำเสมอ
  * แสดงผลใน UI ด้วยภาษาไทยและเวลาประเทศไทย (Asia/Bangkok)
  * เมื่อปิดและเปิดแอปพลิเคชันใหม่ เวลาจะไม่คลาดเคลื่อนหรือเลื่อนข้ามวัน
* **Audit Logging:**
  * ทุกการกระทำสำคัญ (`JobCreated`, `READINESS_CHECK`, `STATUS_CHANGE`, `INVALID_TRANSITION`, `CRASH_RECOVERY`) จะถูกบันทึกลงในตาราง `job_events`
  * มีหน้าต่าง Audit Log Viewer ใน UI ให้กดดูประวัติย้อนหลังของแต่ละคิวงานได้
* **การกู้คืนงานค้างเมื่อแอปปิดกะทันหัน (Crash Auto-Recovery):**
  * เมื่อเปิดแอปพลิเคชันขึ้นมา ระบบจะค้นหางานที่ค้างอยู่ในสถานะระหว่างทำงาน (`Processing`, `Product Selected`, `Scheduling`) และเปลี่ยนสถานะเป็น `Requires Manual Action` ทันที พร้อมบันทึกเหตุการณ์ลง Audit Log ป้องกันความเสี่ยงในการส่งงานซ้ำซ้อน

---

## 4. โครงสร้างฐานข้อมูลและการอัปเกรด (Database Migration 2)

ระบบฐานข้อมูล SQLite ได้รับการรัน Migration Version 2 เรียบร้อย โดยตรวจสอบโครงสร้างก่อนเพิ่มคอลัมน์ ทำให้ข้อมูลเดิมยังคงอยู่ครบถ้วน 100%:

```sql
-- Migration 2: Video Metadata, Product Source, Queue Validation Errors
ALTER TABLE videos ADD COLUMN width INTEGER;
ALTER TABLE videos ADD COLUMN height INTEGER;
ALTER TABLE videos ADD COLUMN resolution TEXT;
ALTER TABLE videos ADD COLUMN fps REAL;
ALTER TABLE videos ADD COLUMN format_name TEXT;
ALTER TABLE videos ADD COLUMN codec_name TEXT;
ALTER TABLE videos ADD COLUMN file_status TEXT DEFAULT 'Ready';

ALTER TABLE products ADD COLUMN source_type TEXT DEFAULT 'showcase';

ALTER TABLE publishing_jobs ADD COLUMN validation_errors TEXT;

CREATE INDEX IF NOT EXISTS idx_products_source_type ON products(source_type);
INSERT INTO schema_migrations (version, applied_at) VALUES (2, datetime('now'));
```

---

## 5. ผลการทดสอบระบบจริง (Automated Test Verification)

การทดสอบใน Phase 3 ได้แบ่งการทดสอบออกเป็น Unit Test และ Integration Test ชัดเจน โดยครอบคลุมทั้ง 12 สถานการณ์ที่กำหนด:

### ตารางสรุปผลการทดสอบ (Test Matrix)

| ข้อที่ | สถานการณ์การทดสอบ | ไฟล์ชุดทดสอบ | ผลการทดสอบจริง |
| :---: | :--- | :--- | :---: |
| 1 | การอ่าน Metadata จากไฟล์วิดีโอจริง via ffprobe | `tests/unit/media.test.ts` | **PASSED** (1280x720, 720p, 30fps, h264) |
| 2 | การสร้าง Thumbnail จากเฟรมจริง via ffmpeg | `tests/unit/media.test.ts` | **PASSED** (ไฟล์ขนาด 46 KB, ไม่สร้างซ้ำ) |
| 3 | การจัดการไฟล์ที่ไม่มีอยู่จริงหรือไฟล์เสีย | `tests/unit/media.test.ts` | **PASSED** (ดักจับ Error ถูกต้อง ไม่ทำให้แอปล่ม) |
| 4 | การนำเข้าสินค้าจาก CSV และ JSON | `tests/unit/product-transfer.test.ts` | **PASSED** (แยกแถวผ่าน/ไม่ผ่าน แสดงเหตุผลครบ) |
| 5 | การรักษา TikTok Product ID 19 หลักเป็น String | `tests/unit/product-transfer.test.ts` | **PASSED** (เลขท้าย `...525` ไม่ถูกปัดเป็น `...500`) |
| 6 | การนำเข้าและส่งออกภาษาไทย (Round-trip) | `tests/unit/product-transfer.test.ts` | **PASSED** (มี UTF-8 BOM ข้อความไทยสมบูรณ์) |
| 7 | การตรวจสอบความพร้อมของคิวงาน (Readiness) | `tests/unit/queue-engine.test.ts` | **PASSED** (สรุป Array ข้อผิดพลาดครบทุกเงื่อนไข) |
| 8 | การเปลี่ยนสถานะคิวงานและการปฏิเสธ Transition ผิด | `tests/unit/queue-engine.test.ts` | **PASSED** (ห้าม Draft -> Scheduled, บังคับผ่าน Ready) |
| 9 | การบันทึก Audit Log ลงตาราง `job_events` | `tests/unit/queue-engine.test.ts` | **PASSED** (บันทึก Timestamp, EventType, StepName ครบ) |
| 10 | การจัดการเขตเวลา Asia/Bangkok (UTC+7) | `tests/unit/queue-engine.test.ts` | **PASSED** (แปลงเวลาและเช็คระยะล่วงหน้า $\ge 15$ นาที) |
| 11 | การกู้คืนสถานะงานเมื่อแอปปิดกะทันหัน (Crash Recovery) | `tests/integration/crash-recovery.test.ts` | **PASSED** (ปรับเป็น 'Requires Manual Action' ทันที) |
| 12 | การบันทึกข้อมูลและเปิดแอปใหม่โดยข้อมูลยังอยู่ครบ | `tests/integration/crash-recovery.test.ts` | **PASSED** (ทดสอบเขียน ปิด เปิดใหม่ ข้อมูลคงเดิม 100%) |

### ผลลัพธ์จากการรันคำสั่งทดสอบจริง:

```text
> ttpost@1.0.0 test
> vitest run && node scripts/verify-full-persistence.js

 RUN  v5.0.5 C:/Users/nutta/Desktop/Lab/ttpost

 ✓ tests/unit/product-transfer.test.ts (3 tests) 63ms
 ✓ tests/unit/queue-engine.test.ts (4 tests) 122ms
 ✓ tests/unit/media.test.ts (3 tests) 192ms
 ✓ tests/database.test.ts (6 tests) 54ms
 ✓ tests/integration/crash-recovery.test.ts (2 tests) 78ms

 Test Files  5 passed (5)
      Tests  18 passed (18)
   Duration  389ms

[Persistence Test] Starting End-to-End SQLite persistence test across Electron sessions...
[Persistence Test] Inserting canary video record with ID: canary-1793031374779
[Persistence Test] Launching Electron app process...
[Electron stdout] [INFO] [Main] Electron app ready, initializing database...
[Electron stdout] [INFO] [Database] Running Migration 2: Video metadata and schema enhancements
[Electron stdout] [INFO] [Main] Database ready. Active jobs checked: 0
[Electron stdout] [INFO] [Main] Main window displayed
[Persistence Test] Closing Electron app process...
[Persistence Test] Verifying canary record after Electron app closed...
[Persistence Test] SUCCESS: Canary record successfully persisted across app lifecycle!
```

---

## 6. คำสั่งสำหรับเปิดใช้งานและทดสอบแอปพลิเคชัน

### 6.1 รันการทดสอบอัตโนมัติทั้งหมด (Unit & Integration Tests):
```bash
npm test
```

### 6.2 บิลด์ไฟล์ Production (Renderer + Main Process):
```bash
npm run build
```

### 6.3 เปิดแอปพลิเคชันในโหมดพัฒนา (Development Mode):
```bash
npm run dev
```

### 6.4 เปิดแอปพลิเคชันในโหมด Production จาก Bundle:
```bash
npm start
```

---

## 7. ปัญหาที่ยังเหลือและข้อจำกัดที่ยังไม่ได้ทดสอบ (Known Issues & Limitations)

1. **การติดตั้ง FFmpeg บนเครื่อง Client ในโหมด Production:**
   * ในเครื่องทดสอบปัจจุบัน พบไบนารี FFmpeg/FFprobe ที่ `C:\ffmpeg\bin\` และใน System PATH ทำให้ฟังก์ชันสกัด Metadata และภาพตัวอย่างทำงานได้สมบูรณ์
   * อย่างไรก็ตาม ในขั้นตอนการทำ Installer สำหรับแจกจ่ายผู้ใช้ทั่วไป (Packaging) จำเป็นต้องรวมไฟล์ `ffmpeg.exe` และ `ffprobe.exe` ไว้ในโฟลเดอร์ `resources/bin/` ของ Electron Application เพื่อไม่ให้ผู้ใช้ต้องติดตั้ง FFmpeg เอง
2. **การตรวจสอบกับ TikTok Studio จริง:**
   * ใน Phase 3 นี้เป็นการเตรียมความพร้อมของ Engine ภายในเครื่องเท่านั้น ข้อมูลสินค้ายังถือเป็น `verified: false` (บันทึกโดยผู้ใช้) จนกว่าจะมีการล็อกอินและตรวจสอบกับ TikTok ใน Phase 4
3. **การรับประกันการไม่โพสต์ซ้ำ:**
   * ระบบป้องกันการส่งงานซ้ำในเครื่องคอมพิวเตอร์ผ่าน State Machine และ Crash Recovery ได้สมบูรณ์ แต่ยังไม่สามารถรับประกันได้ว่า TikTok Studio รับคำสั่งไปแล้วหรือไม่ จนกว่าจะเริ่มทำระบบ Browser Automation ตรวจสอบ DOM จริงใน Phase 4

---

## 8. สิ่งที่ต้องดำเนินการต่อใน PHASE 4 (Next Phase: Browser Automation)

ใน **PHASE 4 — TIKTOK STUDIO AUTOMATION CORE** จะนำ Foundation ทั้งหมดที่สร้างไว้ใน Phase 1, 2 และ 3 ไปเชื่อมต่อกับเว็บ TikTok Studio จริง:

1. **Chromium Session & Profile Manager:** จัดเก็บและโหลด Browser Profile จากโฟลเดอร์ User Data เพื่อจดจำการล็อกอิน TikTok Studio โดยไม่ต้องบันทึกรหัสผ่านของผู้ใช้
2. **Login & Session Checker:** ตรวจสอบสถานะการเข้าสู่ระบบ หากหลุดจาก Session ให้แสดงปุ่มเพื่อให้ผู้ใช้ล็อกอินผ่านหน้าต่างเบราว์เซอร์
3. **Workflow Step 1-9 Implementation:**
   * อัปโหลดไฟล์วิดีโอจริงเข้าสู่หน้า `https://www.tiktok.com/tiktokstudio/content`
   * กรอกแคปชันและแฮชแท็ก
   * เปิดหน้าต่าง "เพิ่มลิงก์" $\rightarrow$ เลือก "สินค้า"
   * เลือกแท็บ "ร้านของฉัน" หรือ "นำเสนอสินค้า"
   * ค้นหาและปักตะกร้าสินค้าโดยใช้ **Product ID 19 หลัก** เพื่อป้องกันการเลือกผิดตัว
   * ยืนยันชื่อแสดงผลสินค้า (ไม่เกิน 30 ตัวอักษร)
   * เลือกวิธีกำหนดเวลาแบบ "ตั้งเวลา" พร้อมเลือกวันและเวลาตรงตามคิวงาน
   * ตรวจสอบหลักฐานบน DOM ว่า TikTok บันทึกการตั้งเวลาจริง (ไม่สรุปผลเพียงเพราะกดปุ่ม)
4. **Human-in-the-Loop Guards:** ระบบตรวจจับ CAPTCHA / MFA หรือป๊อปอัปแทรกซ้อนเพื่อหยุดรอให้ผู้ใช้ดำเนินการด้วยตนเอง

---

*จบรายงาน PHASE 3 — ระบบพร้อมสำหรับการเริ่มพัฒนา PHASE 4 ตามลำดับ*
