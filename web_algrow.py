import streamlit as st
import PIL.Image
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from datetime import datetime, timezone, timedelta
from google import genai

# ==========================================
# 1. ตั้งค่า API Key (ดึงจาก Streamlit Secrets)
# ==========================================
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="My AlGrow", page_icon="🚀", layout="wide")

# ==========================================
# 2. ฟังก์ชันเดิมของคุณ 100% (ไม่แตะต้อง)
# ==========================================
@st.cache_data(ttl=3600)
def find_viral_videos(api_key, search_query, max_results=15, days_ago=7):
    youtube = build('youtube', 'v3', developerKey=api_key)
    now = datetime.now(timezone.utc)
    time_limit = (now - timedelta(days=days_ago)).isoformat().replace("+00:00", "Z")
    try:
        search_response = youtube.search().list(
            q=search_query, part="id", type="video", maxResults=max_results, 
            order="viewCount", publishedAfter=time_limit
        ).execute()
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        if not video_ids: return []
        video_response = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()
        results = []
        for video in video_response.get('items', []):
            if 'viewCount' not in video['statistics']: continue
            title = video['snippet']['title']
            views = int(video['statistics']['viewCount'])
            published_at = datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            hours_since_published = max((now - published_at).total_seconds() / 3600, 1)
            vph = views / hours_since_published
            results.append({
                "title": title, "video_id": video['id'], "views": views,
                "hours_old": round(hours_since_published, 1), "vph": round(vph, 2),
                "url": f"https://www.youtube.com/watch?v={video['id']}"
            })
        return sorted(results, key=lambda x: x['vph'], reverse=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการค้นหา: {e}")
        return []

def scrape_and_rewrite(video_id, title):
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=['th', 'en'])
        formatter = TextFormatter()
        original_text = formatter.format_transcript(fetched_transcript)
        
        prompt = f"""
        สวมบทบาทเป็นนักเขียนบท YouTube Shorts มืออาชีพ ฉันมีสคริปต์จากคลิปไวรัล หน้าที่ของคุณคือ 'เขียนใหม่ทั้งหมด (Rewrite)' 
        เงื่อนไข:
        1. ห้ามคัดลอกประโยคเดิมแบบคำต่อคำ
        2. สร้าง Hook ใหม่ที่ทรงพลังใน 3 วินาทีแรก
        3. ภาษาและโทนเสียง: เล่าเรื่องสนุก เป็นธรรมชาติ
        4. การจัดหน้า: แบ่งย่อหน้าชัดเจน ห้ามใส่คำแนะนำในวงเล็บ
        5. Call to Action: ตอนท้ายคลิปเนียนชวนกดติดตาม
        
        นี่คือสคริปต์ต้นฉบับ:
        {original_text}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash', # 📌 ใช้โมเดล 2.5 ที่คุณรันผ่าน
            contents=prompt
        )
        return response.text
    except Exception as e:
        st.error(f"❌ ดึงสคริปต์ไม่ได้ (คลิปอาจไม่มีซับไตเติล) สาเหตุ: {e}")
        return None

# ==========================================
# 3. ฟังก์ชันใหม่: วิเคราะห์รูปภาพ (Plugin เสริม)
# ==========================================
def analyze_channel_from_image(image_file):
    try:
        img = PIL.Image.open(image_file)
        prompt = "นี่คือภาพหน้าจอจากคลิป YouTube โปรดวิเคราะห์และบอกชื่อช่อง (Channel Name) โลโก้ และเนื้อหาหลักที่เกี่ยวข้องในภาพให้แม่นยำที่สุด"
        response = client.models.generate_content(
            model='gemini-2.5-flash', # ใช้รุ่น 2.5 ที่ผ่านชัวร์ๆ ควบคู่กับรูปภาพ
            contents=[prompt, img]
        )
        return response.text
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาดในการวิเคราะห์ภาพ: {e}"

# ==========================================
# 4. Web UI (ระบบเมนูแยกฟีเจอร์ชัดเจน)
# ==========================================
# สร้าง Sidebar ด้านซ้าย
st.sidebar.title("🚀 My AlGrow Menu")
menu = st.sidebar.radio("เลือกเครื่องมือ:", ["🎯 ค้นหาคลิป & Rewrite", "📸 Find Channel (วิเคราะห์จากรูป)"])

# ------------------------------------------
# หน้าฟีเจอร์ที่ 1 (ของเดิมของคุณ)
# ------------------------------------------
if menu == "🎯 ค้นหาคลิป & Rewrite":
    st.title("🎯 ค้นหาคลิปไวรัล & Rewrite สคริปต์")
    keyword = st.text_input("🔍 พิมพ์คีย์เวิร์ด (เช่น trivia, gadget):")

    if keyword:
        with st.spinner('กำลังค้นหาคลิปพุ่งแรง...'):
            videos = find_viral_videos(YOUTUBE_API_KEY, keyword, days_ago=7)
        
        if videos:
            st.success(f"🏆 พบ {len(videos)} คลิปไวรัลล่าสุด!")
            video_options = {f"{v['title']} (🔥 VPH: {v['vph']:,.0f} | วิว: {v['views']:,})": v for v in videos[:7]}
            selected_option = st.selectbox("เลือกคลิปที่ต้องการนำมา Rewrite:", list(video_options.keys()))
            selected_video = video_options[selected_option]
            
            st.write(f"🔗 [ดูคลิปต้นฉบับ]({selected_video['url']})")
            
            if st.button("✨ ให้ AI เขียนสคริปต์ใหม่", type="primary"):
                with st.spinner(f"🤖 กำลังดึงสคริปต์และให้ AI เขียนใหม่..."):
                    final_script = scrape_and_rewrite(selected_video['video_id'], selected_video['title'])
                    
                    if final_script:
                        st.success("✅ เขียนสคริปต์เสร็จสมบูรณ์!")
                        st.text_area("📝 สคริปต์ของคุณ:", value=final_script, height=400)
                        st.download_button(
                            label="💾 ดาวน์โหลดเป็นไฟล์ .txt",
                            data=f"ไอเดียจากคลิป: {selected_video['title']}\nลิงก์: {selected_video['url']}\n{'='*40}\n\n{final_script}",
                            file_name=f"READY_TO_RECORD_{selected_video['video_id']}.txt",
                            mime="text/plain"
                        )
        else:
            st.warning("❌ ไม่พบวิดีโอไวรัลใหม่ๆ ลองเปลี่ยนคีย์เวิร์ดดูนะครับ")

# ------------------------------------------
# หน้าฟีเจอร์ที่ 2 (เพิ่มใหม่)
# ------------------------------------------
elif menu == "📸 Find Channel (วิเคราะห์จากรูป)":
    st.title("📸 Find Channel")
    st.markdown("แคปภาพหน้าจอคลิปที่คุณสนใจ แล้วอัปโหลดให้ AI วิเคราะห์หาชื่อช่องและเจาะลึกเนื้อหา")
    
    # กล่องอัปโหลดรูปภาพ
    uploaded_file = st.file_uploader("อัปโหลดภาพ Screenshot (รองรับ JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # แสดงรูปที่อัปโหลด
        st.image(uploaded_file, caption="ภาพที่คุณอัปโหลด", use_container_width=True)
        
        # ปุ่มกดวิเคราะห์
        if st.button("🔍 วิเคราะห์หาช่องคู่แข่ง", type="primary"):
            with st.spinner("🤖 AI กำลังสแกนรูปภาพ..."):
                analysis_result = analyze_channel_from_image(uploaded_file)
                st.success("✅ วิเคราะห์เสร็จสิ้น!")
                st.markdown("### 📊 ผลการวิเคราะห์จาก AI")
                st.info(analysis_result)
