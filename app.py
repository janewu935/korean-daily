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
    .report-box { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 2px solid #007FFF; margin: 20px 0; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; border-radius: 12px; }
    .flashcard { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 1px solid #E6F3FF; text-align: center; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .cheer-box { background-color: #E6F3FF; padding: 15px; border-radius: 10px; border-left: 5px solid #007FFF; color: #007FFF; font-weight: bold; text-align: center; margin-top: 30px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化與每日應援語 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False

def get_cheer_message():
    messages = [
        "宜真，今天的妳也比昨天更進步了！加油！💙",
        "Process Engineer 的韓文實力正在穩定提升中！",
        "24/7 With Us! 練習累了就聽聽 TWS 的歌吧 🎶",
        "每一題的練習都是為了 10 月的 TOPIK 考照鋪路！",
        "像研究 TGV 結構一樣精準地掌握韓文吧！妳做得到的！",
        "別忘了妳的初衷：『希望能看懂劇本練習韓文』，Fighting!",
        "今天也要保持應援藍的好心情喔！💎"
    ]
    # 使用日期作為種子，每天換一句
    random.seed(date.today().toordinal())
    return random.choice(messages)

def update_ex_stats(is_ok):
    st.session_state.ex_total += 1
    if is_ok: st.session_state.ex_correct += 1

# --- 2. 隨機拼湊引擎 ---
def generate_ultimate_quiz():
    subjects = [{"cn": "我", "kr": "저는"}, {"cn": "老師", "kr": "선생님은"}, {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"}]
    actions = [
        {"cn": "吃麵包", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "want": "빵을 먹고 싶어 해요", "neg": "빵을 먹지 않아요", "req": "빵을 먹어 주세요", "can": "빵을 먹을 수 있어요"},
        {"cn": "喝咖啡", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "want": "커피를 마시고 싶어 해요", "neg": "커피를 마시지 않아요", "req": "커피를 마셔 주세요", "can": "커피를 마실 수 있어요"},
        {"cn": "學習韓語", "pol": "한국어를 공부해요", "past": "한국어를 공부했어요", "want": "한국어를 공부하고 싶어 해요", "neg": "한국어를 공부하지 않아요", "req": "한국어를 공부해 주세요", "can": "한국어를 공부할 수 있어요"}
    ]
    grammar = random.choice(["pol", "past", "want", "neg", "req", "can"])
    sub = random.choice(subjects)
    act = random.choice(actions)
    if grammar == "want":
        kr = f"{sub['kr']} {act['want'].replace('해 해요', '해요') if sub['cn'] == '我' else act['want']}"
        cn = f"{sub['cn']}想{act['cn']}。"
    elif grammar == "req": kr = act['req']; cn = f"請{act['cn']}。"
    elif grammar == "can": kr = f"{sub['kr']} {act['can']}"; cn = f"{sub['cn']}會{act['cn']}。"
    else: kr = f"{sub['kr']} {act[grammar]}"; cn = f"{sub['cn']}{'昨天' if grammar=='past' else '不' if grammar=='neg' else ''}{act['cn']}。"
    return {"cn": cn, "kr": kr}

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).replace(" ", "").strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: st.error("語音失敗")

@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df.dropna(subset=['kr', 'cn'])
    except: return pd.DataFrame()

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 顯示報告
if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""<div class="report-box"><h3 style='text-align: center;'>📊 Excel 複習良率報告</h3><p style='text-align: center; font-size: 20px;'>準確率：{acc:.1f}%</p></div>""", unsafe_allow_html=True)
    if st.button("🔄 關閉報告並重置"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.show_report = False; st.rerun()

st.divider()

# 每日挑戰
st.subheader("✍️ 每日文法挑戰")
if 'dq' not in st.session_state: st.session_state.dq = generate_ultimate_quiz()
if 'dq_id' not in st.session_state: st.session_state.dq_id = 0
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入韓文：", key=f"dq_{st.session_state.dq_id}")
col_dq1, col_dq2 = st.columns(2)
with col_dq1:
    if st.button("驗證答案"):
        if u_in_dq:
            is_ok = clean_text(u_in_dq) == clean_text(dq['kr'])
            if is_ok: st.balloons(); st.success(f"⭕ 正確：{dq['kr']}")
            else: st.error(f"❌ 錯誤！正確答案：`{dq['kr']}`"); play_audio(dq['kr'])
with col_dq2:
    if st.button("換下一題"):
        st.session_state.dq = generate_ultimate_quiz(); st.session_state.dq_id += 1; st.rerun()

st.divider()

# Excel 複習與閃卡
st.subheader("🎯 Excel 題庫與閃卡")
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("章節篩選：", all_ch)
    study_mode = st.radio("學習模式：", ["📖 複習 (閃卡)", "✍️ 考試 (打字)"], horizontal=True)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cats = ["單字", "文法", "發音"]
    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cats[i]
            tmp = df[df['type'] == target_cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            if not tmp.empty:
                t_id = f"tid_{target_cat}"
                if t_id not in st.session_state: st.session_state[t_id] = 0
                q_key = f"ex_item_{target_cat}"
                if q_key not in st.session_state: st.session_state[q_key] = tmp.sample(1).iloc[0]
                item = st.session_state[q_key]
                st.markdown(f"""<div class="flashcard"><h3>{item['cn']}</h3></div>""", unsafe_allow_html=True)
                
                if "複習" in study_mode:
                    if st.button("👁️ 顯示答案", key=f"show_{target_cat}"):
                        st.info(f"🇰🇷：**{item['kr']}**"); play_audio(item['kr'])
                else:
                    u_in_ex = st.text_input("在此輸入韓文", key=f"exin_{target_cat}_{st.session_state[t_id]}")
                    if st.button("驗證內容", key=f"exbtn_{target_cat}"):
                        is_ok = clean_text(u_in_ex) == clean_text(str(item['kr']))
                        update_ex_stats(is_ok)
                        if is_ok: st.balloons(); st.success(f"⭕ 正確！")
                        else: st.error(f"❌ 錯誤！正確答案：`{item['kr']}`"); play_audio(item['kr'])
                
                if st.button("下一個", key=f"exnxt_{target_cat}"):
                    if q_key in st.session_state: del st.session_state[q_key]
                    st.session_state[t_id] += 1; st.rerun()
    
    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束複習並產出報告"):
        st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 💙 每日應援回歸！ ---
st.markdown(f"""<div class="cheer-box">{get_cheer_message()}</div>""", unsafe_allow_html=True)
