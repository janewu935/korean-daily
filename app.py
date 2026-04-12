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
    .diff-text { color: #FF4B4B; font-weight: bold; text-decoration: underline; }
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

# --- 2. 互動式糾錯邏輯 ---
def clean_text(text):
    # 移除標點符號與前後空格，方便比對
    return re.sub(r'[^\w\s]', '', text).strip()

def check_translation(user_input, correct_answer):
    u = clean_text(user_input)
    c = clean_text(correct_answer)
    if u == c:
        return True, ""
    else:
        # 簡單的逐字對比提示（這裡可以根據需要強化）
        return False, f"接近了！再檢查一下。正確應該是：{correct_answer}"

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語筆記 💙</p>', unsafe_allow_html=True)

# 3. 第一冊文法題庫
lesson_quotes = [
    {"ch": "L1 (이다)", "cn": "我是台灣人。", "kr": "저는 대만 사람이에요."},
    {"ch": "L2 (이/가 아니다)", "cn": "這不是手機。", "kr": "이것은 휴대폰이 아니에요."},
    {"ch": "L3 (있다/없다)", "cn": "弟弟在家裡。", "kr": "남동생이 집에 있어요."},
    {"ch": "L4 (아요/어요)", "cn": "我也買蘋果。", "kr": "저도 사과를 사요."},
    {"ch": "L5 (았/었)", "cn": "昨天做了運動。", "kr": "어제 운동을 했어요."},
    {"ch": "L6 (하고)", "cn": "我喝咖啡和水。", "kr": "커피하고 물을 마셔요."}
]

st.subheader("✍️ 今日文法挑戰：互動翻譯")

if 'daily_quiz' not in st.session_state:
    st.session_state.daily_quiz = random.choice(lesson_quotes)

dq = st.session_state.daily_quiz

with st.container():
    st.info(f"💡 **請翻譯：** 「 {dq['cn']} 」")
    user_trans = st.text_input("在下方輸入韓文：", key="daily_trans_input")
    
    col1, col2 = st.columns(2)
    with col1:
        check_btn = st.button("驗證我的翻譯")
    with col2:
        if st.button("換一題"):
            st.session_state.daily_quiz = random.choice(lesson_quotes)
            st.rerun()
            
    if check_btn:
        if not user_trans:
            st.warning("要先輸入內容才能驗證喔！")
        else:
            is_correct, msg = check_translation(user_trans, dq['kr'])
            if is_correct:
                st.balloons()
                st.success("🎉 太完美了！完全正確。")
                play_audio(dq['kr'])
            else:
                st.error("⚠️ 發現 Bug 了！")
                st.write(f"**你的輸入：** {user_trans}")
                st.write(f"**正確解答：** {dq['kr']}")
                st.info("💡 糾正：請注意助詞或動詞變化的結尾是否正確喔！")
                play_audio(dq['kr'])

st.divider()

# --- 4. 原有的 Excel 複習核心 ---
df = load_data()
if not df.empty:
    st.subheader("🎯 章節題庫複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇複習章節：", all_chapters)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    # ... (後面邏輯維持與之前相同)
    # 此處省略重複代碼以確保你能清楚看到上方的變更
    for i, tab in enumerate(tabs):
        with tab:
            cat = ["單字", "文法", "發音"][i]
            tmp = df[df['type'] == cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            if not tmp.empty:
                key = f"quiz_{cat}"
                if key not in st.session_state: st.session_state[key] = tmp.sample(1).iloc[0]
                item = st.session_state[key]
                st.write(f"📍 **章節：{item['chapter']}**")
                st.markdown(f"### 題目：{item['cn']}")
                # 這裡也套用相同的驗證模式
                u_in = st.text_input("輸入韓文", key=f"q_in_{cat}")
                if st.button("檢查答案", key=f"q_btn_{cat}"):
                    if clean_text(u_in) == clean_text(str(item['kr'])):
                        st.balloons(); st.success("正確！")
                    else:
                        st.error(f"錯誤！正確答案：{item['kr']}")
                    play_audio(item['kr'])
                if st.button("下一題", key=f"q_next_{cat}"):
                    del st.session_state[key]; st.rerun()
