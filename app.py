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
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化所有狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]

# --- 2. 核心功能函數 ---
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

def generate_daily_quiz():
    subjects = [{"cn": "我", "kr": "저는"}, {"cn": "老師", "kr": "선생님은"}, {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"}]
    actions = [
        {"cn": "吃麵包", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "want": "빵을 먹고 싶어 해요", "neg": "빵을 먹지 않아요", "req": "빵을 먹어 주세요", "can": "빵을 먹을 수 있어요"},
        {"cn": "喝咖啡", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "want": "커피를 마시고 싶어 해요", "neg": "커피를 마시지 않아요", "req": "커피를 마셔 주세요", "can": "커피를 마실 수 있어요"},
        {"cn": "學習韓語", "pol": "한국어를 공부해요", "past": "한국어를 공부했어요", "want": "한국어를 공부하고 싶어 해요", "neg": "한국어를 공부하지 않아요", "req": "한국어를 공부해 주세요"}
    ]
    grammar = random.choice(["pol", "past", "want", "neg", "req"])
    sub = random.choice(subjects); act = random.choice(actions)
    if grammar == "want":
        kr = f"{sub['kr']} {act['want'].replace('해 해요', '해요') if sub['cn'] == '我' else act['want']}"
        cn = f"{sub['cn']}想{act['cn']}。"
    elif grammar == "req": kr = act['req']; cn = f"請{act['cn']}。"
    else: kr = f"{sub['kr']} {act[grammar]}"; cn = f"{sub['cn']}{'昨天' if grammar=='past' else '不' if grammar=='neg' else ''}{act['cn']}。"
    return {"cn": cn, "kr": kr}

# --- 3. 主介面顯示 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 結算報告
if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""<div class="report-box"><h3 style='text-align: center; color: #007FFF;'>📊 Excel 複習結算</h3><p style='text-align: center; font-size: 20px;'>準確率：{acc:.1f}% ({st.session_state.ex_correct}/{st.session_state.ex_total})</p></div>""", unsafe_allow_html=True)
    if st.session_state.wrong_items:
        st.subheader("❌ 錯誤內容：")
        for w in st.session_state.wrong_items:
            st.write(f"📍 {w['cn']} → {w['kr']}")
    if st.button("🔄 開啟新測驗"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.wrong_items = []; st.session_state.pools = {"單字": [], "文法": [], "發音": []}; st.session_state.show_report = False; st.rerun()
    st.stop()

# --- 💡 每日一句翻譯考試 (絕對存在版) ---
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state: st.session_state.dq = generate_daily_quiz()
if 'dq_id' not in st.session_state: st.session_state.dq_id = 0
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入韓文：", key=f"dq_in_{st.session_state.dq_id}")

c_dq1, c_dq2 = st.columns(2)
with c_dq1:
    if st.button("驗證翻譯"):
        if u_in_dq:
            if clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
            else: st.error(f"❌ 正確答案：{dq['kr']}"); play_audio(dq['kr'])
with c_dq2:
    if st.button("換下一題翻譯"):
        st.session_state.dq = generate_daily_quiz(); st.session_state.dq_id += 1; st.rerun()

st.divider()

# --- 5. Excel 複習區 ---
st.subheader("🎯 Excel 題庫複習")
df = load_data()
if not df.empty:
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_chapters
    
    # 💡 互斥選單邏輯：選單元就踢掉 ALL，選 ALL 就踢掉單元
    def sync_selection():
        new_val = st.session_state.temp_sel
        if "ALL 全部單元" in st.session_state.sel_ch and len(new_val) > 1:
            st.session_state.sel_ch = [v for v in new_val if v != "ALL 全部單元"]
        elif "ALL 全部單元" in new_val and "ALL 全部單元" not in st.session_state.sel_ch:
            st.session_state.sel_ch = ["ALL 全部單元"]
        else:
            st.session_state.sel_ch = new_val
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}

    st.multiselect("範圍篩選：", options, key="temp_sel", on_change=sync_selection, default=st.session_state.sel_ch)
    
    final_ch = all_chapters if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch
    study_mode = st.radio("模式：", ["📖 閃卡", "✍️ 考試"], horizontal=True)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cat_list = ["單字", "文法", "發音"]
    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cat_list[i]
            if not st.session_state.pools[target_cat]:
                curr_df = df[(df['type'] == target_cat) & (df['chapter'].astype(str).isin(final_ch))]
                if not curr_df.empty:
                    st.session_state.pools[target_cat] = curr_df.to_dict('records')
                    random.shuffle(st.session_state.pools[target_cat])
            
            p = st.session_state.pools[target_cat]
            if p:
                st.write(f"📝 剩餘：{len(p)} 題")
                item = p[0]
                st.markdown(f"""<div class="flashcard"><h3>{item['cn']}</h3><small>{item['chapter']}</small></div>""", unsafe_allow_html=True)
                if "閃卡" in study_mode:
                    if st.button("👁️ 解答", key=f"s_{target_cat}"): st.info(f"🇰🇷：{item['kr']}"); play_audio(item['kr'])
                else:
                    u_in = st.text_input("輸入答案", key=f"ex_{target_cat}_{len(p)}")
                    if st.button("提交", key=f"b_{target_cat}"):
                        is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                        st.session_state.ex_total += 1
                        if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                        else: st.error(f"❌ 答案：{item['kr']}"); st.session_state.wrong_items.append(item)
                        play_audio(item['kr'])
                if st.button("下一題 ➡️", key=f"n_{target_cat}"): p.pop(0); st.rerun()
            else: st.write("✅ 該類別已完成")

    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束複習並看報告"): st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.info("宜真加油！💙 每天進步一點點，10 月 TOPIK 必過！")
