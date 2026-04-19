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
    .grammar-focus { background-color: #E6F3FF; border: 2px dashed #007FFF; padding: 10px; border-radius: 10px; color: #007FFF; text-align: center; font-size: 1.2em; margin-bottom: 15px; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 核心邏輯 ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]

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

# --- 2. 介面呈現 ---
st.markdown('<p class="main-title">💙 韓語造句練習 💙</p>', unsafe_allow_html=True)

# 每日翻譯考試 (維持原樣)
st.subheader("✍️ 每日一句翻譯考試")
if 'dq' not in st.session_state:
    st.session_state.dq = {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}
dq = st.session_state.dq
st.info(f"💡 「 {dq['cn']} 」")
u_in_dq = st.text_input("輸入韓文：", key="dq_field")
if st.button("驗證翻譯"):
    if u_in_dq and clean_text(u_in_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
    else: st.error(f"❌ 答案：{dq['kr']}"); play_audio(dq['kr'])

st.divider()

# --- 3. Excel 複習區 ---
st.subheader("🎯 Excel 題庫：分類與造句練習")
df = load_data()

if not df.empty:
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_chapters
    
    def handle_selection():
        latest = st.session_state.selector_key
        old = st.session_state.sel_ch
        if old == ["ALL 全部單元"] and len(latest) > 1: st.session_state.sel_ch = [x for x in latest if x != "ALL 全部單元"]
        elif "ALL 全部單元" in latest and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        elif not latest: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = latest
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}

    st.multiselect("選擇複習範圍：", options, key="selector_key", default=st.session_state.sel_ch, on_change=handle_selection)

    final_ch = all_chapters if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch
    tabs = st.tabs(["📖 單字", "📝 文法造句", "📢 發音"])
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
                item = p[0]
                cn_text = item['cn']
                
                # 💡 針對文法造句顯示公式提示
                grammar_hint = ""
                if target_cat == "文法":
                    match = re.search(r'（(.*?)）', cn_text)
                    if match:
                        grammar_hint = match.group(1)
                        cn_display = cn_text.replace(f"（{grammar_hint}）", "").strip()
                    else:
                        cn_display = cn_text
                    
                    if grammar_hint:
                        st.markdown(f'<div class="grammar-focus">✨ 練習文法：{grammar_hint}</div>', unsafe_allow_html=True)
                else:
                    cn_display = cn_text

                st.markdown(f"""<div class="flashcard"><h3>{cn_display}</h3><small>單元：{item['chapter']}</small></div>""", unsafe_allow_html=True)
                
                u_in = st.text_input("請翻譯成完整的韓文句子：", key=f"ex_{target_cat}_{len(p)}")
                
                if st.button("提交驗證", key=f"btn_{target_cat}"):
                    is_ok = clean_text(u_in) == clean_text(str(item['kr']))
                    st.session_state.ex_total += 1
                    if is_ok: st.success("⭕ 正確！"); st.session_state.ex_correct += 1; st.balloons()
                    else: st.error(f"❌ 錯誤！正確答案是：{item['kr']}"); st.session_state.wrong_items.append(item)
                    play_audio(item['kr'])

                if st.button("下一題 ➡️", key=f"next_{target_cat}"):
                    p.pop(0); st.rerun()
            else:
                st.write("✅ 該分類複習完畢。")

# 報告顯示邏輯
if st.session_state.show_report:
    st.subheader("📊 複習報告")
    # ... (省略報告代碼)

if st.button("⏹️ 結束複習並看報告"): st.session_state.show_report = True; st.rerun()
