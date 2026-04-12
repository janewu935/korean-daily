import streamlit as st
import random

st.set_page_config(page_title="韓語每日一句", page_icon="🇰🇷")

# 你的韓語資料庫
korean_data = [
    {"kr": "포기하지 마세요. 꿈은 이루어질 거예요.", "cn": "請不要放棄，夢想會實現的。"},
    {"kr": "어제보다 더 나은 오늘", "cn": "比昨天更好的今天"},
    {"kr": "할 수 있어요! 화이팅!", "cn": "你可以的！加油！"}
]

st.title("🇰🇷 宜真的韓語小站")
st.subheader("目標：TOPIK II 3級合格")

if st.button('換一句話'):
    q = random.choice(korean_data)
    st.info(f"### {q['kr']}")
    st.write(f"💡 翻譯：{q['cn']}")
else:
    st.write("點擊按鈕獲取今日動力！")
