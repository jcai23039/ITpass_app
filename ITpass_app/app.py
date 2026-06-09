import streamlit as st
import json
import random

# 外部のJSONファイルから問題データを読み込む関数
def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"category": "ストラテジ系", "text": "著作権法で保護されるものはどれか。", "choices": ["プログラム言語", "アルゴリズム", "ソースコード", "フリーウェアの規約"], "answer": "ソースコード", "explanation": "プログラムのソースコードは著作物として保護されます。"},
            {"category": "テクノロジ系", "text": "OSS(Open Source Software)に関する記述はどれか。", "choices": ["ソースコードの公開が必須", "商用利用は禁止", "著作権が放棄されている", "改変は禁止"], "answer": "ソースコードの公開が必須", "explanation": "OSSはソースコードが公開され、改良や再配布が認められています。"}
        ]

def start_quiz(mode_name):
    all_questions = load_questions()
    filtered_questions = []
    if mode_name == "全体出題":
        filtered_questions = all_questions
    else:
        for q in all_questions:
            if q["category"] == mode_name:
                filtered_questions.append(q)
    
    if len(filtered_questions) > 0:
        random.shuffle(filtered_questions)
        filtered_questions = filtered_questions[:10]
        st.session_state.shuffled_questions = filtered_questions
        st.session_state.game_started = True
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_choice = None
        st.session_state.wrong_questions = []
        st.rerun()
    else:
        st.sidebar.warning(f"⚠️ {mode_name} のデータが未検出です。")

def start_revenge_quiz():
    if len(st.session_state.wrong_questions) > 0:
        revenge_questions = list(st.session_state.wrong_questions)
        random.shuffle(revenge_questions)
        st.session_state.shuffled_questions = revenge_questions
        st.session_state.game_started = True
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_choice = None
        st.session_state.wrong_questions = []
        st.rerun()

def back_to_home():
    st.session_state.game_started = False
    st.rerun()

# 状態管理の初期化
if "game_started" not in st.session_state: st.session_state.game_started = False
if "shuffled_questions" not in st.session_state: st.session_state.shuffled_questions = []
if "current_index" not in st.session_state: st.session_state.current_index = 0
if "answered" not in st.session_state: st.session_state.answered = False
if "score" not in st.session_state: st.session_state.score = 0
if "wrong_questions" not in st.session_state: st.session_state.wrong_questions = []
if "selected_choice" not in st.session_state: st.session_state.selected_choice = None

# ワイドモード設定
st.set_page_config(layout="wide")

