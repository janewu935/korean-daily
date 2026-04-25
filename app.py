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
    /* 全局背景與字體顏色 (莫蘭迪淡色系) */
    .stApp { background-color: #FDFCF8; } 
    h1, h2, h3, p, span, label, div { color: #5C5C5C !important; }
    
    /* 區塊標題 */
    .section-title {
        font-size: 22px; font-weight: 800; color: #7B9095 !important; 
        border-bottom: 2px solid #EAE7E0; padding-bottom: 10px; margin-bottom: 20px; margin-top: 20px;
    }
    
    /* 每日挑戰置頂樣式 */
    .daily-header { font-size: 24px; font-weight: 700; color: #444444; margin-bottom: -15px; }
    
    /* 輸入/結果區域標籤 */
    .box-label { color: #a3d2e2; font-weight: 700; margin-bottom: 2px; }
    
    /* 大卡片設計 */
    .flashcard-box {
        background-color: #FFFFFF; border: 1px solid #EAE7E0; border-radius: 12px;
        padding: 40px 20px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
        margin-bottom: 20px; min-height: 180px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }
    .flashcard-box h2 { color: #3A4042 !important; font-weight: 700; margin-bottom: 10px; }
    
    /* 文法與提示標籤 */
    .hint-tag {
        background-color: #F4F1EA; color: #8C8C8C !important; padding: 6px 15px;
        border-radius: 20px; font-size: 0.9em; display: inline-block; margin-top: 15px;
    }
    .rule-tag { color: #93A8AC !important; font-size: 1.1em; margin-bottom: 10px; font-weight: bold; }
    
    /* 進度題數顯示 */
    .progress-text { color: #7B9095; font-weight: bold; margin-bottom: 5px; text-align: right; font-size: 1.1em; }
    
    /* 按鈕樣式 (淡雅藍綠色) */
    .stButton>button {
        background-color: #A3C4BC !important; color: #FFFFFF !important; border-radius: 8px;
        font-weight: 600; height: 42px; border: none; box-shadow: 1px 1px 5px rgba(163,196,188,0.3);
        transition: background-color 0.3s ease; width: 100%;
    }
    .stButton>button:hover { background-color: #8EB4AC !important; }
    
    /* 報告區塊 */
    .report-card { background: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #EBBAB9; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
state_keys = {
    'ex_total': 0, 'ex_correct': 0, 'show_report': False, 
    'wrong_items': [], 'pools': {"單字": [], "文法": [], "發音": []},
    'pool_sizes': {"單字": 0, "文法": 0, "發音": 0}, 
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
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1dcEYmAqIYng4YFFAT98Uxy_NXskGQaAAidCzzORuJag/export?format=csv&gid=0"
    try: df = pd.read_csv(url).fillna(""); df.columns = [c.strip().lower() for c in df.columns]; return df
    except: return pd.DataFrame()

# --- 3. 介面呈現 ---

# 📊 報告頁面
if st.session_state.show_report:
    st.markdown('<div class="section-title">📊 練習報告結算</div>', unsafe_allow_html=True)
    acc = (st.session_state.ex_correct / st.session_state.ex_total * 100) if st.session_state.ex_total > 0 else 0
    st.metric("整體準確率", f"{acc:.1f}%", f"{st.session_state.ex_correct} / {st.session_state.ex_total} 題")
    if st.session_state.wrong_items:
        st.write("📝 錯題清單 (單字/發音)：")
        for w in st.session_state.wrong_items:
            st.markdown(f'<div class="report-card"><b>題目：</b>{w["cn"]}<br><b>正確解答：</b>{w["ans"]}</div>', unsafe_allow_html=True)
    if st.button("🔄 返回首頁開啟新練習"):
        for k in ['ex_total', 'ex_correct', 'wrong_items', 'show_report']: st.session_state[k] = 0 if isinstance(state_keys[k], int) else state_keys[k]
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
        st.session_state.pool_sizes = {"單字": 0, "文法": 0, "發音": 0}
        st.rerun()
    st.stop()

# ================= 區塊 1：每日一句 =================
st.markdown('<div class="section-title">每日一句韓語</div>', unsafe_allow_html=True)
dq_list = [{"cn": "我想喝咖啡。", "kr": "저는 커피를 마시고 싶어요"}, {"cn": "姊姊正在坐火車。", "kr": "언니는 기차를 타고 있어요"}]
dq = dq_list[st.session_state.dq_idx % len(dq_list)]

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

df = load_data()
if not df.empty:
    all_ch = sorted(df['chapter'].astype(str).unique().tolist())
    def sync_sel():
        new = st.session_state.temp_sel; old = st.session_state.sel_ch
        if "ALL 全部單元" in old and len(new) > 1: st.session_state.sel_ch = [x for x in new if x != "ALL 全部單元"]
        elif "ALL 全部單元" in new and "ALL 全部單元" not in old: st.session_state.sel_ch = ["ALL 全部單元"]
        elif not new: st.session_state.sel_ch = ["ALL 全部單元"]
        else: st.session_state.sel_ch = new
        st.session_state.pools = {"單字": [], "文法": [], "發音": []}
        st.session_state.pool_sizes = {"單字": 0, "文法": 0, "發音": 0}
    
    st.multiselect("選擇單元：", ["ALL 全部單元"]+all_ch, key="temp_sel", on_change=sync_sel, default=st.session_state.sel_ch)
    final_ch = all_ch if "ALL 全部單元" in st.session_state.sel_ch else st.session_state.sel_ch

    tabs = st.tabs(["單字", "文法", "發音"])
    cat_list = ["單字", "文法", "發音"]
    
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
                total_q = st.session_state.pool_sizes[cat]
                completed_q = total_q - len(p)
                st.markdown(f'<div class="progress-text">剩餘：{len(p)} / 已完成：{completed_q}</div>', unsafe_allow_html=True)
                
                item = p[0]
                
                html_card = '<div class="flashcard-box">'
                
                # 🚀 變更：文法直接顯示 kr 與 cn
                if cat == "文法":
                    html_card += f'<h2>{item["kr"]}</h2>'
                    html_card += f'<div class="rule-tag">{item["cn"]}</div>'
                    if exam_mode == "複習" and item.get('note'): 
                        html_card += f'<div class="hint-tag">💡 備註：{item["note"]}</div>'
                else:
                    html_card += f'<h2>{item["cn"]}</h2>'
                    if exam_mode == "複習" and item.get('note'): 
                        html_card += f'<div class="rule-tag">📌 備註：{item["note"]}</div>'
                    target_ans = item['kr']
                
                html_card += '</div>'
                st.markdown(html_card, unsafe_allow_html=True)

                st.markdown('<p class="box-label">造句 / 答案：</p>', unsafe_allow_html=True)
                u_in = st.text_input("", key=f"in_{cat}_{len(p)}", label_visibility="collapsed", placeholder="請輸入韓文...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("檢查", key=f"btn_{cat}_{len(p)}"):
                        if cat == "文法":
                            if u_in.strip():
                                st.session_state.ex_total += 1
                                st.session_state.ex_correct += 1
                                st.success("⭕ 造句完成！請點擊下方框框右上角的「複製圖示」，貼給 Gemini 幫妳批改！")
                                # 💡 產生可一鍵複製的程式碼區塊
                                copy_text = f"Gemini 請幫我批改這句韓文！\n🎯 目標文法：{item['kr']} ({item['cn']})\n✍️ 我的造句：{u_in}"
                                st.code(copy_text, language="markdown")
                            else:
                                st.error("❌ 請先輸入您的造句喔！")
                        else:
                            st.session_state.ex_total += 1
                            if clean_text(u_in) == clean_text(str(target_ans)):
                                st.success(f"⭕ 正確解答：{item['kr']}"); st.session_state.ex_correct += 1; st.balloons()
                            else:
                                st.error(f"❌ 錯誤！正確解答：{item['kr']}")
                                st.session_state.wrong_items.append({"cn": item['cn'], "ans": item['kr']})
                            play_audio(item['kr'])
                            
                with col2:
                    if st.button("下一題", key=f"nxt_{cat}_{len(p)}"):
                        p.pop(0); st.rerun()
            else:
                st.write("✅ 該範圍已練習完畢。")
                if st.session_state.pool_sizes[cat] > 0:
                    if st.button(f"重啟{cat}練習", key=f"reset_{cat}"):
                        st.session_state.pool_sizes[cat] = 0; st.rerun()

    st.write("") 
    if st.button("結束 (同步產出複習報告)", key="end_btn"): st.session_state.show_report = True; st.rerun()
