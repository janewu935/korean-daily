import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# --- 1. 初始化與頁面設定 ---
st.set_page_config(page_title="韓語全能挑戰", page_icon="💙")

# CSS 樣式：強化文字對比度
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .grammar-rule-box { border: 2px dashed #007FFF; padding: 12px; border-radius: 10px; color: #007FFF; text-align: center; margin-bottom: 20px; background-color: rgba(0, 127, 255, 0.05); font-weight: bold; }
    
    /* 🚀 修正：大卡片文字顏色強制加深 */
    .flashcard-main { 
        background-color: #FFFFFF; padding: 40px; border-radius: 20px; border: 1px solid #E6F3FF; 
        text-align: center; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); 
    }
    .flashcard-main h2 { color: #333333 !important; font-weight: 800 !important; }
    
    .formula-hint { background-color: #F1F1F1; color: #555555; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.9em; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; }
    .progress-text { color: #007FFF; font-weight: bold; margin-bottom: 5px; text-align: right; font-size: 1.1em; }
    .report-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
state_keys = {
    'ex_total': 0, 'ex_correct': 0, 'show_report': False, 
    'wrong_items': [], 'pools': {"單字": [], "文法": [], "發音": []},
    'sel_ch': ["ALL 全部單元"], 'dq_idx': 0
}
for key, value in state_keys.items():
    if key not in st.session_state: st.session_state[key] = value

# --- 2. 智慧造句引擎 ---
def generate_auto_sentence(excel_cn, excel_kr):
    subjects = [{"cn": "姊姊", "kr": "언니는", "is": "언니예요"}, {"cn": "老師", "kr": "선생님은", "is": "선생님이에요"}, {"cn": "妹妹", "kr": "여動生은", "is": "여동생이에요"}]
    objects = [{"cn": "學生", "kr": "학생", "is": "학생이에요"}, {"cn": "韓國人", "kr": "한국 사람", "is": "한국 사람이에요"}]
    actions = [
        {"cn": "看電影", "root": "영화를 보", "pol": "영화를 봐요", "ing": "영화를 보고 있어요", "hate": "영화를 보기 싫어해요", "neg": "영화를 보지 않아요"},
        {"cn": "喝咖啡", "root": "커피를 마시", "pol": "커피를 마셔요", "ing": "커피를 마시고 있어요", "hate": "커피를 마시기 싫어해요", "neg": "커피를 마시지 않아요"}
    ]
    sub = random.choice(subjects); obj = random.choice(objects); act = random.choice(actions)
    label = str(excel_cn)
    if "是＋名詞" in label: return {"cn": f"{sub['cn']}是{obj['cn']}。", "ans": f"{sub['kr']} {obj['is']}"}
    elif "正在" in label: return {"cn": f"{sub['cn']}正在{act['cn']}。", "ans": f"{sub['kr']} {act['ing']}"}
    elif "不想" in label: return {"cn": f"{sub['cn']}不想{act['cn']}。", "ans": f"{sub['kr']} {act['hate']}"}
    elif "不＋" in label: return {"cn": f"{sub['cn']}不{act['cn']}。", "ans": f"{sub['kr']} {act['neg']}"}
    else: return {"cn": f"{sub['cn']}{act['cn']}。", "ans": f"{sub['kr']} {act['pol']}"}

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
        df = pd.read_csv(csv_url).fillna(""); df.columns = [c.strip().lower() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- 3. 主介面 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 分析報告
if st.session_state.show_report:
    st.subheader("📊 練習成果報告")
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.metric("準確率", f"{acc:.1f}%", f"{st.session_state.ex_correct} / {st.session_state.ex_total}")
    if st.session_state.wrong_items:
        for w in st.session_state.wrong_items:
            st.markdown(f'<div class="report-card"><b>題目：</b>{w["cn"]}<br><b>正確解答：</b>{w["ans"]}</div>', unsafe_allow_html=True)
    if st.button("🔄 重新開始練習"):
        for k in ['ex_total', 'ex_correct', 'wrong_items', 'show_report']: st.session_state[k] = 0 if isinstance(state_keys[k], int) else state_keys[k]
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}; st.rerun()
    st.stop()

# 每日翻譯挑戰 (手動換題)
st.subheader("✍️ 每日翻譯挑戰")
dq_list = [{"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}, {"cn": "姊姊正在坐火車。", "kr": "언니는 기차를 타고 있어요"}]
dq = dq_list[st.session_state.dq_idx % len(dq_list)]
st.info(f"💡挑戰： 「 {dq['cn']} 」")
u_dq = st.text_input("在此輸入翻譯挑戰答案：", key="dq_main_input")
if st.button("驗證挑戰結果"):
    if clean_text(u_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
    else: st.error(f"❌ 答案：{dq['kr']}"); play_audio(dq['kr'])
if st.button("換下一句挑戰 ➡️"): st.session_state.dq_idx += 1; st.rerun()

st.divider()

# Excel 複習區
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
    
    st.multiselect("選擇複習範圍：", ["ALL 全部單元"]+all_ch, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
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
                st.markdown(f'<p class="progress-text">📝 剩餘：{len(p)} 題</p>', unsafe_allow_html=True)
                item = p[0]
                if cat == "文法":
                    if 'auto_q' not in st.session_state or st.session_state.get('cur_q_key') != f"v_{len(p)}":
                        st.session_state.auto_q = generate_auto_sentence(item['cn'], item['kr'])
                        st.session_state.cur_q_key = f"v_{len(p)}"
                    q = st.session_state.auto_q
                    if item.get('note'): st.markdown(f'<div class="grammar-rule-box">✨ 規則：{item["note"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="flashcard-main"><h2>{q["cn"]}</h2><div class="formula-hint">💡 公式：{item["kr"]}</div></div>', unsafe_allow_html=True)
                    u_in = st.text_input("輸入完整造句答案：", key=f"in_{cat}_{len(p)}")
                    ans = q['ans']
                else:
                    st.markdown(f'<div class="flashcard-main"><h2>{item["cn"]}</h2><small>單元：{item["chapter"]}</small></div>', unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文回答：", key=f"in_{cat}_{len(p)}")
                    ans = item['kr']

                if st.button("提交驗證", key=f"btn_{cat}_{len(p)}"):
                    st.session_state.ex_total += 1
                    if clean_text(u_in) == clean_text(str(ans)):
                        st.success(f"⭕ 正確！解答：{ans}"); st.session_state.ex_correct += 1; st.balloons()
                    else:
                        st.error(f"❌ 錯誤！正確答案：{ans}")
                        st.session_state.wrong_items.append({"cn": q['cn'] if cat=="文法" else item['cn'], "ans": ans})
                    play_audio(ans)
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}_{len(p)}"):
                    if 'auto_q' in st.session_state: del st.session_state.auto_q
                    p.pop(0); st.rerun()
            else: st.write("✅ 已完成該章節練習。")

    if st.button("⏹️ 結束測驗並產出報告"): st.session_state.show_report = True; st.rerun()
