import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# --- 1. 初始化狀態 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
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

# --- CSS 樣式 (精準對位) ---
st.markdown("""
    <style>
    .grammar-rule-box { 
        border: 2px dashed #007FFF; 
        padding: 10px; border-radius: 10px; color: #007FFF; text-align: center; margin-bottom: 20px;
        background-color: rgba(0, 127, 255, 0.05); font-weight: bold;
    }
    .flashcard-main { 
        background-color: #FFFFFF; padding: 40px; border-radius: 20px; 
        border: 1px solid #E6F3FF; text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
    }
    .formula-hint {
        background-color: #F1F1F1; color: #555555; padding: 5px 15px;
        border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 主介面 ---
st.title("💙 韓語全能學習系統 💙")

df = load_data()
if not df.empty:
    # 互斥選單邏輯
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_ch
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}

    st.multiselect("選擇複習章節：", options, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
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
                    # 顯示規則 (note)
                    if item.get('note'):
                        st.markdown(f'<div class="grammar-rule-box">✨ 文法規則：{item["note"]}</div>', unsafe_allow_html=True)
                    
                    # 顯示題目卡 (cn: 姊姊正在睡覺)
                    st.markdown(f"""
                    <div class="flashcard-main">
                        <h2 style="color: #1A1A1A;">{item['cn']}</h2>
                        <div class="formula-hint">💡 公式提示：{item['kr']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 輸入造句
                    u_in = st.text_input("請根據題目造出韓文句子：", key=f"ex_{cat}_{len(p)}")
                    
                    if st.button("提交驗證", key=f"btn_{cat}"):
                        # 💡 這裡的比對目標：優先看 Excel 有沒有 'answer' 欄位，沒有就比對 'kr'
                        ans_col = 'answer' if 'answer' in df.columns else 'kr'
                        correct_ans = str(item[ans_col])
                        
                        is_ok = clean_text(u_in) == clean_text(correct_ans)
                        st.session_state.ex_total += 1
                        if is_ok:
                            st.success("⭕ 正確！句子寫得很好。"); st.session_state.ex_correct += 1; st.balloons()
                        else:
                            st.error(f"❌ 錯誤！正確答案是：{correct_ans}")
                        play_audio(correct_ans)
                else:
                    # 單字/發音模式
                    st.markdown(f"""<div class="flashcard-main"><h2>{item['cn']}</h2></div>""", unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文：", key=f"ex_{cat}_{len(p)}")
                    if st.button("驗證", key=f"btn_{cat}"):
                        if clean_text(u_in) == clean_text(str(item['kr'])):
                            st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                        else: st.error(f"❌ 答案：{item['kr']}")
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}"): p.pop(0); st.rerun()
            else:
                st.write("✅ 該類別已完成。")
