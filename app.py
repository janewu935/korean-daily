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
    .wrong-list { color: #FF4B4B; background-color: #FFF0F0; padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #FF4B4B; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'last_sel_ch' not in st.session_state: st.session_state.last_sel_ch = []

# --- 2. 輔助功能 ---
def get_cheer_message():
    messages = ["宜真，今天的妳也比昨天更進步了！加油！💙", "Process Engineer 的韓文實力正在穩定提升中！", "24/7 With Us! 練習累了就聽聽 TWS 的歌吧 🎶", "每一題的練習都是為了 10 月的 TOPIK 考照鋪路！", "像研究 TGV 結構一樣精準地掌握韓文吧！", "今天也要保持應援藍的好心情喔！💎"]
    random.seed(date.today().toordinal())
    return random.choice(messages)

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
        {"cn": "學習韓語", "pol": "한국어를 공부해요", "past": "한국어를 공부했어요", "want": "한국어를 공부하고 싶어 해요", "neg": "한국어를 공부하지 않아요", "req": "한국어를 공부해 주세요", "can": "한국어를 공부할 수 있어요"}
    ]
    grammar = random.choice(["pol", "past", "want", "neg", "req", "can"])
    sub = random.choice(subjects); act = random.choice(actions)
    if grammar == "want":
        kr = f"{sub['kr']} {act['want'].replace('해 해요', '해요') if sub['cn'] == '我' else act['want']}"
        cn = f"{sub['cn']}想{act['cn']}。"
    elif grammar == "req": kr = act['req']; cn = f"請{act['cn']}。"
    elif grammar == "can": kr = f"{sub['kr']} {act['can']}"; cn = f"{sub['cn']}會{act['cn']}。"
    else: kr = f"{sub['kr']} {act[grammar]}"; cn = f"{sub['cn']}{'昨天' if grammar=='past' else '不' if grammar=='neg' else ''}{act['cn']}。"
    return {"cn": cn, "kr": kr}

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""<div class="report-box"><h3 style='text-align: center; color: #007FFF;'>📊 Excel 複習結算</h3><p style='text-align: center; font-size: 20px;'>準確率：{acc:.1f}% ({st.session_state.ex_correct}/{st.session_state.ex_total})</p></div>""", unsafe_allow_html=True)
    if st.session_state.wrong_items:
        st.subheader("❌ 寫錯的內容回顧：")
        for w in st.session_state.wrong_items:
            st.markdown(f"""<div class="wrong-list">📍 [{w['type']}] {w['cn']} → <b>{w['kr']}</b> ({w['chapter']})</div>""", unsafe_allow_html=True)
        if st.button("🔥 針對錯題重新複習"):
            for cat in st.session_state.pools:
                st.session_state.pools[cat] = [x for x in st.session_state.wrong_items if x['type'] == cat]
            st.session_state.wrong_items = []; st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.show_report = False; st.rerun()
    if st.button("🔄 開啟全新一輪 (清空池子)"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.wrong_items = []; st.session_state.pools = {"單字": [], "文法": [], "發音": []}; st.session_state.show_report = False; st.rerun()
    st.stop()

# --- 4. 每日翻譯挑戰 ---
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state: st.session_state.dq = generate_daily_quiz()
if 'dq_id' not in st.session_state: st.session_state.dq_id = 0
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入翻譯：", key=f"dq_in_{st.session_state.dq_id}")
c_dq1, c_dq2 = st.columns(2)
with c_dq1:
    if st.button("驗證翻譯"):
        if u_in_dq:
            is_ok = clean_text(u_in_dq) == clean_text(dq['kr'])
            if is_ok: st.balloons(); st.success(f"⭕ 正確：{dq['kr']}")
            else: st.error(f"❌ 錯誤！正確答案：{dq['kr']}"); play_audio(dq['kr'])
with c_dq2:
    if st.button("換下一題"):
        st.session_state.dq = generate_daily_quiz(); st.session_state.dq_id += 1; st.rerun()

st.divider()

# --- 5. Excel 複習區 ---
st.subheader("🎯 Excel 題庫分類複習")
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    
    # --- 💡 關鍵：預設全選所有章節 ---
    sel_ch = st.multiselect("篩選章節：", all_ch, default=all_ch, key="chapter_sel")
    
    # 檢查篩選章節是否有變動，若變動則清空池子重新初始化
    if sel_ch != st.session_state.last_sel_ch:
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
        st.session_state.last_sel_ch = sel_ch

    study_mode = st.radio("模式：", ["📖 閃卡 (複習)", "✍️ 考試 (練習)"], horizontal=True)
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cat_list = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cat_list[i]
            
            # 初始化該單元、該分類的專屬池子
            if not st.session_state.pools[target_cat]:
                curr_df = df[df['type'] == target_cat]
                if sel_ch:
                    curr_df = curr_df[curr_df['chapter'].astype(str).isin(sel_ch)]
                if not curr_df.empty:
                    st.session_state.pools[target_cat] = curr_df.to_dict('records')
                    random.shuffle(st.session_state.pools[target_cat])

            current_pool = st.session_state.pools[target_cat]
            if current_pool:
                st.write(f"📝 目前選取單元剩餘：{len(current_pool)} 題")
                item = current_pool[0]
                st.markdown(f"""<div class="flashcard"><h3>{item['cn']}</h3><small>單元：{item['chapter']}</small></div>""", unsafe_allow_html=True)
                
                if "閃卡" in study_mode:
                    if st.button("👁️ 顯示答案", key=f"show_{target_cat}"):
                        st.info(f"🇰🇷：**{item['kr']}**"); play_audio(item['kr'])
                else:
                    u_in_ex = st.text_input("輸入韓文回答", key=f"in_{target_cat}_{len(current_pool)}")
                    if st.button("提交驗證", key=f"btn_{target_cat}"):
                        is_ok = clean_text(u_in_ex) == clean_text(str(item['kr']))
                        st.session_state.ex_total += 1
                        if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                        else:
                            st.error(f"❌ 錯誤！答案：{item['kr']}")
                            if item not in st.session_state.wrong_items: st.session_state.wrong_items.append(item)
                        play_audio(item['kr'])

                if st.button("下一題 ➡️", key=f"next_{target_cat}"):
                    st.session_state.pools[target_cat].pop(0)
                    st.rerun()
            else:
                st.write(f"✅ 該分類在所選單元中已複習完畢。")

    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束測驗並產出總報告"):
        st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown(f"""<div class="cheer-box">{get_cheer_message()}</div>""", unsafe_allow_html=True)
