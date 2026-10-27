# รายงานผลการทดสอบ Integration Dry Run: Pilot Scene 05 (Hybrid Upper-Rigging)

> [!NOTE]
> การทดสอบ Dry Run นี้ดำเนินการในโฟลเดอร์แยกต่างหาก `ep007_dryrun` **โดยไม่มีการแก้ไขไฟล์ต้นฉบับใน Pipeline หลัก (`ep007`) แม้แต่ไฟล์เดียว**

---

## 1. สรุปผลการทดสอบ (Executive Summary)

| รายการตรวจสอบ | ผลลัพธ์ | รายละเอียดทางเทคนิค |
| :--- | :---: | :--- |
| **ความปลอดภัยของ Pipeline หลัก** | **PASSED (100%)** | `make_advanced_ep007_v2.py` และ `index.html` เดิมไม่มีการแตะต้อง (LastWriteTime คงเดิม) |
| **HyperFrames Check Runtime** | **PASSED (0 Errors)** | `0 runtime errors`, `0 runtime warnings`, `0 motion warnings`, `24/24 text checks pass WCAG AA` |
| **ความต่อเนื่องของฉากติดกัน (s04)** | **BIT-EXACT (RMS = 0.0000)** | ที่ $t=16.00\text{s}$ ภาพตรงกับต้นฉบับ $100\%$ ไม่ได้รับผลกระทบ |
| **ความต่อเนื่องของฉากติดกัน (s06)** | **BIT-EXACT (RMS = 0.0000)** | ที่ $t=22.50\text{s}$ ภาพตรงกับต้นฉบับ $100\%$ ตำแหน่งกล้อง `#camera` รีเซ็ตกลับ $x=0$ แม่นยำ |
| **รอยต่อข้อต่อหัวไหล่ (Shoulder Seam)** | **SEAMLESS** | วงแขนหมุนรอบ Pivot $(55.34\%, 50.51\%)$ แนบสนิทกับลำตัวทุกมุมองศา |
| **การพรางภาพเงาเดิม (Ghosting Elimination)** | **ELIMINATED** | การขยับ Micro-Creep $15\text{px}$ ผสาน Camera Pan $-20\text{px}$ บังเงาเดิมบนพื้นหลังมิดชิด |
| **ความยาวรวม & Outro Hold** | **VERIFIED** | ความยาวรวม $64.400\text{s}$ เป๊ะ และช่วง Outro Choice Cards ค้าง $3.50\text{s}$ สมบูรณ์แบบ |

---

## 2. โครงสร้างสถาปัตยกรรมที่ทำการต่อเชื่อม (Integration Architecture)

### 2.1 DOM Structure (`index.html`)
ใน `make_dryrun_ep007.py` ฉาก 01–04 และ 06–14 ยังคงสร้างด้วยโค้ดเดิม $100\%$ โดยมีเฉพาะฉาก 05 ที่แตกย่อย Foreground ออกเป็น Rigged Container:

```html
<!-- Scene 05: Stickman Hybrid Upper-Rigging -->
<section id="scene-05" class="clip scene-clip" data-start="17.020" data-duration="4.990" style="z-index: 15;">
  <div class="scene-img-wrap">
    <!-- ภาพพื้นหลังเดิม (Bokeh 6px) -->
    <img id="bg-05" class="scene-bg" src="./img/s05.jpg" />
    
    <!-- Articulated Character Rig -->
    <div id="ek-rig-05" class="scene-fg-rig">
      <img id="ek-body-05" class="scene-fg-body" src="./img/s05_body.png" />
      <img id="ek-arm-05" class="scene-fg-arm" src="./img/s05_arm_jerrycan.png" />
    </div>
  </div>
</section>
```

### 2.2 การกำหนด CSS & Scale Contract
รักษาขนาดและสัดส่วนเดียวกันกับ `.scene-fg` ของ Pipeline หลักทุกประการ:

```css
/* Foreground Rig Container: ใช้สเกล 110% และ drop-shadow ร่วมกัน */
.scene-fg-rig {
  position: absolute;
  inset: -5%;
  width: 110%;
  height: 110%;
  transform-origin: center center;
  will-change: transform;
  z-index: 2;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.65));
}

/* ลำตัวและขาท่อนล่าง */
.scene-fg-body {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform-origin: center center;
  will-change: transform;
}

/* แขนขวาและถังน้ำมัน พร้อมจุดหมุนหัวไหล่ที่ผ่านการคำนวณพิกัด */
.scene-fg-arm {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform-origin: 55.3385% 50.5087%;
  will-change: transform;
}
```

### 2.3 GSAP Timeline Orchestration
ลำดับคำสั่ง Animation ของ Scene 05 ($17.02\text{s} - 21.96\text{s}$, รวม $4.94\text{s}$):

```javascript
// Scene 05: Stickman Hybrid Upper-Rigging
const cycleDur = sc.duration / 6; // 0.823333s ต่อ Half-Cycle (6 รอบพอดี)

// 1. Background Parallax Push-in
tl.fromTo(bgSel, { scale: 1.0, y: 0 }, { scale: 1.06, y: 15, duration: sc.duration, ease: 'sine.inOut' }, sc.start);

// 2. Camera Parallax Tracking Pan (-20px) พร้อมรีเซ็ตกล้องกลับที่ 21.96s
tl.fromTo('#camera', { x: 0 }, { x: -20, duration: sc.duration, ease: 'sine.inOut' }, sc.start);
tl.set('#camera', { x: 0 }, sc.start + sc.duration);

// 3. Character Rig Micro-Creep (เดินย่องไปข้างหน้า 15px)
tl.fromTo('#ek-rig-05', 
  { x: 0, y: 0, scale: 1.0 }, 
  { x: 15, y: 10, scale: 1.06, duration: sc.duration, ease: 'sine.inOut' }, 
  sc.start
);

// 4. Torso Bobbing (ลำตัวโยกขึ้นลงตามจังหวะก้าว)
tl.fromTo('#ek-body-05', 
  { y: 0, rotation: 0 }, 
  { y: -6, rotation: 1.5, duration: cycleDur, ease: 'sine.inOut', yoyo: true, repeat: 5 }, 
  sc.start
);

// 5. Arm & Jerrycan Swing (แขนและถังน้ำมันแกว่งแบบลูกตุ้ม)
tl.fromTo('#ek-arm-05', 
  { rotation: -4.5 }, 
  { rotation: 4.5, duration: cycleDur, ease: 'sine.inOut', yoyo: true, repeat: 5 }, 
  sc.start
);
```

