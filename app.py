import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re
import time

# 設定
st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- 自定義 CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .stInfo { background-color: #E6F3FF !important; border-left: 5px solid #007FFF !important; color: #007FFF !important; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 1. 讀取與發音
@st.cache_data(ttl=10)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        return pd.read_csv(csv_url).dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.error("發音失敗")

def clean_text(text):
    return re.sub(r'[^\w\s]', '', str(text)).strip()

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語筆記 💙</p>', unsafe_allow_html=True)

# 2. 每日翻譯挑戰區
lesson_quotes = [
    {"ch": "L1 (이다)", "cn": "我是台灣人。", "kr": "저는 대만 사람이에요."},
    {"ch": "L2 (이/가 아니다)", "cn": "這不是手機。", "kr": "이것은 휴대폰이 아니에요."},
    {"ch": "L3 (있다/없다)", "cn": "弟弟在教室裡。", "kr": "남동생이 교실에 있어요."},
    {"ch": "L4 (아요/어요)", "cn": "我也買蘋果。", "kr": "저도 사과를 사요."},
    {"ch": "L5 (았/었)", "cn": "昨天做了運動。", "kr": "어제 운동을 했어요."},
    {"ch": "L6 (하고/와/과)", "cn": "我喝咖啡和水。", "kr": "커피하고 물을 마셔요."},
]

# 初始化題目與輸入框的「隨機 ID」
if 'daily_quiz' not in st.session_state:
    st.session_state.daily_quiz = random.choice(lesson_quotes)
if 'daily_input_id' not in st.session_state:
    st.session_state.daily_input_id = 0

dq = st.session_state.daily_quiz

with st.container():
    st.info(f"💡 **請翻譯：** 「 {dq['cn']} 」")
    
    # 關鍵：這裡的 key 加上了隨機 ID，變動時會強制清空
    user_trans = st.text_input("在下方輸入韓文：", key=f"daily_input_{st.session_state.daily_input_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("驗證我的翻譯"):
            if not user_trans:
                st.warning("要先輸入內容才能驗證喔！")
            else:
                if clean_text(user_trans) == clean_text(dq['kr']):
                    st.balloons()
                    st.success("🎉 正確！")
                    play_audio(dq['kr'])
                else:
                    st.error("⚠️ 發現錯誤！")
                    st.write(f"**你的輸入：** {user_trans}")
                    st.write(f"**正確解答：** {dq['kr']}")
                    play_audio(dq['kr'])
    
    with col2:
        if st.button("換一題"):
            st.session_state.daily_quiz = random.choice(lesson_quotes)
            # 更改 ID，讓 Streamlit 生成一個全新的輸入框
            st.session_state.daily_input_id += 1 
            st.rerun()

st.divider()

# --- 3. 原有的 Excel 複習核心 ---
df = load_data()
if not df.empty:
    st.subheader("🎯 章節題庫複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇複習章節：", all_chapters)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])

    for i, tab in enumerate(tabs):
        with tab:
            cat = ["單字", "文法", "發音"][i]
            tmp = df[df['type'] == cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if not tmp.empty:
                # 每個 Tab 也給它一個獨立的 input_id
                tab_id_key = f"input_id_{cat}"
                if tab_id_key not in st.session_state:
                    st.session_state[tab_id_key] = 0
                
                quiz_key = f"quiz_item_{cat}"
                if quiz_key not in st.session_state:
                    st.session_state[quiz_key] = tmp.sample(1).iloc[0]
                
                item = st.session_state[quiz_key]
                st.write(f"📍 **章節：{item['chapter']}**")
                st.markdown(f"### 題目：{item['cn']}")

                # 同樣的 Key 隨機化技巧
                u_in = st.text_input("輸入韓文回答", key=f"input_{cat}_{st.session_state[tab_id_key]}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("檢查答案", key=f"btn_{cat}"):
                        if clean_text(u_in) == clean_text(str(item['kr'])):
                            st.balloons(); st.success("正確！")
                        else:
                            st.error(f"正確答案：{item['kr']}")
                        play_audio(item['kr'])
                with c2:
                    if st.button("下一題", key=f"next_{cat}"):
                        del st.session_state[quiz_key]
                        st.session_state[tab_id_key] += 1 # 強制刷新輸入框
                        st.rerun()

    st.divider()
    st.markdown(f"**[🔗 打開 Excel 試算表](https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit)**")
