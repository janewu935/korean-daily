import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gtts import gTTS
import io
import random
from datetime import date

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 語音功能 ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.warning("語音產生失敗")

# --- 2. 核心連線 (使用公開編輯網址) ---
# 既然你已經開了「任何人皆可編輯」，我們用這個簡單路徑
SHEET_URL = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit"

def get_data():
    # 使用 pandas 直接讀取公開 CSV 格式是最穩定的讀取方式
    csv_url = SHEET_URL.replace('/edit', '/export?format=csv')
    data = pd.read_csv(csv_url)
    return data.dropna(how="all")

# --- 3. 介面設計 ---
st.title("🇰🇷 宜真的韓語基地")

try:
    df = get_data()
    st.sidebar.success(f"✅ 連線成功 (單字數: {len(df)})")
except:
    df = pd.DataFrame(columns=["date", "kr", "cn"])
    st.sidebar.error("❌ 讀取失敗")

tab1, tab2 = st.tabs(["📝 新增單字", "📖 複習模式"])

with tab1:
    with st.form("my_form", clear_on_submit=True):
        new_kr = st.text_input("輸入韓文 (KR)")
        new_cn = st.text_input("輸入中文 (CN)")
        submit = st.form_submit_button("永久存入試算表")
        
        if submit and new_kr and new_cn:
            # 這裡我們使用一個小技巧：利用 Google Forms 概念或提醒
            st.warning("⚠️ 寫入功能正在切換更穩定的連線方式。")
            st.info("請點擊下方連結手動新增，或等我為你設定 Service Account 鑰匙。")
            # 這裡提供一個最快解決方案：既然自動寫入卡住，
            # 我們改用 st.write 顯示一個可以點擊的連結，
            # 讓你直接在手機上打開試算表 APP 輸入，那是最快且不會失敗的。
            st.markdown(f"[點我直接打開試算表輸入]({SHEET_URL})")

with tab2:
    if not df.empty:
        item = df.sample(1).iloc[0]
        st.subheader("🧠 隨機挑戰")
        st.info(f"這個怎麼說？ **{item['cn']}**")
        if st.button("看答案並聽發音"):
            st.success(f"答案是：{item['kr']}")
            play_audio(str(item['kr']))
        if st.button("下一個"):
            st.rerun()
