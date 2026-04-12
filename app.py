import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 設定與讀取 ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit"
CSV_URL = SHEET_URL.replace('/edit', '/export?format=csv')

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp)
    except:
        st.warning("語音產生失敗")

@st.cache_data(ttl=30) # 縮短快取時間至 30 秒，方便你在試算表改完後快速看到結果
def load_data():
    data = pd.read_csv(CSV_URL)
    # 確保抓到正確的欄位，並過濾掉空行
    return data.dropna(subset=['kr', 'cn'])

# --- 2. 每日一句庫 ---
quotes = [
    {"kr": "오늘도 화이팅! 할 수 있어요.", "cn": "今天也要加油！你可以的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"},
    {"kr": "꿈을 향해 한 걸음씩.", "cn": "朝著夢想一步步前進。"}
]

# --- 3. 介面設計 ---
st.title("🇰🇷 宜真的韓語基地")

# 每日一句
with st.container():
    if 'daily_q' not in st.session_state:
        st.session_state.daily_q = random.choice(quotes)
    q = st.session_state.daily_q
    st.info(f"✨ **今日動力**\n### {q['kr']}\n{q['cn']}")
    if st.button("🔊 播放金句語音"):
        play_audio(q['kr'])

st.divider()

# 讀取資料
try:
    df = load_data()
    
    # 側邊欄
    st.sidebar.title("🛠️ 學習管理")
    st.sidebar.markdown(f"[🔗 點我打開試算表]({SHEET_URL})")
    st.sidebar.write("---")
    st.sidebar.caption("目前的標題列應為：\nchapter, kr, cn, type, note")

    # 分頁功能
    tab1, tab2, tab3 = st.tabs(["📖 單字複習", "📝 文法練習", "📢 發音規則"])

    def QuizSection(category):
        # 篩選類別
        target_df = df[df['type'] == category]
        
        if target_df.empty:
            st.write(f"目前『{category}』還沒有資料喔！")
        else:
            # 隨機抽題
            item = target_df.sample(1).iloc[0]
            
            # 顯示章節資訊
            st.caption(f"📍 章節：{item['chapter']}")
            st.subheader(f"{category}挑戰")
            st.warning(f"請翻譯：**{item['cn']}**")
            
            with st.expander("點我看答案與聽發音"):
                st.success(f"結果：{item['kr']}")
                play_audio(str(item['kr']))
                if pd.notna(item['note']):
                    st.info(f"💡 備註：{item['note']}")
            
            if st.button(f"換下一個 {category}", key=category):
                st.rerun()

    with tab1:
        QuizSection("單字")
    with tab2:
        QuizSection("文法")
    with tab3:
        QuizSection("發音")

except Exception as e:
    st.error("讀取失敗，請確認試算表格式與權限。")
    st.info(f"錯誤訊息：{e}")
