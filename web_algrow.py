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
# 2. ฟังก์ชันเดิมของคุณ 100% (ห้ามแก้)
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
            model='gemini-2.5-flash', # 📌 ใช้ 2.5-flash ตัวที่คุณรันผ่าน 
            contents=prompt
        )
        return response.text
    except Exception as e:
        st.error(f"❌ ดึงสคริปต์ไม่ได้ (คลิปอาจไม่มีซับไตเติล) สาเหตุ: {e}")
        return None

# ==========================================
# 3. ฟังก์ชันเสริม: วิเคราะห์รูป (Feature 2)
# ==========================================
def analyze_channel_from_image(image_file):
    try:
        img = PIL.Image.open(image_file)
        prompt = "นี่คือภาพหน้าจอจากคลิป YouTube โปรดวิเคราะห์และบอกชื่อช่อง (Channel Name) โลโก้ และเนื้อหาหลักที่เกี่ยวข้องในภาพให้แม่นยำที่สุด"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        return response.text
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาดในการวิเคราะห์ภาพ: {e}"

# ==========================================
# 4. ฟังก์ชันเสริม: ค้นหาช่องและสถิติ (Feature 3 - ใหม่)
# ==========================================
@st.cache_data(ttl=3600)
def get_similar_channels(api_key, query, max_results=5):
    """ค้นหาช่องคู่แข่งและดึงสถิติปัจจบัน"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    try:
        # 1. ค้นหาไอดีช่องจากคีย์เวิร์ด
        search_res = youtube.search().list(q=query, type="channel", part="snippet", maxResults=max_results).execute()
        channel_ids = [item['snippet']['channelId'] for item in search_res.get('items', [])]
        
        if not channel_ids: return []

        # 2. ดึงสถิติของช่องเหล่านั้น
        stats_res = youtube.channels().list(part="snippet,statistics", id=",".join(channel_ids)).execute()
        results = []
        for ch in stats_res.get('items', []):
            results.append({
                "title": ch['snippet']['title'],
                "description": ch['snippet'].get('description', 'ไม่มีคำอธิบายช่อง'),
                "subs": int(ch['statistics'].get('subscriberCount', 0)),
                "views": int(ch['statistics'].get('viewCount', 0)),
                "videos": int(ch['statistics'].get('videoCount', 0)),
                "url": f"https://www.youtube.com/channel/{ch['id']}"
            })
        # เรียงตามจำนวนผู้ติดตามจากมากไปน้อย
        return sorted(results, key=lambda x: x['subs'], reverse=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลช่อง: {e}")
        return []


import re

# ==========================================
# [เพิ่มใหม่] ฟังก์ชันตัวช่วยสำหรับ Feature 4
# ==========================================
def extract_video_id(url):
    """สกัดเอาแค่รหัส Video ID ออกมาจากลิงก์ YouTube"""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# ==========================================
# [เพิ่มใหม่] ฟังก์ชันดึงคลิปล่าสุดของช่องคู่แข่ง
# ==========================================
def get_recent_videos_for_channel(api_key, channel_id, max_results=10):
    youtube = build('youtube', 'v3', developerKey=api_key)
    try:
        # ค้นหาคลิปล่าสุดของช่องนั้น
        search_res = youtube.search().list(
            part="snippet", channelId=channel_id, maxResults=max_results, order="date", type="video"
        ).execute()
        
        video_ids = [item['id']['videoId'] for item in search_res.get('items', [])]
        if not video_ids: return []
        
        # ดึงยอดวิวของคลิปเหล่านั้น
        stats_res = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()
        videos_data = []
        for v in stats_res.get('items', []):
            videos_data.append({
                "title": v['snippet']['title'],
                "views": int(v['statistics'].get('viewCount', 0)),
                "date": v['snippet']['publishedAt'][:10] # เอาแค่วันที่ YYYY-MM-DD
            })
        return videos_data
    except Exception as e:
        return []

def analyze_channel_strategy(channel_name, videos_data):
    """ให้ AI วิเคราะห์แนวทางของช่องจากคลิปล่าสุด"""
    prompt = f"""
    คุณคือนักวิเคราะห์การเติบโตบน YouTube (YouTube Strategist)
    นี่คือข้อมูลคลิปล่าสุด 10 คลิปจากช่อง '{channel_name}':
    {videos_data}
    
    โปรดวิเคราะห์ข้อมูลเหล่านี้และเขียนสรุปสั้นๆ กระชับ เป็นข้อๆ ดังนี้:
    1. 🎯 Content Trend: ช่วงนี้ช่องนี้กำลังเน้นทำเนื้อหาแนวไหน?
    2. 🔥 Winning Format: คลิปไหนที่ยอดวิวโดดเด่นกว่าเพื่อน และคิดว่าเป็นเพราะอะไร? (เช่น ชื่อคลิปน่าสนใจ, เกาะกระแส)
    3. 💡 Actionable Advice: แนะนำกลยุทธ์ 1-2 ข้อ ที่เราสามารถนำมาปรับใช้กับช่องของเราได้เพื่อแย่งยอดวิว
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', # ใช้รุ่นที่รันผ่าน
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ ไม่สามารถวิเคราะห์ได้ในขณะนี้: {e}"

