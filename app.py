import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .report-box { background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 2px solid #007FFF; margin: 20px 0; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; border-radius: 12px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化統計與狀態 ---
if 'total' not in st.session_state: st.session_state.total = 0
if 'correct' not in st.session_state: st.session_state.correct = 0
if 'is_testing' not in st.session_state: st.session_state.is_testing = True

def update_stats(is_ok):
    st.session_state.total += 1
    if is_ok: st.session_state.correct += 1

# --- 2. 隨機拼湊引擎 ---
def generate_quiz():
    subjects = [{"cn": "我", "kr": "저는"}, {"cn": "老師", "kr": "선생님은"}, {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"}]
    actions = [
        {"cn": "吃麵包", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "want": "빵을 먹고 싶어 해요", "neg": "빵을 먹지 않아요", "req": "빵을 먹어 주세요", "can": "빵을 먹을 수 있어요"},
        {"cn": "喝咖啡", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "want": "커피를 마시고 싶어 해요", "neg": "커피를 마시지 않아요", "req": "커피를 마셔 주세요", "can": "커피를 마실 수 있어요"},
        {"cn": "學習韓文", "pol": "한국어를 공부해요", "past": "한국어를 공부했어요", "want": "한국어를 공부하고 싶어 해요", "neg": "한국어를 공부하지 않아요", "req": "한국어를 공부해 주세요", "can": "한국어를 공부할 수 있어요"},
        {"cn": "買衣服", "pol": "옷을 사요", "past": "옷을 샀어요", "want": "옷을 사고 싶어 해요", "neg": "옷을 사지 않아요", "req": "옷을 사 주세요", "can": "옷을 살 수 있어요"}
    ]
    grammar = random.choice(["pol", "past", "want", "neg", "req", "can"])
    sub = random.choice(subjects)
    act = random.choice(actions)
    
    if grammar == "want":
        kr = f"{sub['kr']} {act['want'].replace('해 해요', '해요') if sub['cn'] == '我' else act['want']}"
        cn = f"{sub['cn']}想{act['cn']}。"
    elif grammar == "req":
        kr = act['req']; cn = f"請{act['cn']}。"
    elif grammar == "can":
        kr = f"{sub['kr']} {act['can']}"; cn = f"{sub['cn']}會{act['cn']}。"
    else:
        kr = f"{sub['kr']} {act[grammar]}"; cn = f"{sub['cn']}{'昨天' if grammar=='past' else '不' if grammar=='neg' else ''}{act['cn']}。"
    return {"cn": cn, "kr": kr}

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: st.error("發音失敗")

# --- 3. 讀取 Excel ---
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
st.markdown('<p class="main-title">💙 韓語測驗與複習系統 💙</p>', unsafe_allow_html=True)

# 顯示報告區
if not st.session_state.is_testing:
    acc = (st.session_state.correct / st.session_state.total * 100) if st.session_state.total > 0 else 0
    st.markdown(f"""
    <div class="report-box">
        <h3 style='color: #007FFF; text-align: center;'>📋 當日學習分析報告</h3>
        <p style='font-size: 18px; text-align: center;'>總練習數：{st.session_state.total} | 答對：{st.session_state.correct} | 準確率：{acc:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    if acc >= 80: st.success("🌟 準確率達標！妳的韓文製程非常穩定！")
    elif acc >= 50: st.warning("📈 有進步空間，加油！")
    else: st.error("🔧 需要停機維護，回去翻一下課本喔！")
    
    if st.button("🔄 重置數據並開始新測驗"):
        st.session_state.total = 0; st.session_state.correct = 0; st.session_state.is_testing = True
        st.rerun()

# 4. 隨機文法挑戰區
if st.session_state.is_testing:
    st.subheader("✍️ 文法拼湊大挑戰")
    if 'dq' not in st.session_state: st.session_state.dq = generate_quiz()
    if 'in_id' not in st.session_state: st.session_state.in_id = 0
    
    dq = st.session_state.dq
    st.info(f"💡 **翻譯題目：** 「 {dq['cn']} 」")
    u_in = st.text_input("輸入韓文：", key=f"in_{st.session_state.in_id}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("驗證答案"):
            if u_in:
                is_ok = clean_text(u_in) == clean_text(dq['kr'])
                update_stats(is_ok)
                if is_ok: st.balloons(); st.success("正確！")
                else: st.error(f"正確答案：{dq['kr']}")
                play_audio(dq['kr'])
    with c2:
        if st.button("換下一題"):
            st.session_state.dq = generate_quiz(); st.session_state.in_id += 1; st.rerun()
    
    if st.button("⏹️ 結束測驗並產出報告"):
        st.session_state.is_testing = False; st.rerun()

st.divider()

# 5. 我的單字複習頁面 (原本消失的部分回來了！)
st.subheader("🎯 我的 Excel 題庫複習")
df = load_data()
if not df.empty:
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
                st.write(f"📍 章節：{item['chapter']} | 題目：{item['cn']}")
                u_in_ex = st.text_input("在此輸入回答", key=f"ex_{target_cat}_{st.session_state[tab_id_key]}")
                
                c3, c4 = st.columns(2)
                with c3:
                    if st.button("檢查內容", key=f"btn_ex_{target_cat}"):
                        is_ok = clean_text(u_in_ex) == clean_text(str(item['kr']))
                        update_stats(is_ok) # Excel 複習也計入統計
                        if is_ok: st.balloons(); st.success("正確！")
                        else: st.error(f"正確答案：{item['kr']}")
                        play_audio(item['kr'])
                with c4:
                    if st.button("下一題", key=f"next_ex_{target_cat}"):
                        if q_key in st.session_state: del st.session_state[q_key]
                        st.session_state[tab_id_key] += 1; st.rerun()
else:
    st.warning("Excel 還沒有資料喔！")

st.markdown(f"**[🔗 打開 Excel 試算表]({load_data.__wrapped__.__code__.co_consts[1]})**")
