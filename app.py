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

# --- 1. 初始化統計 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False

def update_ex_stats(is_ok):
    st.session_state.ex_total += 1
    if is_ok: st.session_state.ex_correct += 1

# --- 2. 輔助功能 ---
@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df.dropna(subset=['kr', 'cn'])
    except: return pd.DataFrame()

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: st.error("語音失敗")

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語 Excel 題庫系統 💙</p>', unsafe_allow_html=True)

# 3. 分析報告顯示區 (放在最上方，方便看完就關掉)
if st.session_state.show_report:
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.markdown(f"""
    <div class="report-box">
        <h3 style='color: #007FFF; text-align: center;'>📊 Excel 複習良率報告</h3>
        <p style='text-align: center; font-size: 18px;'>今日 Excel 複習總量：{st.session_state.ex_total} 題</p>
        <p style='text-align: center; font-size: 18px;'>答對數：{st.session_state.ex_correct} | <b>準確率：{acc:.1f}%</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    if acc >= 85: st.success("🎯 製程穩定！妳對這些自建單字的掌握度非常高。")
    elif acc >= 60: st.warning("⚠️ 發現微量偏差，建議針對錯誤的章節加強複習。")
    else: st.error("🚨 良率過低！需要重新檢視 Excel 題庫內容與記憶狀況。")
    
    if st.button("清空數據並繼續複習"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0
        st.session_state.show_report = False; st.rerun()

st.divider()

# 4. Excel 題庫複習區
st.subheader("🎯 Excel 單字/文法複習")
df = load_data()
if not df.empty:
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇章節：", all_chapters)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cats = ["單字", "文法", "發音"]
    
    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cats[i]
            tmp = df[df['type'] == target_cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if not tmp.empty:
                # 獨立 Key 與重置 ID
                t_id = f"id_{target_cat}"
                if t_id not in st.session_state: st.session_state[t_id] = 0
                q_key = f"item_{target_cat}"
                if q_key not in st.session_state: st.session_state[q_key] = tmp.sample(1).iloc[0]
                
                item = st.session_state[q_key]
                st.write(f"📍 章節：{item['chapter']} | 題目：{item['cn']}")
                u_in = st.text_input("輸入韓文回答", key=f"in_{target_cat}_{st.session_state[t_id]}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("檢查答案", key=f"chk_{target_cat}"):
                        is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                        update_ex_stats(is_ok) # 這裡更新數據
                        if is_ok: st.balloons(); st.success("正確！")
                        else: st.error(f"正確答案：{item['kr']}")
                        play_audio(item['kr'])
                with c2:
                    if st.button("下一題", key=f"next_{target_cat}"):
                        if q_key in st.session_state: del st.session_state[q_key]
                        st.session_state[t_id] += 1; st.rerun()
            else:
                st.write(f"目前『{target_cat}』分類沒資料。")

    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束複習並看 Excel 統計報告"):
        st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Excel 還沒有資料喔！")
