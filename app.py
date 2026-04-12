import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 設定與讀取 ---
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

@st.cache_data(ttl=10) # 設定極短快取，讓章節選單更新更即時
def load_data():
    data = pd.read_csv(CSV_URL)
    return data.dropna(subset=['kr', 'cn'])

# --- 2. 每日金句 ---
quotes = [
    {"kr": "오늘도 화이팅! 할 수 있어요.", "cn": "今天也要加油！你可以的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"}
]

st.title("🇰🇷 宜真的韓語基地")

# 每日一句
if 'daily_q' not in st.session_state:
    st.session_state.daily_q = random.choice(quotes)
st.info(f"✨ **今日動力**\n### {st.session_state.daily_q['kr']}\n{st.session_state.daily_q['cn']}")

st.divider()

# --- 3. 核心邏輯與篩選 ---
try:
    df = load_data()
    
    # 側邊欄設定
    st.sidebar.title("🎯 複習篩選")
    all_chapters = sorted(df['chapter'].unique().tolist())
    
    # 章節選擇器
    selected_chapters = st.sidebar.multiselect(
        "選擇要複習的章節 (不選則預設全部)",
        options=all_chapters,
        default=[]
    )
    
    st.sidebar.markdown(f"[🔗 打開試算表]({SHEET_URL})")

    # 分頁功能
    tab1, tab2, tab3 = st.tabs(["📖 單字", "📝 文法", "📢 發音"])

    def QuizSection(category):
        # 1. 先篩選類別
        temp_df = df[df['type'] == category]
        
        # 2. 再篩選章節
        if selected_chapters:
            target_df = temp_df[temp_df['chapter'].isin(selected_chapters)]
        else:
            target_df = temp_df
            
        if target_df.empty:
            st.write(f"⚠️ 在所選章節中找不到『{category}』資料。")
            return

        state_key = f"current_item_{category}"
        if state_key not in st.session_state:
            st.session_state[state_key] = target