# ==========================================
# 5. Web UI (ระบบ Sidebar Menu)
# ==========================================
st.sidebar.title("🚀 My AlGrow Menu")
menu = st.sidebar.radio(
    "เลือกเครื่องมือ:", 
    [
        "🎯 1. ค้นหาคลิป & Rewrite", 
        "📸 2. Find Channel (จากรูป)", 
        "📊 3. Similar Channels & Trends",
        "🕵️‍♂️ 4. YouTube Scraper", # 📌 เพิ่มเมนูที่ 4 ตรงนี้
        "💡 5. AI Niche Explorer" # 📌 เพิ่มเมนูที่ 5 ตรงนี้
    ]
)

# ------------------------------------------
# หน้าฟีเจอร์ที่ 1 (ของเดิมของคุณ)
# ------------------------------------------
if menu == "🎯 1. ค้นหาคลิป & Rewrite":
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
# หน้าฟีเจอร์ที่ 2 (Find Channel)
# ------------------------------------------
elif menu == "📸 2. Find Channel (จากรูป)":
    st.title("📸 Find Channel")
    st.markdown("แคปภาพหน้าจอคลิปที่คุณสนใจ แล้วอัปโหลดให้ AI วิเคราะห์หาชื่อช่องและเจาะลึกเนื้อหา")
    
    uploaded_file = st.file_uploader("อัปโหลดภาพ Screenshot (รองรับ JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="ภาพที่คุณอัปโหลด", use_container_width=True)
        if st.button("🔍 วิเคราะห์หาช่องคู่แข่ง", type="primary"):
            with st.spinner("🤖 AI กำลังสแกนรูปภาพ..."):
                analysis_result = analyze_channel_from_image(uploaded_file)
                st.success("✅ วิเคราะห์เสร็จสิ้น!")
                st.info(analysis_result)

# ------------------------------------------
# หน้าฟีเจอร์ที่ 3 (Similar Channels & Trends - อัปเกรด AI Analysis)
# ------------------------------------------
elif menu == "📊 3. Similar Channels & Trends":
    st.title("📊 Similar Channels & Trends")
    st.markdown("ค้นหาช่องคู่แข่งใน Niche ของคุณ และให้ AI วิเคราะห์สถิติเพื่อเจาะลึกแนวทางการเติบโต")
    
    niche_keyword = st.text_input("🔍 พิมพ์ Niche หรือแนวช่องของคุณ (เช่น เล่าเรื่องผี, AI Tools):")
    
    if niche_keyword:
        with st.spinner("กำลังสแกนหาช่องคู่แข่งในตลาด..."):
            channels = get_similar_channels(YOUTUBE_API_KEY, niche_keyword)
            
        if channels:
            st.success(f"พบ {len(channels)} ช่องที่เป็นคู่แข่งหรือมีเนื้อหาใกล้เคียง!")
            
            for ch in channels:
                st.markdown(f"### 📺 [{ch['title']}]({ch['url']})")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("👥 ผู้ติดตาม (Subs)", f"{ch['subs']:,}")
                col2.metric("👁️ ยอดวิวรวม", f"{ch['views']:,}")
                col3.metric("🎬 จำนวนคลิป", f"{ch['videos']:,}")
                
                st.markdown(f"📝 **รายละเอียดช่อง:** {ch['description'][:200]}...")
                
                # 📌 ปุ่มกดให้ AI วิเคราะห์กลยุทธ์ (ใช้ key=ch['id'] เพื่อไม่ให้ปุ่มทับซ้อนกัน)
                if st.button(f"🧠 ให้ AI วิเคราะห์กลยุทธ์ของช่อง '{ch['title']}'", key=ch['url']):
                    with st.spinner(f"กำลังดึงข้อมูลคลิปล่าสุดและวิเคราะห์แนวทางการเติบโต..."):
                        recent_videos = get_recent_videos_for_channel(YOUTUBE_API_KEY, ch['url'].split('/')[-1])
                        
                        if recent_videos:
                            # ให้ AI วิเคราะห์
                            analysis_result = analyze_channel_strategy(ch['title'], recent_videos)
                            st.markdown("#### 📈 บทวิเคราะห์แนวทางการเติบโต (โดย AI)")
                            st.info(analysis_result)
                            
                            # แถมข้อมูลดิบให้ดูด้วยแบบพับเก็บได้
                            with st.expander("ดูรายการคลิปล่าสุดที่นำมาวิเคราะห์"):
                                for v in recent_videos:
                                    st.write(f"- {v['date']} | วิว: {v['views']:,} | {v['title']}")
                        else:
                            st.warning("ไม่สามารถดึงข้อมูลคลิปล่าสุดได้ หรือช่องนี้อาจไม่มีคลิปใหม่")
                
                st.divider() # เส้นคั่นระหว่างช่อง
        else:
            st.warning("❌ ไม่พบช่องที่เกี่ยวข้อง ลองใช้คีย์เวิร์ดที่กว้างขึ้นดูนะครับ")


# ------------------------------------------
# หน้าฟีเจอร์ที่ 4 (YouTube Scraper)
# ------------------------------------------
elif menu == "🕵️‍♂️ 4. YouTube Scraper":
    st.title("🕵️‍♂️ YouTube Scraper")
    st.markdown("ดึงข้อมูล SEO, Tags, และสคริปต์ (Transcript) จากคลิป YouTube คู่แข่งได้ในพริบตา")
    
    # ช่องใส่ลิงก์
    video_url = st.text_input("🔗 วางลิงก์ YouTube ที่ต้องการเจาะข้อมูลที่นี่:")
    
    if video_url:
        video_id = extract_video_id(video_url)
        
        if video_id:
            with st.spinner("กำลังดูดข้อมูลหลังบ้านของคลิปนี้..."):
                try:
                    # 1. ดึงข้อมูล SEO และสถิติ
                    yt = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
                    res = yt.videos().list(part="snippet,statistics", id=video_id).execute()
                    
                    if res.get('items'):
                        item = res['items'][0]
                        snippet = item['snippet']
                        stats = item.get('statistics', {})
                        
                        st.subheader(snippet['title'])
                        
                        # แสดงหน้าปัดสถิติ
                        col1, col2, col3 = st.columns(3)
                        col1.metric("👁️ ยอดวิว", f"{int(stats.get('viewCount', 0)):,}")
                        col2.metric("👍 ยอดไลก์", f"{int(stats.get('likeCount', 0)):,}")
                        col3.metric("📅 วันที่ลงคลิป", snippet['publishedAt'][:10])
                        
                        st.divider()
                        
                        # แสดง Tags เพื่อเอาไปใช้ทำ SEO
                        tags = snippet.get('tags', [])
                        st.markdown("### 🏷️ SEO Tags ของคลิปนี้")
                        if tags:
                            st.code(", ".join(tags), language="text")
                        else:
                            st.info("คลิปนี้ไม่ได้ใส่ Tags ซ่อนไว้")
                        
                        st.markdown("### 📝 คำอธิบายคลิป (Description)")
                        st.text_area("", snippet.get('description', ''), height=150)
                        
                        # 2. ดึง Transcript
                        st.markdown("### 💬 สคริปต์วิดีโอ (Transcript)")
                        try:
                            transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['th', 'en'])
                            transcript_text = TextFormatter().format_transcript(transcript_list)
                            
                            st.text_area("", transcript_text, height=300)
                            
                            # ปุ่มดาวน์โหลดข้อมูลทั้งหมดรวมกัน
                            st.download_button(
                                label="💾 ดาวน์โหลดข้อมูล (สคริปต์ + Tags)", 
                                data=f"หัวข้อ: {snippet['title']}\nลิงก์: {video_url}\n\n[SEO Tags]\n{', '.join(tags)}\n\n[สคริปต์]\n{transcript_text}", 
                                file_name=f"SCRAPED_{video_id}.txt",
                                mime="text/plain"
                            )
                        except Exception:
                            st.warning("⚠️ ไม่สามารถดูดสคริปต์ได้: คลิปนี้อาจจะไม่มีซับไตเติล (CC) ให้ดึง")
                    else:
                        st.error("❌ ไม่พบข้อมูลวิดีโอนี้ (วิดีโออาจถูกลบหรือตั้งเป็นส่วนตัว)")
                        
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        else:
            st.error("⚠️ ลิงก์ไม่ถูกต้อง กรุณาก๊อปปี้ลิงก์ YouTube มาวางให้ครบถ้วนครับ")

