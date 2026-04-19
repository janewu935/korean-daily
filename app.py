import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re
from datetime import date

st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- CSS 樣式 (依照設計圖優化) ---
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
        font-weight: bold;
    }
    .flashcard-main { 
        background-color: #FFFFFF; 
        padding: 40px; 
        border-radius: 20px; 
        border: 1px solid #E6F3FF; 
        text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
    }
    .formula-hint {
        background-color: #F1F1F1;
        color: #555555;
        padding: 5px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 15px;
        font-size: 0.9em;
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

# --- 2. 狀態初始化 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]

# --- 3. 介面呈現 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 每日翻譯挑戰
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state:
    st.session_state.dq = {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入翻譯答案：", key="dq_input")
if st.button("驗證翻譯"):
    if u_in_dq and clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
    else: st.error(f"❌ 錯誤！正確答案：{dq['kr']}"); play_audio(dq['kr'])

st.divider()

# --- 4. Excel 複習區 ---
st.subheader("🎯 Excel 題庫：文法造句模式")
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

    st.multiselect("選擇複習章節：", options, key="temp_sel", on_change=sync_selection, default=st.session_state.sel_ch)
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
                    # 1. 藍色虛線框：顯示 note (文法規則)
                    if item.get('note'):
                        st.markdown(f'<div class="grammar-rule-box">✨ 文法規則：{item["note"]}</div>', unsafe_allow_html=True)
                    
                    # 2. 大題目卡：顯示 cn (隨機生成的中文題目)
                    st.markdown(f"""
                    <div class="flashcard-main">
                        <h2 style="color: #1A1A1A;">{item['cn']}</h2>
                        <div class="formula-hint">💡 公式提示：{item['kr']}</div>
                        <br><br><small style="color: #999;">單元：{item['chapter']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    # 3. 造句輸入區
                    # 如果妳 Excel 有 answer 欄位，請將 item['kr'] 改為 item['answer']
                    u_in = st.text_input("請根據題目與公式造出韓文句子：", key=f"ex_{cat}_{len(p)}")
                
                else:
                    # 一般單字/發音模式
                    st.markdown(f"""<div class="flashcard-main"><h2>{item['cn']}</h2><small>單元：{item['chapter']}</small></div>""", unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文答案：", key=f"ex_{cat}_{len(p)}")

                # 提交驗證
                if st.button("驗證答案", key=f"btn_{cat}"):
                    # 這裡比對的是妳輸入的句子 vs Excel 裡的答案
                    # 建議 Excel 增加一欄 'answer' 放完整正確句子
                    target_ans = item.get('answer', item['kr']) 
                    is_ok = clean_text(u_in) == clean_text(str(target_ans))
                    
                    st.session_state.ex_total += 1
                    if is_ok:
                        st.success("⭕ 太強了！句子完全正確。"); st.session_state.ex_correct += 1; st.balloons()
                    else:
                        st.error(f"❌ 差一點點！正確答案參考：{target_ans}")
                        st.session_state.wrong_items.append(item)
                    play_audio(target_ans)
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}"): p.pop(0); st.rerun()
            else:
                st.write("✅ 已完成該章節練習。")

st.divider()
st.info("宜真加油！💙 照著這個節奏練習，10 月的 TOPIK 考照一定穩！")
