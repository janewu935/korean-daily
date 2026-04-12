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

@st.cache_data(ttl=30)
def load_data():
    data = pd.read_csv(CSV_URL)
    return data.dropna(subset=['kr', 'cn'])

# --- 2. 每日金句 ---
quotes = [
    {"kr": "오늘도 화이팅! 할 수 있어요.", "cn": "今天也要加油！你可以的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"}
]

st.title("🇰🇷 宜真的韓語基地")

with st.container():
    if 'daily_q' not in st.session_state:
        st.session_state.daily_q = random.choice(quotes)
    q = st.session_state.daily_q
    st.info(f"✨ **今日動力**\n### {q['kr']}\n{q['cn']}")
    if st.button("🔊 播放金句語音"):
        play_audio(q['kr'])

st.divider()

# --- 3. 核心邏輯 ---
try:
    df = load_data()
    st.sidebar.markdown(f"[🔗 點我打開試算表]({SHEET_URL})")

    tab1, tab2, tab3 = st.tabs(["📖 單字", "📝 文法", "📢 發音"])

    def QuizSection(category):
        target_df = df[df['type'] == category]
        if target_df.empty:
            st.write(f"目前還沒有『{category}』的資料。")
            return

        # 使用 session_state 來固定當前的題目，防止輸入時重新整理
        state_key = f"current_item_{category}"
        if state_key not in st.session_state:
            st.session_state[state_key] = target_df.sample(1).iloc[0]
        
        item = st.session_state[state_key]

        st.caption(f"📍 章節：{item['chapter']}")
        st.subheader(f"{category}練習")
        st.warning(f"請回答：**{item['cn']}**")

        mode = st.radio("選擇模式", ["快速複習 (Go/No Go)", "打字挑戰 (Typing)"], key=f"mode_{category}")

        if mode == "快速複習 (Go/No Go)":
            with st.expander("點我看答案與聽發音"):
                st.success(f"結果：{item['kr']}")
                play_audio(str(item['kr']))
                if pd.notna(item['note']):
                    st.info(f"💡 備註：{item['note']}")
        
        else: # 打字挑戰模式
            user_input = st.text_input("請輸入韓文拼寫：", key=f"input_{category}")
            if st.button("檢查答案", key=f"check_{category}"):
                if user_input.strip() == str(item['kr']).strip():
                    st.balloons()
                    st.success("🎉 完全正確！")
                    play_audio(str(item['kr']))
                else:
                    st.error(f"❌ 拼寫有誤，再試一次！正確答案是：{item['kr']}")
                    play_audio(str(item['kr']))

        if st.button(f"換下一個 {category}", key=f"next_{category}"):
            del st.session_state[state_key]
            st.rerun()

    with tab1: QuizSection("單字")
    with tab2: QuizSection("文法")
    with tab3: QuizSection("發音")

except Exception as e:
    st.error(f"讀取失敗：{e}")
