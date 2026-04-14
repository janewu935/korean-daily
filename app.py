import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re
from datetime import date

st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .report-box { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 2px solid #007FFF; margin: 20px 0; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; border-radius: 12px; }
    .flashcard { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 1px solid #E6F3FF; text-align: center; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .cheer-box { background-color: #E6F3FF; padding: 15px; border-radius: 10px; border-left: 5px solid #007FFF; color: #007FFF; font-weight: bold; text-align: center; margin-top: 30px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    .wrong-list { color: #FF4B4B; background-color: #FFF0F0; padding: 10px; border-radius: 8px; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化狀態與數據 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = [] # 儲存錯題清單
if 'pool' not in st.session_state: st.session_state.pool = [] # 當前複習池

def get_cheer_message():
    messages = ["宜真，今天的妳也比昨天更進步了！加油！💙", "Process Engineer 的韓文實力正在穩定提升中！", "24/7 With Us! 練習累了就聽聽 TWS 的歌吧 🎶", "每一題的練習都是為了 10 月的 TOPIK 考照鋪路！", "像研究 TGV 結構一樣精準地掌握韓文吧！", "今天也要保持應援藍的好心情喔！💎"]
    random.seed(date.today().toordinal())
    return random.choice(messages)

@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df.dropna(subset=['kr', 'cn'])
    except: return pd.DataFrame()

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).replace(" ", "").strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: st.error("語音失敗")

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 顯示報告與錯題回顧
if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""
    <div class="report-box">
        <h3 style='text-align: center; color: #007FFF;'>📊 複習結算報告</h3>
        <p style='text-align: center; font-size: 20px;'>準確率：{acc:.1f}% ({st.session_state.ex_correct}/{st.session_state.ex_total})</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.wrong_items:
        st.subheader("❌ 這次寫錯的單字：")
        for w in st.session_state.wrong_items:
            st.markdown(f"""<div class="wrong-list">📍 {w['cn']} → <b>{w['kr']}</b> ({w['chapter']})</div>""", unsafe_allow_html=True)
        
        if st.button("🔥 針對這些錯題重新複習"):
            st.session_state.pool = st.session_state.wrong_items.copy()
            st.session_state.wrong_items = []
            st.session_state.ex_total = 0; st.session_state.ex_correct = 0
            st.session_state.show_report = False
            st.rerun()
    else:
        st.success("🎉 太完美了！沒有任何錯題！")

    if st.button("🔄 開啟全新一輪複習"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.wrong_items = []
        st.session_state.pool = []; st.session_state.show_report = False; st.rerun()
    st.stop()

# --- Excel 複習區 ---
st.subheader("🎯 Excel 題庫複習 (不重複模式)")
df = load_data()
if not df.empty:
    col_sel, col_mode = st.columns([2, 1])
    with col_sel:
        all_ch = sorted(df['chapter'].astype(str).unique().tolist())
        sel_ch = st.multiselect("篩選章節：", all_ch)
    with col_mode:
        study_mode = st.radio("模式：", ["📖 閃卡", "✍️ 考試"], horizontal=True)

    # 初始化複習池
    if not st.session_state.pool:
        current_df = df.copy()
        if sel_ch: current_df = current_df[current_df['chapter'].astype(str).isin(sel_ch)]
        if not current_df.empty:
            st.session_state.pool = current_df.to_dict('records')
            random.shuffle(st.session_state.pool) # 隨機打亂順序

    if st.session_state.pool:
        # 顯示進度
        total_in_pool = len(st.session_state.pool)
        st.write(f"📝 剩餘題數：{total_in_pool}")
        
        item = st.session_state.pool[0] # 取出目前池子裡的第一題
        st.markdown(f"""<div class="flashcard"><h3>{item['cn']}</h3><p>{item['type']} | {item['chapter']}</p></div>""", unsafe_allow_html=True)
        
        if "閃卡" in study_mode:
            if st.button("👁️ 顯示答案", key="show_ans"):
                st.info(f"🇰🇷：**{item['kr']}**"); play_audio(item['kr'])
        else:
            u_in = st.text_input("輸入韓文回答", key=f"ex_{total_in_pool}")
            if st.button("提交並驗證"):
                is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                st.session_state.ex_total += 1
                if is_ok:
                    st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                else:
                    st.error(f"❌ 錯誤！正確答案：{item['kr']}")
                    if item not in st.session_state.wrong_items:
                        st.session_state.wrong_items.append(item)
                play_audio(item['kr'])

        if st.button("下一題 ➡️"):
            st.session_state.pool.pop(0) # 移除已經練習過的題目
            if not st.session_state.pool:
                st.session_state.show_report = True
            st.rerun()
    else:
        st.info("請選擇章節開始複習！")

    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 提早結束並看報告"):
        st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown(f"""<div class="cheer-box">{get_cheer_message()}</div>""", unsafe_allow_html=True)