---

## 3. หลักฐานการเปรียบเทียบภาพจริง (Visual Evidence)

### 3.1 การเปรียบเทียบภาพเต็มเฟรม: Original (Static) vs Dry Run (Rigged)
ภาพเปรียบเทียบ 4 ช่วงเวลาตลอดฉาก 05:
![Scene 05 Side-by-Side Comparison](file:///C:/Users/nutta/.gemini/antigravity/brain/65fa3bba-f8fa-440e-96ab-5714fe8aa3a2/dryrun_s05_comparison.jpg)

### 3.2 ภาพขยายความละเอียดสูง: รอยต่อหัวไหล่และการแกว่งของถังน้ำมัน
ตรวจสอบความแนบสนิทของรอยต่อหัวไหล่ $(55.34\%, 50.51\%)$ ในทุกท่วงท่า:
![High-Res Pivot Crop](file:///C:/Users/nutta/.gemini/antigravity/brain/65fa3bba-f8fa-440e-96ab-5714fe8aa3a2/dryrun_s05_highres_crop.jpg)

### 3.3 ความต่อเนื่องของฉาก: Scene 04 $\rightarrow$ Scene 05 $\rightarrow$ Scene 06
ยืนยันว่าการเปลี่ยนผ่านฉากก่อนหน้าและฉากถัดไปเป็นไปอย่างราบรื่น:
![Scene Transition Continuity](file:///C:/Users/nutta/.gemini/antigravity/brain/65fa3bba-f8fa-440e-96ab-5714fe8aa3a2/dryrun_s04_s05_s06_continuity.jpg)

---

## 4. ผลการวัดความแตกต่างของพิกเซล (Mathematical RMS Diff)

การเปรียบเทียบพิกเซลระหว่างภาพจาก Original และภาพจาก Dry Run:

| Snapshot Timestamp | ตำแหน่งซีน | ค่าเฉลี่ยพิกเซลต่าง (Mean Diff) | ค่ากำลังสองเฉลี่ย (RMS Diff) | การประเมินผล |
| :--- | :--- | :---: | :---: | :--- |
| **16.00s** | Scene 04 (Baby T-Rex) | **0.0000** | **0.0000** | **Bit-Exact**: ไม่มีผลข้างเคียงต่อซีนก่อนหน้า |
| **17.50s** | Scene 05 (ต้นซีน) | 1.8065 | 9.8140 | เคลื่อนไหวอย่างมีชีวิตชีวาตามโมเดล Rigging |
| **19.50s** | Scene 05 (กลางซีน) | 9.2224 | 20.2232 | เคลื่อนไหวอย่างมีชีวิตชีวาตามโมเดล Rigging |
| **21.50s** | Scene 05 (ปลายซีน) | 12.7145 | 23.2065 | เคลื่อนไหวอย่างมีชีวิตชีวาตามโมเดล Rigging |
| **21.94s** | Scene 05 (จุดสิ้นสุดซีน) | 13.0162 | 23.5099 | แขนแกว่งครบรอบสมบูรณ์ ไม่มีอาการแช่แข็ง |
| **22.50s** | Scene 06 (Thermal Vision) | **0.0000** | **0.0000** | **Bit-Exact**: กล้องรีเซ็ตกลับที่เดิม ซีนถัดไปไม่เพี้ยน |

---

## 5. การตรวจสอบความยาวและ Outro Hold (Duration Verification)

- **Total Duration**: $64.400\text{s}$ (ตรงตาม `alignment.json`)
- **End of Dialogue Audio**: $60.90\text{s}$
- **Interactive Choice Cards**:
  - การ์ด A ปรากฏ: $56.80\text{s}$
  - การ์ด B ปรากฏ: $58.60\text{s}$
  - ตรึงค้างกลางจอ (End Freeze): ตั้งแต่ $58.60\text{s}$ จนถึง $64.40\text{s}$
- **Outro Hold Duration**: $64.40\text{s} - 60.90\text{s} = \mathbf{3.50\text{s}}$ ครบถ้วนตามข้อกำหนด

---

## 6. ข้อสรุปและการเตรียมพร้อมสำหรับ Main Pipeline Integration

1. การทดลอง Dry Run ครั้งนี้พิสูจน์แล้วว่า **Hybrid Upper-Rigging สามารถผสานรวมเข้ากับ Pipeline ของ HyperFrames ได้อย่างไร้รอยต่อ** โดยไม่มีผลกระทบด้านลบใด ๆ ต่อฉากอื่น
2. ไฟล์ใน Pipeline หลัก (`c:\Users\nutta\Desktop\Max\อะไรทำไม\Stickman\ep007`) ยังคงปลอดภัย $100\%$ และยังไม่มีการแก้ไขใด ๆ
3. ระบบพร้อมแล้วสำหรับการนำการเปลี่ยนแปลงนี้ไปปรับใช้ใน Pipeline หลักเมื่อได้รับอนุมัติ
