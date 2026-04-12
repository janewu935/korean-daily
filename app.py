import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- CSS 樣式：TWS 應援藍視覺 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; margin-bottom: 5px; }
    .stInfo { background-color: #E6F3FF !important; border-left: 5px solid #007FFF !important; color: #007FFF !important; font-weight: bold; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    h3 { color: #007FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 究極語法拼湊引擎 (L1-L12) ---
def generate_ultimate_quiz():
    subjects = [
        {"cn": "我", "kr": "저는"}, {"cn": "老師", "kr": "선생님은"}, 
        {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"},
        {"cn": "歐巴", "kr": "오빠는"}, {"cn": "姐姐", "kr": "언니는"}
    ]
    # 動作零件庫
    actions = [
        {"cn": "吃麵包", "base": "빵을 먹다", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "want": "빵을 먹고 싶어 해요", "neg": "빵을 먹지 않아요", "req": "빵을 먹어 주세요", "can": "빵을 먹을 수 있어요"},
        {"cn": "喝咖啡", "base": "커피를 마시다", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "want": "커피를 마시고 싶어 해요", "neg": "커피를 마시지 않아요", "req": "커피를 마셔 주세요", "can": "커피를 마실 수 있어요"},
        {"cn": "看電影", "base": "영화를 보다", "pol": "영화를 봐요", "past": "영화를 봤어요", "want": "영화를 보고 싶어 해요", "neg": "영화를 보지 않아요", "req": "영화를 봐 주세요", "can": "영화를 볼 수 있어요"},
        {"cn": "買衣服", "base": "옷을 사다", "pol": "옷을 사요", "past": "옷을 샀어요", "want": "옷을 사고 싶어 해요", "neg": "옷을 사지 않아요", "req": "옷을 사 주세요", "can": "옷을 살 수 있어요"},
        {"cn": "學習韓語", "base": "한국어를 공부하다", "pol": "한국어를 공부해요", "past": "한국어를 공부했어요", "want": "한국어를 공부하고 싶어 해요", "neg": "한국어를 공부하지 않아요", "req": "한국어를 공부해 주세요", "can": "한국어를 공부할 수 있어요"},
        {"cn": "做運動", "base": "운동을 하다", "pol": "운동을 해요", "past": "운동을 했어요", "want": "운동을 하고 싶어 해요", "neg": "운동을 하지 않아요", "req": "운동을 해 주세요", "can": "운동을 할 수 있어요"},
        {"cn": "睡覺", "base": "자다", "pol": "자요", "past": "잤어요", "want": "자고 싶어 해요", "neg": "자지 않아요", "req": "자 주세요", "can": "잘 수 있어요"}
    ]
    
    # 隨機抽取文法時態
    grammar_type = random.choice(["pol", "past", "want", "neg", "req", "can"])
    sub = random.choice(subjects)
    act = random.choice(actions)
    
    kr_text = ""
    cn_text = f"{sub['cn']}"
    
    if grammar_type == "pol":
        kr_text = f"{sub['kr']} {act['pol']}"
        cn_text += f"{act['cn']}。"
    elif grammar_type == "past":
        kr_text = f"{sub['kr']} {act['past']}"
        cn_text += f"昨天{act['cn']}了。"
    elif grammar_type == "neg":
        kr_text = f"{sub['kr']} {act['neg']}"
        cn_text += f"不{act['cn']}。"
    elif grammar_type == "req":
        kr_text = f"{act['req']}"
        cn_text = f"請{act['cn']}。"
    elif grammar_type == "can":
        kr_text = f"{sub['kr']} {act['can']}"
        cn_text += f"會{act['cn']}。"
    elif grammar_type == "want":
        if sub['cn'] == "我":
            kr_text = f"{sub['kr']} {act['want'].replace('해 해요', '해요')}"
            cn_text += f"想{act['cn']}。"
        else:
            kr_text = f"{sub['kr']} {act['want']}"
            cn_text += f"想{act['cn']}。"
            
    return {"cn": cn_text, "kr": kr_text}

# --- 2. 工具函數 ---
def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.error("語音產生失敗")

def clean_text(text):
    return re.sub(r'[^\w\s]', '', str(text)).strip()

# --- 3. 介面設計 ---
st.markdown('<p class="main-title">💙 韓語筆記 💙</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #007FFF; font-weight: bold;'>24/7 With Us! 大家的韓國語挑戰模式</p>", unsafe_allow_html=True)

# 隨機翻譯挑戰
st.subheader("✍️ 文法拼湊大挑戰")

if 'dyn_quiz' not in st.session_state:
    st.session_state.dyn_quiz = generate_ultimate_quiz()
if 'dyn_input_id' not in st.session_state:
    st.session_state.dyn_input_id = 0

dq = st.session_state.dyn_quiz

with st.container():
    st.info(f"💡 **請翻譯：** 「 {dq['cn']} 」")
    
    # 這裡的 Key 會隨 ID 變動，確保「換一題」時輸入框清空
    user_trans = st.text_input("在此輸入韓文答案：", key=f"dyn_in_{st.session_state.dyn_input_id}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("驗證答案"):
            if user_trans:
                if clean_text(user_trans) == clean_text(dq['kr']):
                    st.balloons(); st.success("🎉 太厲害了！完全正確！")
                else:
                    st.error(f"❌ 錯誤！正確答案是：\n{dq['kr']}")
                play_audio(dq['kr'])
            else:
                st.warning("要先打字喔！")
    with c2:
        if st.button("換下一題"):
            st.session_state.dyn_quiz = generate_ultimate_quiz()
            st.session_state.dyn_input_id += 1
            st.rerun()

st.divider()

# --- 4. 原有的 Excel 讀取功能 ---
@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df.dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

df = load_data()
if not df.empty:
    st.subheader("🎯 我的單字庫複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("篩選 Excel 章節：", all_chapters)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cats = ["單字", "文法", "發音"]
    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cats[i]
            tmp = df[df['type'] == target_cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            if not tmp.empty:
                tab_id_key = f"input_id_{target_cat}"
                if tab_id_key not in st.session_state: st.session_state[tab_id_key] = 0
                q_key = f"quiz_item_{target_cat}"
                if q_key not in st.session_state: st.session_state[q_key] = tmp.sample(1).iloc[0]
                item = st.session_state[q_key]
                st.write(f"📍 **章節：{item['chapter']}**")
                st.markdown(f"### 題目：{item['cn']}")
                u_in = st.text_input("輸入回答", key=f"input_{target_cat}_{st.session_state[tab_id_key]}")
                if st.button("檢查", key=f"btn_{target_cat}"):
                    if clean_text(u_in) == clean_text(str(item['kr'])):
                        st.balloons(); st.success("正確！")
                    else:
                        st.error(f"正確答案：{item['kr']}")
                    play_audio(item['kr'])
                if st.button("下一題", key=f"next_{target_cat}"):
                    if q_key in st.session_state: del st.session_state[q_key]
                    st.session_state[tab_id_key] += 1
                    st.rerun()

st.divider()
st.markdown(f"**[🔗 打開 Excel 試算表](https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit)**")