# ==========================================
# ⚡️ サイバーパンク・カスタムCSS注入 ⚡️
# ==========================================
st.markdown(
    """
    <style>
    /* 全体の背景と基本フォントカラー（等幅フォントでハッカー感を演出） */
    .stApp {
        background-color: #0a0a12 !important;
        color: #39ff14 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* タイトルとキャプションの色調整 */
    h1 {
        color: #ff007f !important;
        text-shadow: 0 0 10px #ff007f, 0 0 20px #ff007f;
    }
    .stMarkdown p {
        color: #39ff14;
    }
    
    /* サイドバーのサイバー化 */
    [data-testid="stSidebar"] {
        background-color: #0e0e1a !important;
        border-right: 2px solid #00ffff;
    }
    
    /* Streamlit標準ボタンのスタイルをオーバーライド */
    div.stButton > button {
        background-color: #121224 !important;
        color: #00ffff !important;
        border: 1px solid #00ffff !important;
        box-shadow: 0 0 5px #00ffff;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    /* ボタンホバー時の一斉発光効果 */
    div.stButton > button:hover {
        color: #ffffff !important;
        background-color: #00ffff !important;
        box-shadow: 0 0 15px #00ffff, 0 0 25px #00ffff;
    }
    
    /* 回答後・次の問題へ進む特殊ボタン（ピンク発光） */
    div.stButton > button[kind="primary"] {
        color: #ff007f !important;
        border: 1px solid #ff007f !important;
        box-shadow: 0 0 5px #ff007f !important;
    }
    div.stButton > button[kind="primary"]:hover {
        color: #ffffff !important;
        background-color: #ff007f !important;
        box-shadow: 0 0 15px #ff007f, 0 0 25px #ff007f !important;
    }
    
    /* 水平線のネオン化 */
    hr {
        border-color: #00ffff !important;
        box-shadow: 0 0 5px #00ffff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡️ ITパスポート 学習アプリ")
st.caption("Python with Gemini")
st.divider()

# ==========================================
# アプリメニュー（サイドバー）
# ==========================================
if st.session_state.game_started:
    st.sidebar.markdown("<h3 style='color:#00ffff;'>⚙️ SYSTEM MENU</h3>", unsafe_allow_html=True)
    if st.sidebar.button("🏠 RETURN TO HOME", use_container_width=True):
        back_to_home()
        
    st.sidebar.divider()
    st.sidebar.markdown("<p style='color:#00ffff;'>🔄 CATEGORY OVERRIDE</p>", unsafe_allow_html=True)
    if st.sidebar.button("🔥 ALL CATEGORIES", use_container_width=True): start_quiz("全体出題")
    if st.sidebar.button("📈 STRATEGY", use_container_width=True): start_quiz("ストラテジ系")
    if st.sidebar.button("💼 MANAGEMENT", use_container_width=True): start_quiz("マネジメント系")
    if st.sidebar.button("💻 TECHNOLOGY", use_container_width=True): start_quiz("テクノロジ系")

# ==========================================
# 画面1：モード選択画面
# ==========================================
if not st.session_state.game_started:
    st.markdown("<h3 style='color:#00ffff;'>挑戦したい分野を選んでください</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔥 全体出題", use_container_width=True): start_quiz("全体出題")
        if st.button("💼 マネジメント系", use_container_width=True): start_quiz("マネジメント系")
    with col2:
        if st.button("📈 ストラテジ系", use_container_width=True): start_quiz("ストラテジ系")
        if st.button("💻 テクノロジ系", use_container_width=True): start_quiz("テクノロジ系")

# ==========================================
# 画面2：クイズ実行中
# ==========================================
else:
    questions = st.session_state.shuffled_questions

    if st.session_state.current_index < len(questions):
        q = questions[st.session_state.current_index]
        
        # ステータスバー
        st.markdown(f"<span style='color:#00ffff;'>◆ CATEGORY:</span> {q['category']} ｜ <span style='color:#00ffff;'>◆ TASK:</span> {st.session_state.current_index + 1} / {len(questions)}", unsafe_allow_html=True)
        
        # ホログラム（問題文）ボックス。ピンクの強烈なグロー効果
        formatted_text = q["text"].replace("\n", "<br>")
        st.markdown(
            f"""
            <div style="
                background-color: #0f0014; 
                color: #ffffff; 
                padding: 15px 20px; 
                border-radius: 4px; 
                font-size: 18px; 
                font-weight: bold;
                line-height: 1.5;
                margin-bottom: 15px;
                border: 1px solid #ff007f;
                box-shadow: 0 0 10px #ff007f, inset 0 0 5px #ff007f;
            ">
                {formatted_text}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        choices = q["choices"]
        row1_cols = st.columns(2)
        row2_cols = st.columns(2)
        
        for i, choice in enumerate(choices):
            target_col = row1_cols[i] if i < 2 else row2_cols[i - 2]
            
            btn_type = "secondary"
            if st.session_state.answered and choice == q["answer"]:
                btn_type = "primary" # 正解選択肢をピンクの光に変化させる

            if target_col.button(choice, use_container_width=True, key=f"cyber_btn_{st.session_state.current_index}_{i}", disabled=st.session_state.answered, type=btn_type):
                st.session_state.answered = True
                st.session_state.selected_choice = choice
                if choice == q["answer"]:
                    st.session_state.score += 1
                else:
                    st.session_state.wrong_questions.append(q)
                st.rerun()

        # 結果・ログ出力
        if st.session_state.answered:
            st.write("")
            ans_col1, ans_col2 = st.columns([2, 1])
            
            with ans_col1:
                if st.session_state.selected_choice == q["answer"]:
                    st.markdown("<h3 style='color:#39ff14; text-shadow: 0 0 10px #39ff14;'>▶ 正解！</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='color:#ff007f; text-shadow: 0 0 10px #ff007f;'>▶ 不正解...</h3><p style='color:#00ffff;'>正解: 「{q['answer']}」</p>", unsafe_allow_html=True)
                
                st.markdown(f"<span style='color:#00ffff;'>【解説】\n\n</span> {q['explanation']}", unsafe_allow_html=True)
                
            with ans_col2:
                if st.button("▶ 次へ", use_container_width=True, type="primary"):
                    st.session_state.current_index += 1
                    st.session_state.answered = False
                    st.session_state.selected_choice = None
                    st.rerun()

    # リザルト
    else:
        st.balloons() 
        st.markdown("<h2 style='color:#00ffff; text-shadow: 0 0 10px #00ffff;'>▶ お疲れ様でした！</h2>", unsafe_allow_html=True)
        
        score_rate = st.session_state.score / len(questions)
        if score_rate == 1.0:
            st.markdown(f"<div style='color:#39ff14; font-size:24px; text-shadow: 0 0 15px #39ff14;'>🎉 全問正解 🎉 （{st.session_state.score} / {len(questions)}）</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#00ffff; font-size:20px;'>SCORE: {st.session_state.score} / {len(questions)} </div>", unsafe_allow_html=True)
        
        st.divider()
        
        if len(st.session_state.wrong_questions) > 0:
            st.markdown(f"<p style='color:#ff007f;'>❌ 合計 {len(st.session_state.wrong_questions)} 問不正解でした。リトライしますか？</p>", unsafe_allow_html=True)
            if st.button("▶ リトライ ◀", use_container_width=True, type="primary"):
                start_revenge_quiz()
        
        if st.button("🏠 タイトルへ戻る 🏠", use_container_width=True):
            back_to_home()