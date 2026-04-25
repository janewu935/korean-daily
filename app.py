import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# --- 1. 初始化與頁面設定 ---
st.set_page_config(page_title="韓語全能練習", page_icon="💙")

# 客製化淡色系 CSS 樣式
st.markdown("""
    <style>
    /* 全局背景與文字顏色 */
    .stApp { 
        background-color: #fdfaf6; /* 米色背景 */
    }
    h2, h3, p, span, label, .formula-hint, .progress-text { 
        color: #444444 !important; /* 深灰色文字，增加可讀性 */
    }
    
    /* 頁面大標題 */
    .main-title { 
        color: #a3d2e2 !important; /* 淡藍色標題 */
        font-size: 38px; 
        font-weight: 800; 
        text-align: center; 
        margin-top: -20px;
        margin-bottom: 30px;
    }
    
    /* 每日挑戰置頂樣式 */
    .daily-header {
        font-size: 24px;
        font-weight: 700;
        color: #444444;
        margin-bottom: -15px;
    }
    
    /* 輸入/結果區域標籤 */
    .box-label {
        color: #a3d2e2;
        font-weight: 700;
        margin-bottom: 2px;
    }
    
    /* 文法規則 Dasher Dashed Box */
    .grammar-rule-box { 
        border: 2px dashed #a3d2e2; 
        padding: 12px; 
        border-radius: 10px; 
        color: #a3d2e2; 
        text-align: center; 
        margin-top: 10px;
        margin-bottom: 20px; 
        background-color: rgba(163, 210, 226, 0.05); /* 極淡藍色背景 */
        font-weight: bold; 
    }
    
    /* 題目大卡片樣式 */
    .flashcard-main { 
        background-color: #ffffff; 
        padding: 40px; 
        border-radius: 20px; 
        border: 1px solid #f8d5a3; /* 淡橙色邊框 */
        text-align: center; 
        box-shadow: 2px 2px 15px rgba(0,0,0,0.05); 
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* 灰色小字提示 */
    .formula-hint {
        background-color: #f8f8f8;
        color: #666666;
        padding: 5px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 15px;
        font-size: 0.9em;
    }
    
    /* 進度題數顯示 */
    .progress-text { 
        color: #a3d2e2; 
        font-weight: bold; 
        margin-bottom: 5px; 
        text-align: right; 
        font-size: 1.1em; 
    }
    
    /* 結束報告模式樣式 */
    .metric-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f8d5a3;
    }
    .wrong-item-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B; /* 紅色邊緣，區分錯誤 */
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* 淡色系按鈕樣式 */
    .stButton>button { 
        background-color: #a3d2e2 !important; /* 淡藍色按鈕 */
        color: white !important; 
        border-radius: 12px; 
        font-weight: bold; 
        width: 100%; 
        height: 45px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #89c0d1 !important; /* 滑過時稍微加深藍色 */
    }
    
    /* "考試"模式按鈕特定樣式 */
    [data-testid="stRadio"] label[aria-checked="true"] {
        color: #f8d5a3; /* 考試模式選中時的淡橙色文字 */
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
state_keys = {
    'ex_total': 0, 'ex_correct': 0, 'show_report': False, 
    'wrong_items': [], 'pools': {"單字": [], "文法": [], "發音": []},
    'sel_ch': ["ALL 全部單元"], 'dq_idx': 0, 'exam_mode': "📖 複習"
}
for key, value in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 2. 智慧造句引擎 (配合 Excel cn 欄位) ---
def generate_auto_sentence(excel_cn, excel_kr):
    subjects = [{"cn": "姊姊", "kr": "언니는", "is": "언니예요"}, {"cn": "老師", "kr": "선생님은", "is": "선생님이에요"}, {"cn": "妹妹", "kr": "여동생은", "is": "여동생이에요"}, {"cn": "我", "kr": "저는", "is": "저예요"}]
    objects = [{"cn": "學生", "kr": "학생", "is": "학생이에요"}, {"cn": "韓國人", "kr": "한국 사람", "is": "한국 사람이에요"}, {"cn": "醫生", "kr": "의사", "is": "의사예요"}]
    actions = [
        {"cn": "看電影", "root": "영화를 보", "pol": "영화를 봐요", "ing": "영화를 보고 있어요", "want": "영화를 보고 싶어요", "hate": "영화를 보기 싫어해요", "neg": "영화를 보지 않아요"},
        {"cn": "喝咖啡", "root": "커評를 마시", "pol": "커피를 마셔요", "ing": "커피를 마시고 있어요", "want": "커피를 마시고 싶어요", "hate": "커피를 마시기 싫어해요", "neg": "커피를 마시지 않아요"},
        {"cn": "吃麵包", "root": "빵을 먹", "pol": "빵을 먹어요", "ing": "빵을 먹고 있어요", "want": "빵을 먹고 싶어요", "hate": "빵을 먹기 싫어해요", "neg": "빵을 먹意지 않아요"}
    ]
    sub = random.choice(subjects); obj = random.choice(objects); act = random.choice(actions)
    label = str(excel_cn)
    if "是＋名詞" in label or "名詞예요/이에요" in str(excel_kr): return {"cn": f"{sub['cn']}是{obj['cn']}。", "ans": f"{sub['kr']} {obj['is']}"}
    elif "正在" in label: return {"cn": f"{sub['cn']}正在{act['cn']}。", "ans": f"{sub['kr']} {act['ing']}"}
    elif "不想" in label: return {"cn": f"{sub['cn']}不想{act['cn']}。", "ans": f"{sub['kr']} {act['hate']}"}
    elif "想" in label: return {"cn": f"{sub['cn']}想{act['cn']}。", "ans": f"{sub['kr']} {act['want']}"}
    elif "不＋" in label or "不＋動詞" in label: return {"cn": f"{sub['cn']}不{act['cn']}。", "ans": f"{sub['kr']} {act['neg']}"}
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

# --- 3. 主程式介面 ---
st.markdown('<p class="main-title">💙 韓語全能造句練習機 💙</p>', unsafe_allow_html=True)

# 📊 分析報告顯示
if st.session_state.show_report:
    st.subheader("📊 練習成果報告結算")
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.metric("整體準確率", f"{acc:.1f}%", f"{st.session_state.ex_correct} / {st.session_state.ex_total}")
    if st.session_state.wrong_items:
        st.write("❌ 需要加強的部分 (錯題重練)：")
        for w in st.session_state.wrong_items:
            st.markdown(f'<div class="wrong-item-box"><b>題目：</b>{w["cn"]}<br><b>正確解答參考：</b>{w["ans"]}</div>', unsafe_allow_html=True)
    else:
        st.success(" Perfect! 全部題目都答對了！🎉")
    if st.button("🔄 開啟新的一輪練習"):
        for k in ['ex_total', 'ex_correct', 'wrong_items', 'show_report']: st.session_state[k] = 0 if isinstance(state_keys[k], int) else state_keys[k]
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}; st.rerun()
    st.stop()

# ✍️ 每日翻譯挑戰 (手動換題，長得像設計圖那樣)
st.markdown('<p class="daily-header">每日挑戰</p>', unsafe_allow_html=True)
daily_list = [{"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}, {"cn": "姊姊不是學生。", "kr": "언니는 학생이 아니에요"}, {"cn": "朋友正在坐火車。", "kr": "친구는 기차를 타고 있어요"}]
dq = daily_list[st.session_state.dq_idx % len(daily_list)]
st.markdown(f'<div class="flashcard-main"><h3>{dq["cn"]}</h3></div>', unsafe_allow_html=True)
st.markdown('<p class="box-label">Answer:</p>', unsafe_allow_html=True)
u_dq = st.text_input("", key="dq_in", placeholder="在此輸入您的翻譯...")
if st.button("驗證挑戰結果", key="check_dq"):
    if clean_text(u_dq) == clean_text(dq['kr']): st.success("⭕ 正確！：저예요"); st.balloons()
    else: st.error(f"❌ 錯誤！正確答案參考：{dq['kr']}"); play_audio(dq['kr'])
if st.button("下一句挑戰 ➡️", key="nxt_dq"): st.session_state.dq_idx += 1; st.rerun()

st.divider()

# Excel 題庫區 (美編大改，長得像設計圖那樣)
st.subheader("Chapter Review/Exam")
df = load_data()
if not df.empty:
    # 互斥模式選擇：複習 vs 考試
    exam_tab = st.radio("練習模式：", ["📖 複習", "✍️ 考試"], horizontal=True, key="mode_sel", default=st.session_state.exam_mode)
    
    # 互斥選單邏輯
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        elif not new: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
    st.markdown('<p class="box-label">Select Chapter:</p>', unsafe_allow_html=True)
    st.multiselect("", ["ALL 全部單元"]+all_ch, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
    final_ch = all_ch if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch

    tabs = st.tabs(["📖 單字複習", "📝 文法造句", "📢 發音練習"])
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
                st.markdown(f'<p class="progress-text">🎯 本輪剩餘：{len(p)} 題</p>', unsafe_allow_html=True)
                item = p[0]
                
                # 題目大卡片設計
                if cat == "文法":
                    if 'auto_q' not in st.session_state or st.session_state.get('last_item_key') != f"v_{len(p)}":
                        st.session_state.auto_q = generate_auto_sentence(item['cn'], item['kr'])
                        st.session_state.last_item_key = f"v_{len(p)}"
                    q = st.session_state.auto_q
                    
                    if item.get('note'): st.markdown(f'<div class="grammar-rule-box">✨ 規則：{item["note"]}</div>', unsafe_allow_html=True)
                    
                    if exam_tab == "📖 複習":
                        # 複習模式：顯示題目、規則、公式
                        st.markdown(f'<div class="flashcard-main"><h2 style="color:#1A1A1A">{q["cn"]}</h2><div class="formula-hint">💡 參考公式：{item["kr"]}</div></div>', unsafe_allow_html=True)
                    else:
                        # 考試模式：只顯示題目和單元，隱藏參考公式
                        st.markdown(f'<div class="flashcard-main"><h2 style="color:#1A1A1A">{q["cn"]}</h2><small style="color:#999;">單元：{item["chapter"]}</small></div>', unsafe_allow_html=True)
                    target_ans = q['ans']
                else:
                    # 一般單字/發音模式
                    st.markdown(f'<div class="flashcard-main"><h2 style="color:#1A1A1A">{item["cn"]}</h2><small style="color:#999;">單元：{item["chapter"]}</small></div>', unsafe_allow_html=True)
                    target_ans = item['kr']

                # 輸入區大卡片設計
                st.markdown('<p class="box-label">Answer:</p>', unsafe_allow_html=True)
                u_in = st.text_input("", key=f"input_{cat}_{len(p)}", placeholder="在此輸入完整的韓文...")
                
                if st.button("提交答案挑戰", key=f"btn_{cat}_{len(p)}"):
                    st.session_state.ex_total += 1
                    if clean_text(u_in) == clean_text(str(target_ans)):
                        st.success(f"⭕ 太棒了，正確！解答參考：{target_ans}"); st.session_state.ex_correct += 1; st.balloons()
                    else:
                        st.error(f"❌ 答錯囉！答案參考：{target_ans}")
                        st.session_state.wrong_items.append({"cn": q['cn'] if cat=="文法" else item['cn'], "ans": target_ans})
                    play_audio(target_ans)
                
                if st.button("下一題 ➡️", key=f"nxt_{cat}_{len(p)}"):
                    if 'auto_q' in st.session_state: del st.session_state.auto_q
                    p.pop(0); st.rerun()
            else:
                st.success(f"✅恭喜！{cat}類別的本輪練習已全部完成！章節單元無重複題目。")
                if st.button(f"重啟{cat}新練習", key=f"reset_{cat}"):
                    st.session_state.pools[cat] = []; st.rerun()

    st.divider()
    if st.button("⏹️ 結束練習並產出完整報告"):
        st.session_state.show_report = True; st.rerun()

st.info("宜真加油！💙 用《大家的韓國語》第一冊紮實打底，10月考取 TOPIK 2 吧！")
