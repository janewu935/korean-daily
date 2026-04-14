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
    .flashcard { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 1px solid #E6F3FF; text-align: center; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .cheer-box { background-color: #E6F3FF; padding: 15px; border-radius: 10px; border-left: 5px solid #007FFF; color: #007FFF; font-weight: bold; text-align: center; margin-top: 30px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 核心邏輯與數據 ---
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
    except: pass

def get_cheer():
    messages = ["宜真加油！💙 10 月 TOPIK 必過！", "Process Engineer 的良率保證！", "24/7 With Us! 🎶"]
    random.seed(date.today().toordinal())
    return random.choice(messages)

# --- 2. 初始化狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'prev_filter' not in st.session_state: st.session_state.prev_filter = ""

# --- 3. 每日一句翻譯考試 (絕對置頂) ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)
st.subheader("✍️ 每日一句翻譯考試")

# 這裡放入妳之前的自動拼湊引擎邏輯（簡化版示意）
if 'dq' not in st.session_state:
    st.session_state.dq = {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}

dq = st.session_state.dq
st.info(f"💡 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入韓文答案：", key="dq_field")

c_dq1, c_dq2 = st.columns(2)
with c_dq1:
    if st.button("驗證翻譯"):
        if u_in_dq:
            if clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
            else: st.error(f"❌ 正確答案：{dq['kr']}"); play_audio(dq['kr'])
with c_dq2:
    if st.button("換下一題翻譯"):
        st.session_state.dq = {"cn": "姐姐在睡覺。", "kr": "언니는 자고 있어요"} # 應換成妳的拼湊函數
        st.rerun()

st.divider()

# --- 4. Excel 複習區 (新互斥設計) ---
st.subheader("🎯 Excel 題庫複習")
df = load_data()

if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    
    # 💡 關鍵改動：用 Checkbox 來做 ALL
    is_all = st.checkbox("全部單元一起複習 (ALL)", value=True)
    
    if is_all:
        selected_ch = all_ch
        st.write("✅ 目前已選取：**全部單元**")
    else:
        selected_ch = st.multiselect("選擇特定單元：", all_ch)
    
    # 偵測篩選條件是否有變，有變就重置池子
    current_filter = "ALL" if is_all else str(selected_ch)
    if current_filter != st.session_state.prev_filter:
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
        st.session_state.prev_filter = current_filter

    study_mode = st.radio("模式：", ["📖 閃卡", "✍️ 考試"], horizontal=True)
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cat_list = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cat_list[i]
            if not st.session_state.pools[target_cat]:
                curr_df = df[(df['type'] == target_cat) & (df['chapter'].astype(str).isin(selected_ch))]
                if not curr_df.empty:
                    st.session_state.pools[target_cat] = curr_df.to_dict('records')
                    random.shuffle(st.session_state.pools[target_cat])
            
            p = st.session_state.pools[target_cat]
            if p:
                st.write(f"📝 剩餘：{len(p)} 題")
                item = p[0]
                st.markdown(f"""<div class="flashcard"><h3>{item['cn']}</h3><small>{item['chapter']}</small></div>""", unsafe_allow_html=True)
                if "閃卡" in study_mode:
                    if st.button("👁️ 顯示解答", key=f"s_{target_cat}"): st.info(f"🇰🇷：{item['kr']}"); play_audio(item['kr'])
                else:
                    u_in = st.text_input("回答答案", key=f"ex_{target_cat}_{len(p)}")
                    if st.button("提交", key=f"b_{target_cat}"):
                        is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                        st.session_state.ex_total += 1
                        if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                        else: st.error(f"❌ 答案：{item['kr']}"); st.session_state.wrong_items.append(item)
                        play_audio(item['kr'])
                if st.button("下一題 ➡️", key=f"n_{target_cat}"): p.pop(0); st.rerun()
            else: st.write("✅ 已完成")

# 報告區 (省略)
if st.session_state.show_report:
    # 這裡放妳之前的報告代碼...
    if st.button("🔄 重新開始"): st.session_state.show_report=False; st.rerun()
    st.stop()

if st.button("⏹️ 結束並看報告"): st.session_state.show_report = True; st.rerun()

st.divider()
st.markdown(f"""<div class="cheer-box">{get_cheer()}</div>""", unsafe_allow_html=True)
