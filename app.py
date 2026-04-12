import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

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

# 2. 翻譯挑戰題庫 (《大家的韓國語》第一冊文法精選)
lesson_quotes = [
    {"ch": "L1 (이다)", "cn": "我是台灣人。", "kr": "저는 대만 사람이에요."},
    {"ch": "L2 (이/가 아니다)", "cn": "這不是手機。", "kr": "이것은 휴대폰이 아니에요."},
    {"ch": "L3 (있다/없다)", "cn": "弟弟在教室裡。", "kr": "남동생이 교실에 있어요."},
    {"ch": "L4 (아요/어요)", "cn": "我也買蘋果。", "kr": "저도 사과를 사요."},
    {"ch": "L5 (았/었)", "cn": "昨天做了運動。", "kr": "어제 운동을 했어요."},
    {"ch": "L6 (하고/와/과)", "cn": "我喝咖啡和水。", "kr": "커피하고 물을 마셔요."},
    {"ch": "L7 (方向助詞)", "cn": "去銀行。", "kr": "은행에 가요."}
]

st.subheader("✍️ 今日文法挑戰：互動翻譯")

# 初始化題目與輸入框狀態
if 'daily_quiz' not in st.session_state:
    st.session_state.daily_quiz = random.choice(lesson_quotes)
if 'user_input_val' not in st.session_state:
    st.session_state.user_input_val = ""

dq = st.session_state.daily_quiz

with st.container():
    st.info(f"💡 **請翻譯：** 「 {dq['cn']} 」")
    
    # 這裡的 value 綁定 session_state，實現自動清空
    user_trans = st.text_input("在下方輸入韓文：", value=st.session_state.user_input_val, key="daily_trans_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("驗證我的翻譯"):
            if not user_trans:
                st.warning("要先輸入內容才能驗證喔！")
            else:
                if clean_text(user_trans) == clean_text(dq['kr']):
                    st.balloons()
                    st.success("🎉 太完美了！完全正確。")
                    play_audio(dq['kr'])
                else:
                    st.error("⚠️ 發現 Bug 了！")
                    st.write(f"**你的輸入：** {user_trans}")
                    st.write(f"**正確解答：** {dq['kr']}")
                    st.info("💡 糾正：請對比一下收音或空格喔！")
                    play_audio(dq['kr'])
    
    with col2:
        if st.button("換一題"):
            # 關鍵：同時更換題目並重置輸入框的值
            st.session_state.daily_quiz = random.choice(lesson_quotes)
            st.session_state.user_input_val = "" 
            # 這裡透過刪除 key 來強迫重新繪製輸入框
            if "daily_trans_input" in st.session_state:
                del st.session_state["daily_trans_input"]
            st.rerun()

st.divider()

# --- 3. 原有的 Excel 章節題庫複習 ---
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
                key = f"quiz_{cat}"
                input_key = f"in_{cat}"
                
                if key not in st.session_state:
                    st.session_state[key] = tmp.sample(1).iloc[0]
                
                item = st.session_state[key]
                st.write(f"📍 **章節：{item['chapter']}**")
                st.markdown(f"### 題目：{item['cn']}")

                u_in = st.text_input("輸入韓文回答", key=input_key)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("檢查答案", key=f"btn_{cat}"):
                        if clean_text(u_in) == clean_text(str(item['kr'])):
                            st.balloons()
                            st.success("正確！")
                        else:
                            st.error(f"正確答案：{item['kr']}")
                        play_audio(item['kr'])
                with c2:
                    if st.button("下一題", key=f"next_{cat}"):
                        # 換題時也把該分頁的輸入框清空
                        del st.session_state[key]
                        if input_key in st.session_state:
                            del st.session_state[input_key]
                        st.rerun()

    st.divider()
    st.markdown(f"**[🔗 打開 Excel 試算表]({url if 'url' in locals() else 'https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit'})**")
