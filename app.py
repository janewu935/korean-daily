import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# 設定
st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- 自定義 CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    .main-title { color: #007FFF !important; font-size: 38px; font-weight: 800; text-align: center; }
    .stInfo { background-color: #E6F3FF !important; border-left: 5px solid #007FFF !important; color: #007FFF !important; }
    .stButton>button { background-color: #007FFF !important; color: white !important; border-radius: 12px; font-weight: bold; }
    p, span, label { color: #1A1A1A !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 1. 讀取與發音
@st.cache_data(ttl=5) # 縮短快取時間，讓 Excel 更新更快反映
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url)
        # 統一欄位名稱，避免 Excel 標題打錯
        df.columns = [c.strip().lower() for c in df.columns]
        return df.dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.error("發音失敗")

def clean_text(text):
    return re.sub(r'[^\w\s]', '', str(text)).strip()

# --- 主介面 ---
st.markdown('<p class="main-title">💙 韓語筆記 💙</p>', unsafe_allow_html=True)

df = load_data()

# 2. 每日翻譯挑戰邏輯 (從 Excel 動態讀取)
st.subheader("✍️ 今日文法挑戰：互動翻譯")

# 建立題庫：優先抓 Excel 裡 type 是 '文法' 或 '每日句' 的資料
if not df.empty:
    quiz_pool = df[df['type'].isin(['文法', '每日句'])].to_dict('records')
else:
    quiz_pool = []

# 如果 Excel 沒資料，就用備用題庫（避免網頁壞掉）
if not quiz_pool:
    quiz_pool = [{"chapter": "L1", "cn": "我是台灣人。", "kr": "저는 대만 사람이에요."}]

# 初始化狀態
if 'daily_quiz' not in st.session_state or st.session_state.get('refresh_quiz', False):
    st.session_state.daily_quiz = random.choice(quiz_pool)
    st.session_state.refresh_quiz = False

if 'daily_input_id' not in st.session_state:
    st.session_state.daily_input_id = 0

dq = st.session_state.daily_quiz

with st.container():
    st.info(f"💡 **來自第 {dq['chapter']} 章的挑戰：**\n### 「 {dq['cn']} 」")
    
    # 關鍵：使用動態 Key 確保清空
    user_trans = st.text_input("輸入韓文翻譯：", key=f"daily_input_{st.session_state.daily_input_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("驗證我的翻譯"):
            if not user_trans:
                st.warning("寫點東西再驗證吧！")
            else:
                if clean_text(user_trans) == clean_text(dq['kr']):
                    st.balloons()
                    st.success("🎉 太強了！完全正確。")
                    play_audio(dq['kr'])
                else:
                    st.error("⚠️ 這裡有 Bug 喔！")
                    st.write(f"**正確解答：** {dq['kr']}")
                    play_audio(dq['kr'])
    
    with col2:
        if st.button("換一題挑戰"):
            st.session_state.refresh_quiz = True
            st.session_state.daily_input_id += 1
            st.rerun()

st.divider()

# --- 3. 章節題庫複習 (原本的功能) ---
if not df.empty:
    st.subheader("🎯 分類題庫複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇複習章節：", all_chapters)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    cats = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            target_cat = cats[i]
            tmp = df[df['type'] == target_cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if not tmp.empty:
                tab_id_key = f"input_id_{target_cat}"
                if tab_id_key not in st.session_state: st.session_state[tab_id_key] = 0
                
                q_key = f"quiz_item_{target_cat}"
                if q_key not in st.session_state: st.session_state[q_key] = tmp.sample(1).iloc[0]
                
                item = st.session_state[q_key]
                st.write(f"📍 **章節：{item['chapter']}**")
                st.markdown(f"### 翻譯題目：{item['cn']}")

                u_in = st.text_input("在此輸入回答", key=f"input_{target_cat}_{st.session_state[tab_id_key]}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("檢查", key=f"btn_{target_cat}"):
                        if clean_text(u_in) == clean_text(str(item['kr'])):
                            st.balloons(); st.success("正確！")
                        else:
                            st.error(f"正確答案：{item['kr']}")
                        play_audio(item['kr'])
                with c2:
                    if st.button("下一題", key=f"next_{target_cat}"):
                        if q_key in st.session_state: del st.session_state[q_key]
                        st.session_state[tab_id_key] += 1
                        st.rerun()
else:
    st.warning("Excel 裡還沒有資料喔，快去新增吧！")
