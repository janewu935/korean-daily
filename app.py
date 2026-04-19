import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# --- 1. 初始化與主題設定 ---
st.set_page_config(page_title="韓語造句挑戰", page_icon="💙")

if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]

# --- 2. 核心：智慧造句引擎 ---
def generate_dynamic_sentence(grammar_type):
    """
    根據文法類型，自動生成題目與標準答案
    """
    subjects = [
        {"cn": "姊姊", "kr": "언니는"}, {"cn": "老師", "kr": "선생님은"},
        {"cn": "朋友", "kr": "친구는"}, {"cn": "我", "kr": "저는"},
        {"cn": "妹妹", "kr": "여동생은"}, {"cn": "哥哥", "kr": "오빠는"}
    ]
    actions = [
        {"cn": "坐火車", "root": "기차를 타", "pol": "기차를 타요", "past": "기차를 탔어요", "ing": "기차를 타고 있어요"},
        {"cn": "喝咖啡", "root": "커피를 마셔", "pol": "커피를 마셔요", "past": "커피를 마셨어요", "ing": "커피를 마시고 있어요"},
        {"cn": "睡覺", "root": "자", "pol": "자요", "past": "잤어요", "ing": "자고 있어요"},
        {"cn": "吃麵包", "root": "빵을 먹", "pol": "빵을 먹어요", "past": "빵을 먹었어요", "ing": "빵을 먹고 있어요"},
        {"cn": "看電影", "root": "영화를 봐", "pol": "영화를 봐요", "past": "영화를 봤어요", "ing": "영화를 보고 있어요"}
    ]
    
    sub = random.choice(subjects)
    act = random.choice(actions)
    
    # 根據 Excel 裡的文法名稱判斷
    if "正在" in grammar_type or "고 있다" in grammar_type:
        return {"cn": f"{sub['cn']}正在{act['cn']}。", "ans": f"{sub['kr']} {act['ing']}"}
    elif "過去" in grammar_type or "었/았" in grammar_type:
        return {"cn": f"{sub['cn']}昨天{act['cn']}了。", "ans": f"{sub['kr']} {act['past']}"}
    elif "想" in grammar_type or "고 싶다" in grammar_type:
        # 注意：第三人稱想做某事要用 고 싶어 해요，我用 고 싶어요
        tail = "고 싶어 해요" if sub['cn'] != "我" else "고 싶어요"
        return {"cn": f"{sub['cn']}想{act['cn']}。", "ans": f"{sub['kr']} {act['root']}{tail}"}
    else:
        # 預設現在式
        return {"cn": f"{sub['cn']}{act['cn']}。", "ans": f"{sub['kr']} {act['pol']}"}

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

# --- CSS 樣式 ---
st.markdown("""
    <style>
    .grammar-rule-box { border: 2px dashed #007FFF; padding: 10px; border-radius: 10px; color: #007FFF; text-align: center; margin-bottom: 20px; background-color: rgba(0, 127, 255, 0.05); font-weight: bold; }
    .flashcard-main { background-color: #FFFFFF; padding: 40px; border-radius: 20px; border: 1px solid #E6F3FF; text-align: center; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); }
    .formula-hint { background-color: #F1F1F1; color: #555555; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.9em; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 主程式 ---
st.markdown('<p class="main-title">💙 韓語全能造句系統 💙</p>', unsafe_allow_html=True)

# (每日挑戰置頂代碼)
st.subheader("✍️ 每日一句固定測驗")
# ...

st.divider()

# --- 4. Excel 聯動造句區 ---
st.subheader("🎯 Excel 文法自動造句")
df = load_data()
if not df.empty:
    # (互斥選單代碼)
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    options = ["ALL 全部單元"] + all_ch
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
    st.multiselect("範圍：", options, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
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
                    # 💡 重點：自動生成題目
                    if 'quiz_data' not in st.session_state or st.session_state.get('last_item') != item['cn']:
                        st.session_state.quiz_data = generate_dynamic_sentence(item['kr'])
                        st.session_state.last_item = item['cn']
                    
                    quiz = st.session_state.quiz_data
                    
                    st.markdown(f'<div class="grammar-rule-box">✨ 文法規則：{item["note"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="flashcard-main">
                        <h2 style="color: #1A1A1A;">{quiz['cn']}</h2>
                        <div class="formula-hint">💡 公式提示：{item['kr']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    u_in = st.text_input("請造句：", key=f"ex_v_{len(p)}")
                    if st.button("提交驗證", key=f"btn_v_{len(p)}"):
                        if clean_text(u_in) == clean_text(quiz['ans']):
                            st.success(f"⭕ 正確！：{quiz['ans']}"); st.balloons()
                            st.session_state.ex_correct += 1
                        else:
                            st.error(f"❌ 錯誤！正確答案：{quiz['ans']}")
                        play_audio(quiz['ans'])
                else:
                    # (單字/發音模式...)
                    st.markdown(f"""<div class="flashcard-main"><h2>{item['cn']}</h2></div>""", unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文：", key=f"in_{cat}_{len(p)}")
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}"):
                    if 'quiz_data' in st.session_state: del st.session_state.quiz_data
                    p.pop(0); st.rerun()
