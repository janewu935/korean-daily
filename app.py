import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re
from datetime import date

st.set_page_config(page_title="韓語全能練習", page_icon="💙")

# --- CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .grammar-rule-box { 
        border: 2px dashed #007FFF; padding: 12px; border-radius: 10px; color: #007FFF; 
        text-align: center; margin-bottom: 20px; background-color: rgba(0, 127, 255, 0.05); font-weight: bold;
    }
    .flashcard-main { 
        background-color: #FFFFFF; padding: 40px; border-radius: 20px; border: 1px solid #E6F3FF; 
        text-align: center; box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
    }
    .formula-hint {
        background-color: #F1F1F1; color: #555555; padding: 5px 15px;
        border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.9em;
    }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; }
    .stop-button>button { background-color: #FF4B4B !important; color: white !important; border-radius: 12px; }
    .progress-text { color: #007FFF; font-weight: bold; margin-bottom: 5px; text-align: right; }
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

# --- 2. 智慧造句引擎 ---
def generate_auto_sentence(grammar_formula):
    subjects = [{"cn": "姊姊", "kr": "언니는"}, {"cn": "老師", "kr": "선생님은"}, {"cn": "朋友", "kr": "친구는"}, {"cn": "妹妹", "kr": "여동생은"}]
    actions = [
        {"cn": "坐火車", "root": "기차를 타", "pol": "기차를 타요", "ing": "기차를 타고 있어요"},
        {"cn": "喝咖啡", "root": "커피를 마셔", "pol": "커피를 마셔요", "ing": "커피를 마시고 있어요"},
        {"cn": "看電影", "root": "영화를 봐", "pol": "영화를 봐요", "ing": "영화를 보고 있어요"},
        {"cn": "吃麵包", "root": "빵을 먹", "pol": "빵을 먹어요", "ing": "빵을 먹고 있어요"}
    ]
    sub = random.choice(subjects); act = random.choice(actions)
    if "고 있다" in str(grammar_formula) or "正在" in str(grammar_formula):
        return {"cn": f"{sub['cn']}正在{act['cn']}。", "ans": f"{sub['kr']} {act['ing']}"}
    elif "고 싶다" in str(grammar_formula) or "想" in str(grammar_formula):
        tail = "고 싶어 해요" if sub['cn'] != "我" else "고 싶어요"
        return {"cn": f"{sub['cn']}想{act['cn']}。", "ans": f"{sub['kr']} {act['root']}{tail}"}
    else:
        return {"cn": f"{sub['cn']}{act['cn']}。", "ans": f"{sub['kr']} {act['pol']}"}

def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).replace(" ", "").strip()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko'); fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
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

# --- 3. 介面呈現 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 結算報告邏輯 (維持不變)
if st.session_state.show_report:
    # ... (結算代碼)
    st.stop()

# 每日一句翻譯挑戰
st.subheader("✍️ 每日一句翻譯挑戰")
if 'dq' not in st.session_state: st.session_state.dq = {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}
st.info(f"💡 「 {st.session_state.dq['cn']} 」")
u_in_dq = st.text_input("輸入翻譯挑戰：", key="dq_in")
if st.button("驗證翻譯挑戰"):
    if clean_text(u_in_dq) == clean_text(st.session_state.dq['kr']): st.success("⭕ 正確！"); st.balloons()
    else: st.error(f"❌ 正確答案：{st.session_state.dq['kr']}"); play_audio(st.session_state.dq['kr'])

st.divider()

# Excel 複習區
st.subheader("🎯 Excel 題庫複習")
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
    st.multiselect("複習範圍：", ["ALL 全部單元"]+all_ch, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
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
                # 🛠️ 重新加回來的顯示題數代碼 
                st.markdown(f'<p class="progress-text">📝 剩餘：{len(p)} 題</p>', unsafe_allow_html=True)
                
                item = p[0]
                if cat == "文法":
                    if 'auto_q' not in st.session_state or st.session_state.get('last_item_cn') != item['cn']:
                        st.session_state.auto_q = generate_auto_sentence(item['kr'])
                        st.session_state.last_item_cn = item['cn']
                    q = st.session_state.auto_q
                    if item.get('note'): st.markdown(f'<div class="grammar-rule-box">✨ 文法規則：{item["note"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="flashcard-main"><h2>{q["cn"]}</h2><div class="formula-hint">💡 公式提示：{item["kr"]}</div></div>', unsafe_allow_html=True)
                    u_in = st.text_input("請造句：", key=f"ex_{cat}_{len(p)}")
                    if st.button("提交驗證", key=f"btn_{cat}"):
                        st.session_state.ex_total += 1
                        if clean_text(u_in) == clean_text(q['ans']): st.success(f"⭕ 正確！：{q['ans']}"); st.session_state.ex_correct += 1; st.balloons()
                        else: st.error(f"❌ 錯誤！答案：{q['ans']}"); st.session_state.wrong_items.append({"cn": q['cn'], "kr": q['ans']})
                        play_audio(q['ans'])
                else:
                    st.markdown(f'<div class="flashcard-main"><h2>{item["cn"]}</h2><small>單元：{item["chapter"]}</small></div>', unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文：", key=f"in_{cat}_{len(p)}")
                    if st.button("驗證", key=f"btn_{cat}"):
                        st.session_state.ex_total += 1
                        if clean_text(u_in) == clean_text(str(item['kr'])): st.success("⭕ 正確！"); st.session_state.ex_correct += 1
                        else: st.error(f"❌ 正確答案：{item['kr']}"); st.session_state.wrong_items.append(item)
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}"):
                    if 'auto_q' in st.session_state: del st.session_state.auto_q
                    p.pop(0); st.rerun()
            else: st.write("✅ 已完成該類別複習。")

    st.markdown('<div class="stop-button">', unsafe_allow_html=True)
    if st.button("⏹️ 結束測驗並看報告"): st.session_state.show_report = True; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
st.info("宜真加油！💙 題數顯示回來了，更有練習動力囉！")