# ------------------------------------------
# หน้าฟีเจอร์ที่ 5 (AI Niche Explorer)
# ------------------------------------------
elif menu == "💡 5. AI Niche Explorer":
    st.title("💡 AI Niche Explorer (ค้นหาไอเดียทำช่อง)")
    st.markdown("ตันใช่ไหม? ไม่รู้จะทำช่องแนวไหนดี? ให้ AI กุนซือของเราช่วยวิเคราะห์เทรนด์และแจก Keyword ให้คุณเอาไปลุยต่อได้เลย")
    
    # ให้ผู้ใช้เลือกหมวดหมู่กว้างๆ หรือเลือกแบบสุ่ม
    category = st.selectbox(
        "📂 เลือกหมวดหมู่ความสนใจของคุณ (หรือเลือก 'สุ่มไอเดียแปลกใหม่'):",
        [
            "🎲 สุ่มไอเดียแปลกใหม่ (Surprise Me!)",
            "👻 ลี้ลับ / สยองขวัญ / เล่าเรื่องผี",
            "💰 การเงิน / ธุรกิจ / หาเงินออนไลน์",
            "📱 ไอที / AI / แกดเจ็ต",
            "🧠 จิตวิทยา / พัฒนาตัวเอง",
            "🍜 อาหาร / รีวิวร้านเด็ด",
            "🎬 สปอยล์หนัง / สรุปซีรีส์",
            "🐾 สัตว์เลี้ยง / คลิปตลก",
            "🎭 ช่องแบบไม่เปิดหน้า (Faceless Channel)"
        ]
    )
    
    # ระบุกลุ่มเป้าหมาย (Optional)
    target_audience = st.radio("🎯 กลุ่มเป้าหมายหลักของคุณคือใคร?", ["คนไทย (เนื้อหาภาษาไทย)", "ต่างชาติ (เนื้อหาภาษาอังกฤษเพื่อรับค่าโฆษณาสูง)"], horizontal=True)
    
    if st.button("🚀 ค้นหา Niche และ Keyword ทำเงิน", type="primary"):
        with st.spinner("🤖 กุนซือ AI กำลังวิเคราะห์เทรนด์และดึง Keyword ที่ดีที่สุดมาให้..."):
            
            language_pref = "ภาษาไทย" if target_audience == "คนไทย (เนื้อหาภาษาไทย)" else "ภาษาอังกฤษ"
            
            prompt = f"""
            คุณคือนักกลยุทธ์ YouTube มือทอง (YouTube Strategist) ผู้เชี่ยวชาญการหา Niche ตลาดบลูโอเชียน
            โจทย์: ผู้ใช้งานต้องการทำช่อง YouTube แบบ Shorts/ยาว ในหมวดหมู่: '{category}' เน้นกลุ่มเป้าหมาย: '{language_pref}'
            
            โปรดคิดไอเดีย 'Niche เฉพาะกลุ่ม' (Micro-Niche) ที่กำลังเป็นเทรนด์และมีโอกาสเติบโตสูง จำนวน 3 ไอเดีย
            และในแต่ละไอเดีย ให้ระบุรายละเอียดดังนี้:
            
            1. 📌 ชื่อ Niche: (เช่น เรื่องผีในโรงพยาบาล, AI สำหรับคนทำงานออฟฟิศ)
            2. 💡 ทำไมถึงน่าสนใจ?: (บอกเหตุผลสั้นๆ ว่าทำไมคนถึงชอบดู)
            3. 🔑 Keywords สำหรับเอาไปค้นหา: (ให้คีย์เวิร์ดแบบเป๊ะๆ 3-5 คำ ที่ผู้ใช้สามารถก๊อปปี้ไปวางในระบบค้นหาคลิปคู่แข่งได้ทันที)
            4. 🎬 ตัวอย่างชื่อคลิป: (คิดชื่อคลิปที่ดึงดูดคนดูให้ 2 ชื่อ)
            
            จัดรูปแบบให้สวยงาม อ่านง่าย ใช้ Emoji ประกอบ
            """
            
            try:
                # เรียกใช้ AI (เวอร์ชัน 2.5 ตามที่คุณใช้รันผ่าน)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                st.success("✅ วิเคราะห์เสร็จสิ้น! ก๊อปปี้ Keyword ด้านล่างไปลุยในเมนู 'ค้นหาคลิป' ได้เลย")
                st.markdown("---")
                st.info(response.text)
                
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์: {e}")
