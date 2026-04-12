import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 設定網頁標題
st.set_page_config(page_title="韓語筆記", page_icon="💙")

# 自定義 CSS 樣式：強化對比度與 TWS 氛圍
st.markdown("""
    <style>
    /* 整體背景 */
    .stApp {
        background-color: #F0F8FF;
    }
    /* 標題與文字顏色強化 */
    h1, h2, h3 {
        color: #0047AB !important; /* 深青藍色 */
        font-weight: bold;
    }
    p, span, label {
        color: #1A1A1A !important; /* 近乎黑色，確保閱讀不吃力 */
        font-weight: 500;
    }
    /* 標籤頁字體強化 */
    .stTabs [data-baseweb="tab"] {
        color: #0047AB;
        font-weight: bold;
        font-size: 18px;
    }
    /* 按鈕樣式 */
    .stButton>button {
        background-color: #007FFF;
        color: #FFFFFF !important;
        border-radius: 20px;
        font-weight: bold;
        border: 2px solid #0047AB;
    }
    /* 訊息方框文字 */
    .stInfo {
        background-color: #E6F3FF;
        border-left: 5px solid #007FFF;
        color: #0047AB !important;
    }
    /* 修正輸入框文字顏色 */
    input {
        color: #1A1A1A !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 讀取函數
@st.cache_data(ttl=10)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    try:
        data = pd.read_csv(csv_url)
        return data.dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.error("發音產生失敗")

# --- 主介面 ---
logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/TWS_Logo.svg/512px-TWS_Logo.svg.png" 

col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image(logo_url, width=80)
with col_title:
    st.title("韓語筆記")
    st.markdown("<p style='color: #007FFF; font-weight: bold;'>24/7 With Us! 宜真的專屬學習空間 💙</p>", unsafe_allow_html=True)

# --- 應援金句區 ---
tws_quotes = [
    {"kr": "우리 함께라면 뭐든지 할 수 있어.", "cn": "只要我們在一起，什麼都能做到。"},
    {"kr": "누나, 오늘도 정말 고생 많았어요!", "cn": "努那，今天也真的辛苦了！"},
    {"kr": "포기하지 마, 내가 옆에서 응원할게.", "cn": "不要放棄，我會在身邊為妳應援。"},
    {"kr": "반짝반짝 빛나는 누나를 믿어.", "cn": "相信閃閃發光的妳。"}
]

if 'daily_q' not in st.session_state:
    st.session_state.daily_q = random.choice(tws_quotes)

q = st.session_state.daily_q
st.info(f"💌 **來自 TWS 的應援訊息**\n### {q['kr']}\n{q['cn']}")

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔊 播放"):
        play_audio(q['kr'])
with col2:
    if st.button("換一則訊息"):
        st.session_state.daily_q = random.choice(tws_quotes)
        st.rerun()

st.divider()

# --- 複習邏輯 ---
df = load_data()
if not df.empty:
    st.subheader("🎯 章節複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇章節：", all_chapters)
    
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    categories = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            cat = categories[i]
            tmp = df[df['type'] == cat]
            if sel_ch:
                tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if tmp.empty:
                st.write(f"目前『{cat}』尚無資料")
            else:
                key = f"quiz_{cat}"
                if key not in st.session_state:
                    st.session_state[key] = tmp.sample(1).iloc[0]
                item = st.session_state[key]
                st.write(f"📍 **來源：{item['chapter']}**")
                st.markdown(f"### 請回答：{item['cn']}")

                mode = st.radio("模式", ["快速", "打字"], key=f"m_{cat}")
                if mode == "快速":
                    if st.button("看答案", key=f"ans_{cat}"):
                        st.success(f"結果：{item['kr']}")
                        play_audio(item['kr'])
                        if pd.notna(item['note']):
                            st.info(f"💡 備註：{item['note']}")
                else:
                    user_in = st.text_input("請在此輸入韓文：", key=f"in_{cat}")
                    if st.button("檢查答案", key=f"btn_{cat}"):
                        if user_in.strip() == str(item['kr']).strip():
                            st.balloons()
                            st.success("🎉 Correct! 42的驕傲！")
                        else:
                            st.error(f"❌ 錯誤！答案是：{item['kr']}")
                        play_audio(item['kr'])

                if st.button("下一題", key=f"next_{cat}"):
                    if key in st.session_state:
                        del st.session_state[key]
                    st.rerun()

    st.divider()
    st.markdown(f"**[🔗 點我打開試算表新增單字](https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit)**")

else:
    st.warning("試算表讀取不到資料，請檢查內容！")
