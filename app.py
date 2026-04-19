import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re
from datetime import date

st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- CSS 樣式 (精準還原妳的設計) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .grammar-rule-box { 
        border: 2px dashed #007FFF; 
        padding: 15px; 
        border-radius: 10px; 
        color: #007FFF; 
        text-align: center; 
        margin-bottom: 20px;
        background-color: rgba(0, 127, 255, 0.05);
    }
    .flashcard-main { 
        background-color: #FFFFFF; 
        padding: 40px; 
        border-radius: 20px; 
        border: 1px solid #E6F3FF; 
        text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
        position: relative;
    }
    .kr-hint {
        color: #666666;
        font-size: 1.2em;
        margin-top: 10px;
    }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; border: none; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 核心邏輯與數據 ---
@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        # 讀取 Excel 並保留所有欄位
        df = pd.read_csv(csv_url).fillna("")
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).replace(" ", "").strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: pass

# --- 2. 初始化狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]

# --- 3. 介面呈現 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 每日翻譯考試 (置頂)
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state:
    st.session_state.dq = {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("在此輸入翻譯挑戰：", key="dq_input")
if st.button("驗證翻譯挑戰"):
    if u_in_dq and clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
    else: st.error(f"❌ 錯誤！正確答案：{dq['kr']}"); play_audio(dq['kr'])

st.divider()

# --- 4. Excel 複習區 ---
st.subheader("🎯 Excel 題庫複習區")
df = load_data()

if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_ch
    
    def sync_selection():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        elif not new: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}

    st.multiselect("複習範圍：", options, key="temp_sel", on_change=sync_selection, default=st.session_state.sel_ch)
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
                item = p[0]
                
                if cat == "文法":
                    # 💡 依照妳的設計圖顯示
                    # 1. 藍色虛線框 (note 欄位)
                    if item.get('note'):
                        st.markdown(f'<div class="grammar-rule-box">✨ 練習文法：{item["note"]}</div>', unsafe_allow_html=True)
                    
                    # 2. 大題目卡 (cn 欄位與 kr 提示)
                    st.markdown(f"""
                    <div class="flashcard-main">
                        <h2 style="margin-bottom:0px;">{item['cn']}</h2>
                        <div class="kr-hint">公式提示：{item['kr']}</div>
                        <br><small style="color:#999;">單元：{item['chapter']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("") # 留白
                    u_in = st.text_input("請輸入完整的韓文造句：", key=f"ex_{cat}_{len(p)}")
                
                else:
                    # 一般單字或發音模式
                    st.markdown(f"""<div class="flashcard-main"><h2>{item['cn']}</h2><small>單元：{item['chapter']}</small></div>""", unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文回答：", key=f"ex_{cat}_{len(p)}")

                # 驗證邏輯
                if st.button("提交驗證", key=f"btn_{cat}"):
                    # 注意：這裡的驗證會針對妳輸入的內容進行
                    # 如果是文法題，請在 Excel 另外準備一欄或是直接比對 kr (看妳的 Excel 答案放哪)
                    # 目前邏輯：比對妳輸入的內容與 Excel 的 kr 欄位 (或妳可以新增一欄叫 answer)
                    is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                    st.session_state.ex_total += 1
                    if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                    else: st.error(f"❌ 錯誤！正確答案參考：{item['kr']}")
                    play_audio(item['kr'])
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}"): p.pop(0); st.rerun()
            else:
                st.write("✅ 該類別已完成複習。")

st.divider()
st.info("宜真加油！💙 照著妳設計的完美練習法，TOPIK 2 絕對沒問題！")
