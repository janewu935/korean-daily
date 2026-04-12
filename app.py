import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 設定
st.set_page_config(page_title="宜真韓語基地", page_icon="🇰🇷")

# 1. 讀取函數
@st.cache_data(ttl=10)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    try:
        data = pd.read_csv(csv_url)
        return data.dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

# 2. 發音函數
def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.error("發音產生失敗，請檢查網路連線")

# --- 主介面 ---
st.title("🇰🇷 宜真的韓語基地")

# --- 每日一句區塊 (補回發音按鈕) ---
quotes = [
    {"kr": "오늘도 화이팅! 할 수 있어요.", "cn": "今天也要加油！你可以的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"},
    {"kr": "꿈을 향해 한 걸음씩.", "cn": "朝著夢想一步步前進。"}
]

if 'daily_q' not in st.session_state:
    st.session_state.daily_q = random.choice(quotes)

q = st.session_state.daily_q

with st.container():
    st.info(f"✨ **今日動力**\n### {q['kr']}\n{q['cn']}")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔊 播放"):
            play_audio(q['kr'])
    with col2:
        if st.button("換一句"):
            st.session_state.daily_q = random.choice(quotes)
            st.rerun()

st.divider()

df = load_data()

if not df.empty:
    # --- 章節選擇器 ---
    st.subheader("🎯 篩選章節")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇章節：", all_chapters)
    
    st.divider()

    # 分頁
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    categories = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            cat = categories[i]
            tmp = df[df['type'] == cat]
            if sel_ch:
                tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if tmp.empty:
                st.write(f"目前『{cat}』在所選章節中無資料")
            else:
                key = f"quiz_{cat}"
                if key not in st.session_state:
                    st.session_state[key] = tmp.sample(1).iloc[0]
                
                item = st.session_state[key]
                st.caption(f"📍 來源：{item['chapter']}")
                st.subheader(f"請回答：{item['cn']}")

                mode = st.radio("模式", ["快速", "打字"], key=f"m_{cat}")
                
                if mode == "快速":
                    if st.button("看答案並聽發音", key=f"ans_{cat}"):
                        st.success(f"答案是：{item['kr']}")
                        play_audio(item
