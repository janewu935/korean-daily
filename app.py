import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
from datetime import date
from gtts import gTTS
import io
import pandas as pd

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 連接 Google Sheets ---
# 請確保你的 Secrets 已經設定好，或者直接把網址寫死在下面
url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 這裡就是讀取資料的地方
    df = conn.read(spreadsheet=url, usecols=[0, 1, 2], ttl="0") 
    df = df.dropna(how="all")
    st.sidebar.success("✅ 已連結 Google Sheets")
    st.sidebar.write(f"目前單字數：{len(df)}")
except Exception as e:
    st.sidebar.error(f"❌ 連線失敗：{e}")
    df = pd.DataFrame(columns=["date", "kr", "cn"])

# --- 2. 語音功能 ---
def play_audio(text):
    tts = gTTS(text=text, lang='ko')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp)

# --- 3. 介面與功能 ---
st.title("🇰🇷 宜真的韓語學習基地")

# 區塊一：新增單字
with st.expander("➕ 手機輸入新單字", expanded=True):
    with st.form("add_form", clear_on_submit=True):
        new_kr = st.text_input("輸入韓文單字")
        new_cn = st.text_input("輸入中文意思")
        if st.form_submit_button("永久存入試算表"):
            if new_kr and new_cn:
                # 建立新資料列
                new_data = pd.DataFrame([{"date": str(date.today()), "kr": new_kr, "cn": new_cn}])
                # 合併舊資料與新資料
                updated_df = pd.concat([df, new_data], ignore_index=True)
                # 寫回 Google Sheets
                conn.update(spreadsheet=url, data=updated_df)
                st.success(f"✅ 成功寫入：{new_kr}")
                st.cache_data.clear() # 清除快取，強制下次讀取最新資料
                st.rerun()

# 區塊二：複習與測驗
st.divider()
if not df.empty and len(df) > 0:
    test_item = df.sample(1).iloc[0]
    st.subheader("🧠 隨機複習")
    st.info(f"這是什麼意思？ **{test_item['kr']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 聽發音"):
            play_audio(test_item['kr'])
    with col2:
        if st.button("👀 看答案"):
            st.write(f"💡 **{test_item['cn']}**")
    
    if st.button("換下一個"):
        st.rerun()
else:
    st.write("目前試算表是空的，請先輸入單字！")
