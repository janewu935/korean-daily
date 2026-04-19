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
    .grammar-focus { background-color: #E6F3FF; border: 2px dashed #007FFF; padding: 10px; border-radius: 10px; color: #007FFF; text-align: center; font-size: 1.1em; margin-bottom: 15px; }
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
        df = pd.read_csv(csv_url).dropna(subset=['kr', 'cn'])
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- 3. 每日一句翻譯考試 ---
st.markdown('<p class="main-title">💙 韓語單字練習 💙</p>', unsafe_allow_html=True)
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state:
    st.session_state.dq = {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}
dq = st.session_state.dq
st.info(f"💡 **題目：** 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入翻譯答案：", key="dq_input")
if st.button("驗證翻譯"):
    if u_in_dq and clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
    else: st.error(f"❌ 錯誤！正確答案：{dq['kr']}"); play_audio(dq['kr'])
if st.button("換下一題翻譯"):
    # 這裡可以放隨機拼湊邏輯
    st.session_state.dq = {"cn": "昨天見了朋友。", "kr": "어제 친구를 만났어요"}
    st.rerun()

st.divider()

# --- 4. Excel 複習區 ---
st.subheader("🎯 Excel 題庫：分類造句練習")
df = load_data()

if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_ch
    
    def sync_selection():
        new = st.session_state.temp_sel
        old = st.session_state.sel_ch
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
                cn_raw = str(item['cn'])
                
                # 💡 修正後的解析邏輯：將括號分開
                # 找第一個出現的（ 或 (
                match = re.search(r'[（\(](.*?)[）\)]', cn_raw)
                if match:
                    hint = match.group(1) # 括號內的提示
                    question = cn_raw[:match.start()].strip() # 括號前的題目
                else:
                    hint = ""
                    question = cn_raw

                if cat == "文法" and hint:
                    st.markdown(f'<div class="grammar-focus">✨ 練習文法：{hint}</div>', unsafe_allow_html=True)
                
                # 確保題目不為空白，若為空白則顯示原始文字
                display_q = question if question else cn_raw
                st.markdown(f"""<div class="flashcard"><h3>{display_q}</h3><small>單元：{item['chapter']}</small></div>""", unsafe_allow_html=True)
                
                u_in = st.text_input("請輸入韓文答案：", key=f"ex_{cat}_{len(p)}")
                if st.button("提交驗證", key=f"btn_{cat}"):
                    is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                    st.session_state.ex_total += 1
                    if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                    else: st.error(f"❌ 錯誤！正確答案：{item['kr']}"); st.session_state.wrong_items.append(item)
                    play_audio(item['kr'])
                if st.button("下一題 ➡️", key=f"nxt_{cat}"): p.pop(0); st.rerun()
            else: st.write("✅ 已完成複習。")

st.divider()
st.info("宜真加油！💙 每天練習，TOPIK 2 沒問題！")
