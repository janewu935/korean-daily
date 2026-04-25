import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io
import re

# --- 1. 頁面設定與淡雅色系 CSS ---
st.set_page_config(page_title="韓語全能練習", page_icon="🌷")

st.markdown("""
    <style>
    .stApp { background-color: #FDFCF8; } 
    h1, h2, h3, p, span, label, div { color: #5C5C5C !important; }
    .section-title {
        font-size: 22px; font-weight: 800; color: #7B9095 !important; 
        border-bottom: 2px solid #EAE7E0; padding-bottom: 10px; margin-bottom: 20px; margin-top: 20px;
    }
    .daily-header { font-size: 24px; font-weight: 700; color: #444444; margin-bottom: -15px; }
    .box-label { color: #8EB4AC; font-weight: 700; margin-bottom: 2px; }
    .flashcard-box {
        background-color: #FFFFFF; border: 1px solid #EAE7E0; border-radius: 12px;
        padding: 40px 20px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
        margin-bottom: 20px; min-height: 180px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }
    .flashcard-box h2 { color: #3A4042 !important; font-weight: 700; margin-bottom: 10px; }
    .hint-tag {
        background-color: #F4F1EA; color: #8C8C8C !important; padding: 6px 15px;
        border-radius: 20px; font-size: 0.9em; display: inline-block; margin-top: 15px;
    }
    .rule-tag { color: #93A8AC !important; font-size: 1.1em; margin-bottom: 10px; font-weight: bold; }
    .answer-tag { color: #8EB4AC !important; font-size: 1.2em; font-weight: bold; margin-top: 15px; }
    .progress-text { color: #7B9095; font-weight: bold; margin-bottom: 5px; text-align: right; font-size: 1.1em; }
    .stButton>button {
        background-color: #A3C4BC !important; color: #FFFFFF !important; border-radius: 8px;
        font-weight: 600; height: 42px; border: none; box-shadow: 1px 1px 5px rgba(163,196,188,0.3);
        transition: background-color 0.3s ease; width: 100%;
    }
    .stButton>button:hover { background-color: #8EB4AC !important; }
    .report-card { background: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #EBBAB9; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
state_keys = {
    'ex_total': 0, 'ex_correct': 0, 'show_report': False, 
    'wrong_items': [], 'pools': {"單字": [], "文法": []},
    'pool_sizes': {"單字": 0, "文法": 0}, 
    'sel_ch': ["ALL 全部單元"], 'dq_idx': 0
}
for key, value in state_keys.items():
    if key not in st.session_state: st.session_state[key] = value

# --- 2. 輔助函數 ---
def clean_text(text): return re.sub(r'[^\w\s]', '', str(text)).replace(" ", "").strip()
def play_audio(text):
    try: tts = gTTS(text=str(text), lang='ko'); fp = io.BytesIO(); tts.write_to_fp(fp); st.audio(fp)
    except: pass

@st.cache_data(ttl=5)
def load_all_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/export?format=xlsx"
    try: 
        xls = pd.read_excel(url, sheet_name=None, engine='openpyxl')
        chapter_dfs = []
        daily_sentences = []
        
        for sheet_name, df in xls.items():
            df = df.fillna("")
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # 🚀 判斷是否為「每日一句」工作表
            if sheet_name.strip() == "每日一句":
                if 'cn' in df.columns and 'kr' in df.columns:
                    daily_sentences = df[['cn', 'kr']].to_dict('records')
            
            # 🚀 判斷是否為「單元/章節」工作表
            elif 'cn' in df.columns and 'kr' in df.columns and 'type' in df.columns:
                df['chapter'] = str(sheet_name).strip().upper()
                chapter_dfs.append(df)
        
        full_df = pd.concat(chapter_dfs, ignore_index=True) if chapter_dfs else pd.DataFrame()
        return full_df, daily_sentences
    except:
        return pd.DataFrame(), []

# --- 3. 介面呈現 ---

# 讀取資料
df, excel_dq_list = load_all_data()

# 📊 報告頁面 (邏輯維持不變)
if st.session_state.show_report:
    st.markdown('<div class="section-title">📊 練習報告結算</div>', unsafe_allow_html=True)
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.metric("整體準確率", f"{acc:.1f}%", f"{st.session_state.ex_correct} / {st.session_state.ex_total} 題")
    if st.session_state.wrong_items:
        st.write("📝 錯題清單：")
        for w in st.session_state.wrong_items:
            st.markdown(f'<div class="report-card"><b>題目：</b>{w["cn"]}<br><b>正確解答：</b>{w["ans"]}</div>', unsafe_allow_html=True)
    if st.button("🔄 返回首頁開啟新練習"):
        for k in ['ex_total', 'ex_correct', 'wrong_items', 'show_report']: st.session_state[k] = 0
        st.session_state.pools = {"單字": [], "文法": []}
        st.session_state.pool_sizes = {"單字": 0, "文法": 0}
        st.rerun()
    st.stop()

# ================= 區塊 1：每日一句 (優先讀取 Excel) =================
st.markdown('<div class="section-title">每日一句韓語</div>', unsafe_allow_html=True)

# 如果 Excel 沒資料，就用程式碼內的備案
dq_source = excel_dq_list if excel_dq_list else [
    {"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"},
    {"cn": "姊姊正在坐火車。", "kr": "언니는 기차를 타고 있어요"}
]
dq = dq_source[st.session_state.dq_idx % len(dq_source)]

st.write(f"**韓語翻譯：** {dq['cn']}")
u_dq = st.text_input("答案：", key="dq_in", label_visibility="collapsed", placeholder="在此輸入您的翻譯...")

col_dq1, col_dq2 = st.columns(2)
with col_dq1:
    if st.button("檢查", key="chk_dq"):
        if clean_text(u_dq) == clean_text(dq['kr']): st.success("⭕ 正確！"); st.balloons()
        else: st.error(f"❌ 錯誤！正確解答：{dq['kr']}"); play_audio(dq['kr'])
with col_dq2:
    if st.button("下一題", key="nxt_dq"): st.session_state.dq_idx += 1; st.rerun()

# ================= 區塊 2：單元複習/考試 =================
st.markdown('<div class="section-title">單元複習 / 考試</div>', unsafe_allow_html=True)

exam_mode = st.radio("模式選擇：", ["複習", "考試"], horizontal=True, key="exam_mode_radio")

if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        elif not new: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": []}
        st.session_state.pool_sizes = {"單字": 0, "文法": 0}
    
    st.multiselect("選擇單元：", ["ALL 全部單元"]+all_ch, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
    final_ch = all_ch if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch

    tabs = st.tabs(["📖 單字", "📝 文法造句"])
    cat_list = ["單字", "文法"]
    
    for i, tab in enumerate(tabs):
        with tab:
            cat = cat_list[i]
            if not st.session_state.pools[cat] and st.session_state.pool_sizes[cat] == 0:
                curr_df = df[(df['type'] == cat) & (df['chapter'].astype(str).isin(final_ch))]
                if not curr_df.empty:
                    pool_list = curr_df.to_dict('records')
                    random.shuffle(pool_list)
                    st.session_state.pools[cat] = pool_list
                    st.session_state.pool_sizes[cat] = len(pool_list)
            
            p = st.session_state.pools[cat]
            if p:
                total_q = max(len(p), st.session_state.pool_sizes[cat])
                st.session_state.pool_sizes[cat] = total_q
                completed_q = total_q - len(p)
                st.markdown(f'<div class="progress-text">剩餘：{len(p)} / 已完成：{completed_q}</div>', unsafe_allow_html=True)
                
                item = p[0]
                html_card = f'<div class="flashcard-box"><h2>{item["cn"] if cat=="單字" else item["kr"]}</h2>'
                if cat == "文法":
                    html_card += f'<div class="rule-tag">{item["cn"]}</div>'
                if exam_mode == "複習" and item.get('note'): 
                    html_card += f'<div class="hint-tag">💡 備註：{item["note"]}</div>'
                if cat == "單字" and exam_mode == "複習":
                    html_card += f'<div class="answer-tag">✅ 解答：{item["kr"]}</div>'
                html_card += '</div>'
                st.markdown(html_card, unsafe_allow_html=True)

                st.markdown('<p class="box-label">造句 / 答案：</p>', unsafe_allow_html=True)
                u_in = st.text_input("", key=f"in_{cat}_{len(p)}", label_visibility="collapsed", placeholder="請輸入韓文...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("檢查", key=f"btn_{cat}_{len(p)}"):
                        if cat == "文法":
                            st.session_state.ex_total += 1
                            st.session_state.ex_correct += 1
                            st.success("⭕ 造句完成！請點擊右上方複製貼給 Gemini 批改。")
                            copy_text = f"Gemini 請幫我批改這句韓文！\n🎯 目標文法：{item['kr']} ({item['cn']})\n✍️ 我的造句：{u_in}"
                            st.code(copy_text, language="markdown")
                        else:
                            st.session_state.ex_total += 1
                            if clean_text(u_in) == clean_text(str(item['kr'])):
                                st.success(f"⭕ 正確解答：{item['kr']}"); st.session_state.ex_correct += 1; st.balloons()
                            else:
                                st.error(f"❌ 錯誤！正確解答：{item['kr']}")
                                st.session_state.wrong_items.append({"cn": item['cn'], "ans": item['kr']})
                            play_audio(item['kr'])
                with col2:
                    if st.button("下一題", key=f"nxt_{cat}_{len(p)}"):
                        p.pop(0); st.rerun()
            else:
                st.write("✅ 該單元已練習完畢。")

    st.write("") 
    if st.button("結束 (同步產出複習報告)", key="end_btn"): st.session_state.show_report = True; st.rerun()
