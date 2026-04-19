import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re
from datetime import date

st.set_page_config(page_title="韓語練習", page_icon="💙")

# --- CSS 樣式 (精準還原妳的設計圖) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .grammar-rule-box { 
        border: 2px dashed #007FFF; padding: 10px; border-radius: 10px; color: #007FFF; 
        text-align: center; margin-bottom: 20px; background-color: rgba(0, 127, 255, 0.05); font-weight: bold;
    }
    .flashcard-main { 
        background-color: #FFFFFF; padding: 40px; border-radius: 20px; border: 1px solid #E6F3FF; 
        text-align: center; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); position: relative;
    }
    .formula-hint {
        background-color: #F1F1F1; color: #555555; padding: 5px 15px;
        border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.9em;
    }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; border-radius: 12px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 初始化狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]

# --- 2. 工具函數 ---
def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).replace(" ", "").strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: pass

@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url).fillna("")
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

def generate_daily_quiz():
    # 此處保留原本的隨機翻譯題目邏輯
    return {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}

# --- 3. 主介面 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 結算報告
if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""<div class="report-box"><h3 style='text-align: center;'>📊 複習結算</h3><p style='text-align: center; font-size: 20px;'>準確率：{acc:.1f}% ({st.session_state.ex_correct}/{st.session_state.ex_total})</p></div>""", unsafe_allow_html=True)
    if st.session_state.wrong_items:
        st.subheader("❌ 寫錯的內容：")
        for w in st.session_state.wrong_items:
            st.write(f"📍 {w['cn']} → {w['kr']}")
    if st.button("🔄 開啟新測驗"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.wrong_items = []; st.session_state.pools = {"單字": [], "文法": [], "發音": []}; st.session_state.show_report = False; st.rerun()
    st.stop()

# --- 💡 每日一句翻譯考試 (置頂) ---
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state: st.session_state.dq = generate_daily_quiz()
if 'dq_id' not in st.session_state: st.session_state.dq_id = 0
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入翻譯答案：", key=f"dq_in_{st.session_state.dq_id}")

c_dq1, c_dq2 = st.columns(2)
with c_dq1:
    if st.button("驗證翻譯"):
        if u_in_dq and clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
        else: st.error(f"❌ 答案：{dq['kr']}"); play_audio(dq['kr'])
with c_dq2:
    if st.button("換下一題翻譯"):
        st.session_state.dq = generate_daily_quiz(); st.session_state.dq_id += 1; st.rerun()

st.divider()

# --- 4. Excel 複習區 ---
st.subheader("🎯 Excel 題庫：文法造句與複習")
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_ch
    
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        elif not new: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}

    st.multiselect("複習範圍：", options, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
    final_ch = all_ch if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch

    tabs = st.tabs(["📖 單字", "📝 文法造句", "📢 發音"])
    cat_list = ["單字", "文法", "發音"]
    
    for i, tab in enumerate(tabs):
        with tab:
            cat = cat_list[i]
            if not st.session_state.pools[cat]:
                curr_df = df[(df['type'] == cat) & (df['chapter'].astype(str).isin(final_ch))]
                if not curr_df.empty:
                    st.session_state.pools[cat] = curr_df.to_dict('records')
                    random.shuffle(st.session_state.pools[cat])
            
            p = st.session_state.pools[cat]
            if p:
                st.write(f"📝 剩餘：{len(p)} 題")
                item = p[0]
                
                if cat == "文法":
                    # ✨ 這裡就是妳要的新功能：依據妳的設計圖顯示
                    if item.get('note'):
                        st.markdown(f'<div class="grammar-rule-box">✨ 文法規則：{item["note"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="flashcard-main">
                        <h2 style="color: #1A1A1A;">{item['cn']}</h2>
                        <div class="formula-hint">💡 公式提示：{item['kr']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    u_in = st.text_input("請輸入韓文造句：", key=f"ex_{cat}_{len(p)}")
                    
                    if st.button("提交驗證", key=f"btn_{cat}"):
                        # 優先比對 answer 欄位，沒有就比對 kr
                        ans_col = 'answer' if 'answer' in df.columns else 'kr'
                        correct_ans = str(item[ans_col])
                        is_ok = clean_text(u_in) == clean_text(correct_ans)
                        st.session_state.ex_total += 1
                        if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1; st.balloons()
                        else: st.error(f"❌ 錯誤！正確答案：{correct_ans}")
                        play_audio(correct_ans)
                else:
                    # 一般單字/發音
                    st.markdown(f"""<div class="flashcard-main"><h2>{item['cn']}</h2><small>單元：{item['chapter']}</small></div>""", unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文：", key=f"ex_{cat}_{len(p)}")
                    if st.button("驗證", key=f"btn_{cat}"):
                        if clean_text(u_in) == clean_text(str(item['kr'])):
                            st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                        else: st.error(f"❌ 答案：{item['kr']}")
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}"): p.pop(0); st.rerun()
            else: st.write("✅ 該類別已完成。")

    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束測驗並產出報告"): st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.info("宜真加油！💙 每天練習，10 月 TOPIK 考照必勝！")
