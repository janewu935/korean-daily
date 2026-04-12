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
    .report-box { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 2px solid #007FFF; margin: 20px 0; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; border-radius: 12px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    h3 { color: #007FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化統計與狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False

def update_ex_stats(is_ok):
    st.session_state.ex_total += 1
    if is_ok: st.session_state.ex_correct += 1

# --- 2. 隨機文法拼湊引擎 (L1-L12) ---
def generate_ultimate_quiz():
    subjects = [{"cn": "我", "kr": "저는"}, {"cn": "老師", "kr": "선생님은"}, {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"}]
    actions = [
        {"cn": "吃麵包", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "want": "빵을 먹고 싶어 해요", "neg": "빵을 먹지 않아요", "req": "빵을 먹어 주세요", "can": "빵을 먹을 수 있어요"},
        {"cn": "喝咖啡", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "want": "커피를 마시고 싶어 해요", "neg": "커피를 마시지 않아요", "req": "커피를 마셔 주세요", "can": "커피를 마실 수 있어요"},
        {"cn": "看電影", "pol": "영화를 봐요", "past": "영화를 봤어요", "want": "영화를 보고 싶어 해요", "neg": "영화를 보지 않아요", "req": "영화를 봐 주세요", "can": "영화를 볼 수 있어요"},
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

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).strip()

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

# 3. 分析報告顯示 (針對 Excel 題庫)
if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""
    <div class="report-box">
        <h3 style='color: #007FFF; text-align: center;'>📊 Excel 複習良率報告</h3>
        <p style='text-align: center; font-size: 18px;'>今日 Excel 複習量：{st.session_state.ex_total} | 答對：{st.session_state.ex_correct}</p>
        <p style='text-align: center; font-size: 22px; color: #007FFF;'><b>準確率：{acc:.1f}%</b></p>
    </div>
    """, unsafe_allow_html=True)
    if acc >= 80: st.success("🌟 製程極其穩定！妳的單字量沒問題。")
    elif acc >= 50: st.warning("📈 還不錯，但有些單字拼寫需要校正。")
    else: st.error("🚨 良率過低，建議重新複習基礎單字。")
    if st.button("🔄 關閉報告並重置數據"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.show_report = False; st.rerun()

st.divider()

# 4. 每日一句翻譯 (隨機拼湊引擎)
st.subheader("✍️ 每日文法拼湊挑戰")
if 'dq' not in st.session_state: st.session_state.dq = generate_ultimate_quiz()
if 'dq_id' not in st.session_state: st.session_state.dq_id = 0

dq = st.session_state.dq
st.info(f"💡 **請翻譯：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入挑戰答案：", key=f"dq_{st.session_state.dq_id}")

col_dq1, col_dq2 = st.columns(2)
with col_dq1:
    if st.button("驗證挑戰答案"):
        if u_in_dq:
            is_ok = clean_text(u_in_dq) == clean_text(dq['kr'])
            if is_ok: st.balloons(); st.success("正確！")
            else: st.error(f"正確答案：{dq['kr']}")
            play_audio(dq['kr'])
with col_dq2:
    if st.button("換下一題挑戰"):
        st.session_state.dq = generate_ultimate_quiz(); st.session_state.dq_id += 1; st.rerun()

st.divider()

# 5. Excel 題庫複習與分析
st.subheader("🎯 Excel 題庫複習區")
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇章節：", all_ch)
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
                st.write(f"📍 來源：{item['chapter']} | 題目：{item['cn']}")
                u_in_ex = st.text_input("輸入 Excel 回答", key=f"exin_{target_cat}_{st.session_state[t_id]}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("檢查內容", key=f"exbtn_{target_cat}"):
                        is_ok = clean_text(u_in_ex) == clean_text(str(item['kr']))
                        update_ex_stats(is_ok) # 僅 Excel 計入統計報告
                        if is_ok: st.balloons(); st.success("正確！")
                        else: st.error(f"正確答案：{item['kr']}")
                        play_audio(item['kr'])
                with c2:
                    if st.button("下一個內容", key=f"exnxt_{target_cat}"):
                        if q_key in st.session_state: del st.session_state[q_key]
                        st.session_state[t_id] += 1; st.rerun()
            else: st.write("無資料")
    
    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束 Excel 複習並產出報告"):
        st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Excel 還沒準備好喔！")
