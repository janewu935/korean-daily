import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- CSS 樣式：TWS 應援藍 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .report-box { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 2px solid #007FFF; margin-top: 20px; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化統計與狀態 ---
if 'total' not in st.session_state: st.session_state.total = 0
if 'correct' not in st.session_state: st.session_state.correct = 0
if 'is_testing' not in st.session_state: st.session_state.is_testing = True

def update_stats(is_correct):
    st.session_state.total += 1
    if is_correct: st.session_state.correct += 1

# --- 2. 隨機拼湊引擎 ---
def generate_quiz():
    subjects = [{"cn": "我", "kr": "저는"}, {"cn": "老師", "kr": "선생님은"}, {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"}]
    actions = [
        {"cn": "吃麵包", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "want": "빵을 먹고 싶어 해요", "neg": "빵을 먹지 않아요", "req": "빵을 먹어 주세요"},
        {"cn": "喝咖啡", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "want": "커피를 마시고 싶어 해요", "neg": "커피를 마시지 않아요", "req": "커피를 마셔 주세요"},
        {"cn": "學習韓語", "pol": "한국어를 공부해요", "past": "한국어를 공부했어요", "want": "한국어를 공부하고 싶어 해요", "neg": "한국어를 공부하지 않아요", "req": "한국어를 공부해 주세요"}
    ]
    grammar = random.choice(["pol", "past", "want", "neg", "req"])
    sub = random.choice(subjects)
    act = random.choice(actions)
    if grammar == "want":
        kr = f"{sub['kr']} {act['want'].replace('해 해요', '해요') if sub['cn'] == '我' else act['want']}"
        cn = f"{sub['cn']}想{act['cn']}。"
    elif grammar == "req":
        kr = act['req']; cn = f"請{act['cn']}。"
    else:
        kr = f"{sub['kr']} {act[grammar]}"; cn = f"{sub['cn']}{'昨天' if grammar=='past' else '不' if grammar=='neg' else ''}{act['cn']}。"
    return {"cn": cn, "kr": kr}

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: st.error("語音失敗")

# --- 3. 介面 ---
st.markdown('<p class="main-title">💙 韓語測驗分析系統 💙</p>', unsafe_allow_html=True)

# 顯示分析報告
if not st.session_state.is_testing:
    acc = (st.session_state.correct / st.session_state.total * 100) if st.session_state.total > 0 else 0
    st.markdown(f"""
    <div class="report-box">
        <h3 style='color: #007FFF; text-align: center;'>📋 當日學習分析報告</h3>
        <p>總測驗題數：{st.session_state.total} 題</p>
        <p>答對題數：{st.session_state.correct} 題</p>
        <p>當前準確率：{acc:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    if acc >= 80: st.success("🌟 表現優異！妳的韓文感度就像製程良率一樣穩定！")
    elif acc >= 60: st.warning("📈 還不錯，但有些文法變化的『誤差』需要調整喔。")
    else: st.error("🔧 需要維護！建議重新翻閱《大家的韓國語》第一冊重點。")
    
    if st.button("🔄 開始新測驗 (重置數據)"):
        st.session_state.total = 0
        st.session_state.correct = 0
        st.session_state.is_testing = True
        st.rerun()

# 測驗介面
if st.session_state.is_testing:
    if 'dq' not in st.session_state: st.session_state.dq = generate_quiz()
    if 'in_id' not in st.session_state: st.session_state.in_id = 0
    
    dq = st.session_state.dq
    st.info(f"💡 **請翻譯：** 「 {dq['cn']} 」")
    u_in = st.text_input("輸入韓文：", key=f"in_{st.session_state.in_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("驗證答案"):
            if u_in:
                correct = clean_text(u_in) == clean_text(dq['kr'])
                update_stats(correct)
                if correct: st.balloons(); st.success("正確！")
                else: st.error(f"正確答案：{dq['kr']}")
                play_audio(dq['kr'])
    with col2:
        if st.button("換下一題"):
            st.session_state.dq = generate_quiz()
            st.session_state.in_id += 1
            st.rerun()
    
    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束測驗並產出報告"):
        st.session_state.is_testing = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
