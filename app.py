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

# 1. 內建題庫產生器 (針對大家的韓國語第一冊)
def generate_random_quiz():
    database = [
        {"ch": "L1", "cn": "我是台灣人。", "kr": "저는 대만 사람이에요."},
        {"ch": "L1", "cn": "我是工程師。", "kr": "저는 엔지니어예요."},
        {"ch": "L2", "cn": "這不是手機。", "kr": "이것은 휴대폰이 아니에요."},
        {"ch": "L2", "cn": "那是筆記本嗎？", "kr": "저것은 공책이에요?"},
        {"ch": "L3", "cn": "弟弟在教室裡。", "kr": "남동생이 교실에 있어요."},
        {"ch": "L3", "cn": "椅子上面有貓。", "kr": "의자 위에 고양이가 있어요."},
        {"ch": "L4", "cn": "今天去銀行。", "kr": "오늘은 은행에 가요."},
        {"ch": "L4", "cn": "爸爸在睡覺。", "kr": "아버지가 자요."},
        {"ch": "L5", "cn": "昨天見了朋友。", "kr": "어제 친구를 만났어요."},
        {"ch": "L5", "cn": "上週末做了運動。", "kr": "지난 주말에 운동을 했어요."},
        {"ch": "L6", "cn": "我喝咖啡和水。", "kr": "커피하고 물을 마셔요."},
        {"ch": "L6", "cn": "買了麵包跟牛奶。", "kr": "빵이랑 우유를 샀어요."},
        {"ch": "L7", "cn": "從家裡到公司。", "kr": "집에서 회사까지."},
        {"ch": "L7", "cn": "去百貨公司買東西。", "kr": "백화점에 쇼핑하러 가요."},
        {"ch": "L8", "cn": "現在兩點三十分。", "kr": "지금 두 시 삼십 분이에요."},
        {"ch": "L8", "cn": "星期三有韓語課。", "kr": "수요일에 한국어 수업이 있어요."},
        {"ch": "L9", "cn": "天氣雖然冷，但很好。", "kr": "날씨가 춥지만 좋아요."},
        {"ch": "L10", "cn": "請給我三顆蘋果。", "kr": "사과 세 개 주세요."},
        {"ch": "L11", "cn": "我想看電影。", "kr": "영화 보고 싶어요."},
        {"ch": "L12", "cn": "這件衣服很漂亮。", "kr": "이 옷이 아주 예뻐요."}
    ]
    return random.choice(database)

# 2. 核心功能函數
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

# 3. 隨機翻譯挑戰區
st.subheader("✍️ 大家的韓國語 L1-L12 隨機挑戰")

if 'daily_quiz' not in st.session_state:
    st.session_state.daily_quiz = generate_random_quiz()
if 'daily_input_id' not in st.session_state:
    st.session_state.daily_input_id = 0

dq = st.session_state.daily_quiz

with st.container():
    st.info(f"💡 **翻譯題目：** 「 {dq['cn']} 」")
    
    # 動態 Key 確保清空
    user_trans = st.text_input("輸入韓文：", key=f"daily_input_{st.session_state.daily_input_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("驗證答案"):
            if not user_trans:
                st.warning("寫點東西吧！")
            else:
                if clean_text(user_trans) == clean_text(dq['kr']):
                    st.balloons()
                    st.success("🎉 正確！妳好棒！")
                    play_audio(dq['kr'])
                else:
                    st.error("⚠️ 發現 Bug！")
                    st.write(f"**正確解答：** {dq['kr']}")
                    play_audio(dq['kr'])
    
    with col2:
        if st.button("換下一題挑戰"):
            st.session_state.daily_quiz = generate_random_quiz()
            st.session_state.daily_input_id += 1
            st.rerun()

st.divider()

# --- 4. 原有的 Excel 複習 (妳有空再輸入單字就好) ---
@st.cache_data(ttl=5)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/edit?usp=sharing"
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
    try:
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df.dropna(subset=['kr', 'cn'])
    except:
        return pd.DataFrame()

df = load_data()
if not df.empty:
    st.subheader("🎯 我的 Excel 題庫複習")
    all_chapters = sorted(df['chapter'].astype(str).unique().tolist())
    sel_ch = st.multiselect("篩選章節：", all_chapters)
    
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
                st.markdown(f"### {item['cn']}")
                u_in = st.text_input("輸入回答", key=f"input_{target_cat}_{st.session_state[tab_id_key]}")
                if st.button("檢查", key=f"btn_{target_cat}"):
                    if clean_text(u_in) == clean_text(str(item['kr'])):
                        st.balloons(); st.success("正確！")
                    else:
                        st.error(f"正確答案：{item['kr']}")
                    play_audio(item['kr'])
                if st.button("下一題", key=f"next_{target_cat}"):
                    if q_key in st.session_state: del st.session_state[q_key]
                    st.session_state[tab_id_key] += 1
                    st.rerun()
