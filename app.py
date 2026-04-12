import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random
from datetime import date
from gtts import gTTS
import io
import pandas as pd

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 連接設定 ---
# 使用你提供的公開分享網址
url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"

def get_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 確保每次都抓最新單字
    return conn, conn.read(spreadsheet=url, ttl=0).dropna(how="all")

try:
    conn, df = get_data()
    st.sidebar.success(f"✅ 連線成功！目前有 {len(df)} 個單字")
except Exception as e:
    st.sidebar.error("❌ 連線異常")
    st.sidebar.info("請檢查試算表是否已設為「編輯者」權限")
    df = pd.DataFrame(columns=["date", "kr", "cn"])

# --- 2. 語音功能 ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.warning("暫時無法產生語音")

# --- 3. 介面設計 ---
st.title("🇰🇷 宜真的韓語基地")

tab1, tab2 = st.tabs(["📝 新增單字", "📖 複習模式"])

with tab1:
    st.subheader("手機隨手記")
    with st.form("my_form", clear_on_submit=True):
        new_kr = st.text_input("輸入韓文 (KR)")
        new_cn = st.text_input("輸入中文 (CN)")
        submit = st.form_submit_button("永久存入試算表")
        
        if submit:
            if new_kr and new_cn:
                # 準備新資料
                new_row = pd.DataFrame([{"date": str(date.today()), "kr": new_kr.strip(), "cn": new_cn.strip()}])
                # 合併舊資料
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                try:
                    # 執行寫入
                    conn.update(spreadsheet=url, data=updated_df)
                    st.success(f"✅ 成功存入：{new_kr}")
                    # 強制刷新
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error("寫入失敗！")
                    st.info("請確認 Google 試算表的共用權限已設為「編輯者」。")
            else:
                st.warning("韓文和中文都要填喔！")

with tab2:
    if not df.empty and len(df) > 0:
        # 如果第一列是標題，隨機挑選時排除
        test_df = df[df['kr'] != 'kr'] 
        if not test_df.empty:
            item = test_df.sample(1).iloc[0]
            st.subheader("測驗挑戰")
            st.info(f"這個怎麼說？ **{item['cn']}**")
            
            if st.button("看答案並聽發音"):
                st.success(f"答案是：{item['kr']}")
                play_audio(item['kr'])
            
            if st.button("下一個"):
                st.rerun()
        else:
            st.write("單字本還沒有有效內容。")
    else:
        st.write("目前單字本是空的，快去新增吧！")
