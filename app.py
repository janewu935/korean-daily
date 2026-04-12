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

# --- 主介
