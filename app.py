import streamlit as st
import random
from datetime import date
from gtts import gTTS
import io

st.set_page_config(page_title="宜真韓語全功能站", page_icon="🇰🇷")

# --- 1. 每日一句資料庫 ---
quotes = [
    {"kr": "오늘도 화이팅! 할 수 있어요.", "cn": "今天也要加油！你可以的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"},
    {"kr": "포기하지 마세요, 꿈은 이루어질 거예요.", "cn": "請不要放棄，夢想會實現的。"}
]

# --- 2. 語音播放函數 ---
def play_audio(text):
    tts = gTTS(text=text, lang='ko')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp)

# --- 介面設計 ---
st.title("🇰🇷 宜真的韓語學習基地")

# 區塊一：每日一句 (保留原功能)
with st.expander("✨ 今日動力：每日一句", expanded=True):
    if 'daily_q' not in st.session_state:
        st.session_state.daily_q = random.choice(quotes)
    
    q = st.session_state.daily_q
    st.info(f"### {q['kr']}\n{q['cn']}")
    if st.button("🔊 聽句子發音"):
        play_audio(q['kr'])
    if st.button("換一句話"):
        st.session_state.daily_q = random.choice(quotes)
        st.rerun()

st.divider()

# 區塊二：互動單字本
if 'my_vocab' not in st.session_state:
    st.session_state.my_vocab = []

tab1, tab2 = st.tabs(["➕ 新增單字", "🧠 複習模式"])

with tab1:
    st.subheader("手機隨手記")
    with st.form("vocab_form", clear_on_submit=True):
        kr_word = st.text_input("輸入韓文單字")
        cn_mean = st.text_input("輸入中文意思")
        if st.form_submit_button("存入單字本"):
            if kr_word and cn_mean:
                st.session_state.my_vocab.append({"kr": kr_word, "cn": cn_mean})
                st.success(f"已記錄：{kr_word}")

    st.write("目前單字量：", len(st.session_state.my_vocab))
    if st.session_state.my_vocab:
        st.write(st.session_state.my_vocab[-5:]) # 顯示最後五個

with tab2:
    st.subheader("測驗與複習")
    if not st.session_state.my_vocab:
        st.write("單字本空空的，先去新增吧！")
    else:
        # 隨機抽題
        if 'test_idx' not in st.session_state:
            st.session_state.test_idx = 0
            
        current = st.session_state.my_vocab[st.session_state.test_idx]
        
        mode = st.radio("測驗方式", ["翻譯挑戰", "Go/No Go"])
        
        if mode == "翻譯挑戰":
            st.warning(f"請翻譯：{current['cn']}")
            ans = st.text_input("輸入韓文答案")
            if st.button("檢查"):
                if ans.strip() == current['kr'].strip():
                    st.success("✅ 正確！")
                    play_audio(current['kr'])
                else:
                    st.error(f"❌ 錯誤！答案是：{current['kr']}")
        else:
            st.info(f"這個字記得嗎？ {current['kr']}")
            if st.button("🔊 聽發音"):
                play_audio(current['kr'])
            if st.button("顯示中文答案"):
                st.write(f"解釋：{current['cn']}")
                
        if st.button("換下一個"):
            st.session_state.test_idx = random.randint(0, len(st.session_state.my_vocab)-1)
            st.rerun()

st.divider()
st.caption("目標：10月 TOPIK II 3級合格！加油！")
