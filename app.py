import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 設定網頁標題
st.set_page_config(page_title="韓語筆記", page_icon="💙")

# --- 自定義 CSS 樣式 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFF; }
    h1, h2, h3 { color: #007FFF !important; font-weight: bold; }
    
    /* 確保 Logo 圖片不會破裂，設定圓角與陰影感 */
    .logo-img {
        border-radius: 10px;
        background-color: transparent;
    }

    .stInfo {
        background-color: #E6F3FF !important;
        border-left: 5px solid #007FFF !important;
        color: #007FFF !important;
    }

    .stButton>button {
        background-color: #007FFF !important;
        color: white !important;
        border-radius: 12px;
        font-weight: bold;
    }

    /* 下拉選單顏色統整 */
    div[data-baseweb="select"] > div {
        border-color: #007FFF !important;
    }
    span[data-baseweb="tag"] {
        background-color: #007FFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 讀取與發音函數 (保持原本的穩定邏輯)
@st.cache_data(ttl=10)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    try:
        return pd.read_csv(csv_url).dropna(subset=['kr', 'cn'])
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

# --- 主介面 ---

# 💡 這裡我幫你換了一個更穩定的 Logo 網址
logo_url = "https://w7.pngwing.com/pngs/351/347/png-transparent-tws-logo-thumbnail.png"

col_logo, col_title = st.columns([1, 4])
with col_logo:
    # 增加 use_container_width 確保縮放正常
    st.image(logo_url, width=90)
with col_title:
    st.title("韓語筆記")
    st.markdown("<p style='color: #007FFF; font-weight: bold;'>24/7 With Us! 宜真的專屬學習空間 💙</p>", unsafe_allow_html=True)

# --- 應援金句區 ---
tws_quotes = [
    {"kr": "우리 함께라면 뭐든지 할 수 있어.", "cn": "只要我們在一起，什麼都能做到。"},
    {"kr": "누나, 오늘도 정말 고생 많았어요!", "cn": "努那，今天也真的辛苦了！"},
    {"kr": "포기하지 마, 내가 옆에서 응원할게.", "cn": "不要放棄，我會在身邊為妳應援。"}
]

if 'daily_q' not in st.session_state:
    st.session_state.daily_q = random.choice(tws_quotes)

q = st.session_state.daily_q
st.info(f"💌 **來自 TWS 的應援訊息**\n### {q['kr']}\n{q['cn']}")

# --- 複習功能主體 (保持原本設定) ---
df = load_data()
if not df.empty:
    st.subheader("🎯 章節複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("選擇章節：", all_chapters)
    
    st.divider()
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    categories = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            cat = categories[i]
            tmp = df[df['type'] == cat]
            if sel_ch: tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if tmp.empty:
                st.write(f"目前『{cat}』尚無資料")
            else:
                key = f"quiz_{cat}"
                if key not in st.session_state: st.session_state[key] = tmp.sample(1).iloc[0]
                item = st.session_state[key]
                st.write(f"📍 **來源：{item['chapter']}**")
                st.markdown(f"### 請回答：{item['cn']}")

                # 快速/打字模式
                mode = st.radio("模式", ["快速", "打字"], key=f"m_{cat}")
                if mode == "快速":
                    if st.button("看答案並聽發音", key=f"ans_{cat}"):
                        st.success(f"結果：{item['kr']}")
                        play_audio(item['kr'])
                else:
                    user_in = st.text_input("輸入韓文", key=f"in_{cat}")
                    if st.button("檢查", key=f"btn_{cat}"):
                        if user_in.strip() == str(item['kr']).strip():
                            st.balloons()
                            st.success("🎉 Correct! 42的驕傲！")
                        else:
                            st.error(f"❌ 答案是：{item['kr']}")
                        play_audio(item['kr'])

                if st.button("下一題", key=f"next_{cat}"):
                    if key in st.session_state: del st.session_state[key]
                    st.rerun()
