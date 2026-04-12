import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# 設定
st.set_page_config(page_title="宜真韓語基地", page_icon="🇰🇷")

# 1. 讀取函數
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
    try:
        data = pd.read_csv(csv_url)
        return data.dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

# 2. 發音函數
def play_audio(text):
    try:
        tts = gTTS(text=str(text), lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.error("發音失敗")

# --- 主介面 ---
st.title("🇰🇷 宜真的韓語基地")

# 每日金句 (固定一組)
st.info("✨ 今日動力：오늘도 화이팅! (今天也要加油！)")

df = load_data()

if not df.empty:
    # 側邊欄
    st.sidebar.title("🎯 篩選章節")
    chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.sidebar.multiselect("選擇章節", chapters)
    st.sidebar.markdown("[🔗 打開試算表](https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit)")

    # 分頁
    tabs = st.tabs(["📖 單字", "📝 文法", "📢 發音"])
    categories = ["單字", "文法", "發音"]

    for i, tab in enumerate(tabs):
        with tab:
            cat = categories[i]
            # 篩選資料
            tmp = df[df['type'] == cat]
            if sel_ch:
                tmp = tmp[tmp['chapter'].astype(str).isin(sel_ch)]
            
            if tmp.empty:
                st.write("目前無資料")
            else:
                # 題目邏輯
                key = f"quiz_{cat}"
                if key not in st.session_state:
                    st.session_state[key] = tmp.sample(1).iloc[0]
                
                item = st.session_state[key]
                st.caption(f"章節：{item['chapter']}")
                st.subheader(f"請回答：{item['cn']}")

                mode = st.radio("模式", ["快速", "打字"], key=f"m_{cat}")
                
                if mode == "快速":
                    if st.button("看答案", key=f"ans_{cat}"):
                        st.success(item['kr'])
                        play_audio(item['kr'])
                else:
                    user_in = st.text_input("輸入韓文", key=f"in_{cat}")
                    if st.button("檢查", key=f"btn_{cat}"):
                        if user_in.strip() == str(item['kr']).strip():
                            st.balloons()
                            st.success("正確！")
                        else:
                            st.error(f"錯誤，答案是：{item['kr']}")
                        play_audio(item['kr'])

                if st.button("下一題", key=f"next_{cat}"):
                    del st.session_state[key]
                    st.rerun()
else:
    st.warning("試算表讀取不到資料，請檢查標題列是否為 chapter, kr, cn, type, note")
