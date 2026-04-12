import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 設定與讀取函數 ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit"
CSV_URL = SHEET_URL.replace('/edit', '/export?format=csv')

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.warning("語音產生失敗")

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        return data.dropna(subset=['kr', 'cn'])
    except Exception as e:
        st.error(f"資料讀取失敗，請確認試算表權限。錯誤：{e}")
        return pd.DataFrame(columns=["chapter", "kr", "cn", "type", "note"])

# --- 2. 每日金句 (Session State 固定) ---
quotes = [
    {"kr": "오늘도 화이팅! 할 수 있어요.", "cn": "今天也要加油！你可以的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"},
    {"kr": "포기하지 마세요, 꿈은 이루어질 거예요.", "cn": "不要放棄，夢想會實現的。"}
]

if 'daily_q' not in st.session_state:
    st.session_state.daily_q = random.choice(quotes)

# --- 3. 介面開始 ---
st.title("🇰🇷 宜真的韓語基地")

# 每日一句區塊
st.info(f"✨ **今日動力**\n### {st.session_state.daily_q['kr']}\n{st.session_state.daily_q['cn']}")
if st.button("🔊 播放金句語音"):
    play_audio(st.session_state.daily_q['kr'])

st.divider()

# 讀取試算表資料
df = load_data()

if not df.empty:
    # 側邊欄篩選
    st.sidebar.title("🎯 複習篩選")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    
    selected_chapters = st.sidebar.multiselect(
        "選擇要複習的章節 (不選則預設全部)",
        options=all_chapters,
