import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# --- 1. 頁面與樣式設定 ---
st.set_page_config(page_title="韓語全能練習", page_icon="💙")

st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .grammar-rule-box { border: 2px dashed #007FFF; padding: 12px; border-radius: 10px; color: #007FFF; text-align: center; margin-bottom: 20px; background-color: rgba(0, 127, 255, 0.05); font-weight: bold; }
    .flashcard-main { background-color: #FFFFFF; padding: 40px; border-radius: 20px; border: 1px solid #E6F3FF; text-align: center; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); min-height: 200px; display: flex; flex-direction: column; justify-content: center; align-items: center;}
    .formula-hint { background-color: #F1F1F1; color: #555555; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-top: 15px; font-size: 0.9em; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; height: 45px;}
    .progress-text { color: #007FFF; font-weight: bold; margin-bottom: 5px; text-align: right; font-size: 1.1em; }
    .report-card { background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #007FFF; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化狀態 (Session State) ---
if 'ex_total' not in st.session_state: st.session_state.ex_total = 0
if 'ex_correct' not in st.session_state: st.session_state.ex_correct = 0
if 'show_report' not in st.session_state: st.session_state.show_report = False
if 'wrong_items' not in st.session_state: st.session_state.wrong_items = []
if 'pools' not in st.session_state: st.session_state.pools = {"單字": [], "文法": [], "發音": []}
if 'sel_ch' not in st.session_state: st.session_state.sel_ch = ["ALL 全部單元"]
if 'dq_index' not in st.session_state: st.session_state.dq_index = 0

# --- 3. 智慧造句引擎 (配合 Excel cn 欄位) ---
def generate_auto_sentence(excel_cn, excel_kr):
    subjects = [{"cn": "姊姊", "kr": "언니는", "is": "언니예요"}, {"cn": "老師", "kr": "선생님은", "is": "선생님이에요"}, {"cn": "朋友", "kr": "친구는", "is": "친구예요"}, {"cn": "妹妹", "kr": "여동생은", "is": "여동생이에요"}]
    objects = [{"cn": "學生", "kr": "학생", "is": "학생이에요"}, {"cn": "韓國人", "kr": "한국 사람", "is": "한국 사람이에요"}, {"cn": "醫生", "kr": "의사", "is": "의사예요"}]
    actions = [
        {"cn": "看電影", "root": "영화를 보", "pol": "영화를 봐요", "ing": "영화를 보고 있어요", "want": "영화를 보고 싶어요", "hate": "영화를 보기 싫어해요", "neg": "영화를 보지 않아요"},
        {"cn": "喝咖啡", "root": "커피를 마시", "pol": "커피를 마셔요", "ing": "커피를 마시고 있어요", "want": "커피를 마시고 싶어요", "hate": "커피를 마시기 싫어해요", "neg": "커피를 마시지 않아요"},
        {"cn": "吃麵包", "root": "빵을 먹", "pol": "빵을 먹어요", "ing": "빵을 먹고 있어요", "want": "빵을 먹고 싶어요", "hate": "빵을 먹기 싫어해요", "neg": "빵을 먹지 않아요"}
    ]
    sub = random.choice(subjects); obj = random.choice(objects); act = random.choice(actions)
    cn_label = str(excel_cn)

    if "是＋名詞" in cn_label:
        return {"cn": f"{sub['cn']}是{obj['cn']}。", "ans": f"{sub['kr']} {obj['is']}"}
    elif "正在" in cn_label:
        return {"cn": f"{sub['cn']}正在{act['cn']}。", "ans": f"{sub['kr']} {act['ing']}"}
    elif "想" in cn_label and "不想" not in cn_label:
        return {"cn": f"{sub['cn']}想{act['cn']}。", "ans": f"{sub['kr']} {act['want']}"}
    elif "不想" in cn_label:
        return {"cn": f"{sub['cn']}不想{act['cn']}。", "ans": f"{sub['kr']} {act['hate']}"}
    elif "不＋" in cn_label:
        return {"cn": f"{sub['cn']}不{act['cn']}。", "ans": f"{sub['kr']} {act['neg']}"}
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

# --- 4. 主介面 ---
st.markdown('<p class="main-title">💙 韓語全能學習系統 💙</p>', unsafe_allow_html=True)

# 分析報告頁面
if st.session_state.show_report:
    st.subheader("📊 練習成果分析")
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.metric("準確率", f"{acc:.1f}%", f"{st.session_state.ex_correct} / {st.session_state.ex_total}")
    
    if st.session_state.wrong_items:
        st.write("❌ 需要加強的部分：")
        for w in st.session_state.wrong_items:
            st.markdown(f'<div class="report-card"><b>題目：</b>{w["cn"]}<br><b>正確答案：</b>{w["kr"]}</div>', unsafe_allow_html=True)
    else:
        st.success("太棒了！這次練習全部正確！🎉")
        
    if st.button("🔄 開啟下一輪練習"):
        st.session_state.ex_total = 0; st.session_state.ex_correct = 0; st.session_state.wrong_items = []
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}; st.session_state.show_report = False; st.rerun()
    st.stop()

# 每日挑戰 (可手動換下一句)
st.subheader("✍️ 每日翻譯挑戰")
daily_sentences = [
    {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"},
    {"cn": "姊姊不是學生。", "kr": "언니는 학생이 아니에요"},
    {"cn": "朋友正在坐火車。", "kr": "친구는 기차를 타고 있어요"},
    {"cn": "今天天氣很好。", "kr": "오늘 날씨가 아주 좋아요"}
]
dq = daily_sentences[st.session_state.dq_index % len(daily_sentences)]
st.info(f"💡 挑戰題目： 「 {dq['cn']} 」")
u_dq = st.text_input("輸入挑戰答案：", key="dq_input")
col_dq1, col_dq2 = st.columns(2)
with col_dq1:
    if st.button("驗證挑戰"):
        if clean_text(u_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
        else: st.error(f"❌ 答案：{dq['kr']}"); play_audio(dq['kr'])
with col_dq2:
    if st.button("換下一句 ➡️"):
        st.session_state.dq_index += 1; st.rerun()

st.divider()

# Excel 題庫複習區
df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []} # 切換章節時清空題目池

    st.multiselect("選擇複習章節：", ["ALL 全部單元"]+all_ch, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
    final_ch = all_ch if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch

    tabs = st.tabs(["📖 單字複習", "📝 文法造句", "📢 發音練習"])
    cat_list = ["單字", "文法", "發音"]
    
    for i, tab in enumerate(tabs):
        with tab:
            cat = cat_list[i]
            # 建立不重複的題目池
            if not st.session_state.pools[cat]:
                curr_df = df[(df['type'] == cat) & (df['chapter'].astype(str).isin(final_ch))]
                if not curr_df.empty:
                    st.session_state.pools[cat] = curr_df.to_dict('records')
                    random.shuffle(st.session_state.pools[cat])
            
            pool = st.session_state.pools[cat]
            if pool:
                st.markdown(f'<p class="progress-text">🎯 本輪剩餘：{len(pool)} 題</p>', unsafe_allow_html=True)
                item = pool[0]
                
                if cat == "文法":
                    if 'auto_q' not in st.session_state or st.session_state.get('last_item_id') != f"v_{len(pool)}":
                        st.session_state.auto_q = generate_auto_sentence(item['cn'], item['kr'])
                        st.session_state.last_item_id = f"v_{len(pool)}"
                    q = st.session_state.auto_q
                    if item.get('note'): st.markdown(f'<div class="grammar-rule-box">✨ 文法規則：{item["note"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="flashcard-main"><h2 style="color:#1A1A1A">{q["cn"]}</h2><div class="formula-hint">💡 參考公式：{item["kr"]}</div></div>', unsafe_allow_html=True)
                    u_in = st.text_input("請造句：", key=f"input_{cat}_{len(pool)}")
                    target_ans = q['ans']
                else:
                    st.markdown(f'<div class="flashcard-main"><h2 style="color:#1A1A1A">{item["cn"]}</h2><small>單元：{item["chapter"]}</small></div>', unsafe_allow_html=True)
                    u_in = st.text_input("輸入韓文：", key=f"input_{cat}_{len(pool)}")
                    target_ans = item['kr']

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("提交答案", key=f"btn_{cat}_{len(pool)}"):
                        st.session_state.ex_total += 1
                        if clean_text(u_in) == clean_text(str(target_ans)):
                            st.success("⭕ 太棒了，正確！"); st.session_state.ex_correct += 1; st.balloons()
                        else:
                            st.error(f"❌ 答錯囉！答案是：{target_ans}")
                            st.session_state.wrong_items.append({"cn": item['cn'] if cat != "文法" else q['cn'], "kr": target_ans})
                        play_audio(target_ans)
                with col2:
                    if st.button("下一題 ➡️", key=f"nxt_{cat}_{len(pool)}"):
                        if 'auto_q' in st.session_state: del st.session_state.auto_q
                        pool.pop(0) # 移除已做過的題目，保證不重複
                        st.rerun()
            else:
                st.success(f"✅恭喜！{cat}類別的本輪練習已全部完成！")
                if st.button(f"重啟{cat}練習", key=f"reset_{cat}"):
                    st.session_state.pools[cat] = []; st.rerun()

    st.divider()
    if st.button("⏹️ 結束練習並產出報告"):
        st.session_state.show_report = True; st.rerun()

st.info("宜真加油！💙 照著這個系統練習，10月考照一定沒問題！")
