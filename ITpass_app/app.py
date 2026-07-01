import streamlit as st
import json
import random
import os

# ==========================================
# 共通パス設定（ファイルの見失いを防ぐ）
# ==========================================
BASE_DIR = os.path.dirname(__file__)
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
VOCAB_FILE = os.path.join(BASE_DIR, "vocab.json")
USER_DATA_FILE = os.path.join(BASE_DIR, "users_data.json") # ★ユーザーデータ保存用ファイル

# ==========================================
# データの永続化（ファイルI/O）用関数
# ==========================================
def load_user_data():
    """保存ファイルからユーザー情報と弱点データを読み込む。無ければ初期データを返す"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    # 初回起動時やファイルが壊れている場合のデフォルトデータ
    return {
        "user_db": {
            "user01": {"password": "password123", "name": "ALPHA_OPERATOR"},
            "user02": {"password": "password456", "name": "BETA_TESTER"}
        },
        "all_users_weakness": {
            "user01": {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0},
            "user02": {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
        }
    }

def save_user_data():
    """現在のセッション内のユーザーDBと弱点データをファイルに保存する"""
    data_to_save = {
        "user_db": st.session_state.user_db,
        "all_users_weakness": st.session_state.all_users_weakness
    }
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)


# ==========================================
# 1. 問題・単語データロード
# ==========================================
def load_questions():
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"category": "テクノロジ系", "text": "近距離無線通信技術の国際規格であり、非接触決済などに使われるのはどれか。", "choices": ["BLE", "LTE", "NFC", "Wi-Fi"], "answer": "NFC", "explanation": "NFCは近距離無線通信の規格です。"},
            {"category": "計算問題（テクノロジ系）", "text": "システムAの稼働率が0.9、Bが0.8のとき、直列に接続した全体の稼働率はいくらか。", "choices": ["0.72", "0.85", "0.98", "1.70"], "answer": "0.72", "explanation": "0.9 × 0.8 = 0.72 です。"}
        ]

def load_vocab_words():
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"word": "SLA", "meaning": "サービス品質合意書。品質や範囲について事前に合意し明文化したもの。", "category": "マネジメント系"},
            {"word": "RPA", "meaning": "定型的な事務作業をソフトウェアロボットに代替させて自動化を図る手段。", "category": "ストラテジ系"}
        ]

# ==========================================
# 2. クイズ抽出・モード遷移関数
# ==========================================
def start_quiz(mode_name, max_questions=10):
    all_questions = load_questions()
    filtered_questions = []
    
    if mode_name in ["全体出題", "100問シミュレーション"]:
        filtered_questions = all_questions
    elif mode_name == "テクノロジ系":
        filtered_questions = [q for q in all_questions if "テクノ" in q["category"]]
    elif mode_name == "ストラテジ系":
        filtered_questions = [q for q in all_questions if "ストラテジ" in q["category"]]
    elif mode_name == "マネジメント系":
        filtered_questions = [q for q in all_questions if "マネジメント" in q["category"]]
    elif mode_name == "計算問題特訓":
        filtered_questions = [q for q in all_questions if "計算問題" in q["category"]]
    
    if len(filtered_questions) > 0:
        random.shuffle(filtered_questions)
        limit = min(max_questions, len(filtered_questions))
        st.session_state.shuffled_questions = filtered_questions[:limit]
        st.session_state.game_started = True
        st.session_state.app_mode = "quiz"
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_choice = None
        st.session_state.wrong_questions = []
        st.rerun()

def start_revenge_quiz():
    revenge_questions = st.session_state.wrong_questions.copy()
    random.shuffle(revenge_questions)
    st.session_state.shuffled_questions = revenge_questions
    st.session_state.game_started = True
    st.session_state.app_mode = "quiz"
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.selected_choice = None
    st.session_state.wrong_questions = []
    st.rerun()

def start_vocab_mode():
    all_words = load_vocab_words()
    random.shuffle(all_words)
    vocab_quiz_list = []
    for target in all_words:
        choices = [target["meaning"]]
        other_meanings = [w["meaning"] for w in all_words if w["word"] != target["word"]]
        dummy_choices = random.sample(other_meanings, min(3, len(other_meanings)))
        choices.extend(dummy_choices)
        random.shuffle(choices)
        vocab_quiz_list.append({
            "word": target["word"], 
            "category": target["category"], 
            "answer": target["meaning"], 
            "choices": choices
        })
    st.session_state.vocab_quiz_list = vocab_quiz_list
    st.session_state.vocab_index = 0
    st.session_state.vocab_answered = False
    st.session_state.vocab_selected_choice = None
    st.session_state.vocab_score = 0
    st.session_state.game_started = True
    st.session_state.app_mode = "vocab"
    st.rerun()

def back_to_home():
    st.session_state.game_started = False
    st.session_state.app_mode = "home"
    st.rerun()

# ==========================================
# 3. 状態管理（Session State）の初期化
# ==========================================
# ★起動時に一度だけ外部ファイルからユーザーデータを読み込む
persistent_data = load_user_data()

if "user_db" not in st.session_state: 
    st.session_state.user_db = persistent_data["user_db"]
if "all_users_weakness" not in st.session_state: 
    st.session_state.all_users_weakness = persistent_data["all_users_weakness"]

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "display_name" not in st.session_state: st.session_state.display_name = None
if "is_guest" not in st.session_state: st.session_state.is_guest = False

if "game_started" not in st.session_state: st.session_state.game_started = False
if "app_mode" not in st.session_state: st.session_state.app_mode = "home"
if "shuffled_questions" not in st.session_state: st.session_state.shuffled_questions = []
if "current_index" not in st.session_state: st.session_state.current_index = 0
if "answered" not in st.session_state: st.session_state.answered = False
if "score" not in st.session_state: st.session_state.score = 0
if "wrong_questions" not in st.session_state: st.session_state.wrong_questions = []
if "selected_choice" not in st.session_state: st.session_state.selected_choice = None

if "vocab_quiz_list" not in st.session_state: st.session_state.vocab_quiz_list = []
if "vocab_index" not in st.session_state: st.session_state.vocab_index = 0
if "vocab_answered" not in st.session_state: st.session_state.vocab_answered = False
if "vocab_selected_choice" not in st.session_state: st.session_state.vocab_selected_choice = None
if "vocab_score" not in st.session_state: st.session_state.vocab_score = 0
if "weak_vocab_list" not in st.session_state: st.session_state.weak_vocab_list = []

st.set_page_config(layout="wide", page_title="ITパスポート 試験対策アプリ")

# ==========================================
# 4. クラシックブルー＆マイクロテクスチャCSS
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #466b91 !important;
        background-image: 
            radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
            linear-gradient(135deg, #466b91 0%, #3a597a 100%) !important;
        background-size: 20px 20px, 100% 100% !important;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', sans-serif !important;
        color: #ffffff !important;
    }
    
    .stApp [data-testid="stMarkdownContainer"] p, 
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stMarkdownContainer"] span {
        color: #ffffff;
    }
    
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #ffffff;
        font-weight: 700 !important;
    }
    
    .hud-panel {
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        margin-bottom: 20px;
    }
    .hud-panel, .hud-panel * {
        color: #223142 !important;
    }

    .explanation-box {
        background-color: #e2e8f0 !important;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #466b91;
        margin-bottom: 15px;
    }
    .explanation-box, .explanation-box * {
        color: #1e293b !important;
    }

    div[data-testid="stForm"] {
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px;
        padding: 25px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    div[data-testid="stForm"], div[data-testid="stForm"] * {
        color: #223142 !important;
    }
    div[data-testid="stForm"] div[data-testid="stWidgetLabel"] p {
        color: #223142 !important;
        font-weight: 600;
    }
    
    .stApp input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }

    div[data-testid="stTabs"] button {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        background: transparent !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 3px solid #ffffff !important;
    }

    div.stButton > button {
        font-family: inherit !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease;
        background-color: #1c2e42 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15) !important;
    }
    
    div.stButton > button:hover {
        background-color: #253d58 !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #1e2d42 !important;
        border-color: #1e2d42 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    }
    
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #121c2b !important;
        border-color: #121c2b !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #1c2e42 !important;
        background-image: radial-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px) !important;
        background-size: 16px 16px !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📝 ITパスポート 試験対策システム")
st.divider()

# ==========================================
# 5. ログインチェック & 認証・アカウント作成画面
# ==========================================
if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown("### 🔐 ログイン・新規登録")
    
    tab_login, tab_register, tab_guest = st.tabs(["🔑 ログイン", "➕ 新規アカウント作成", "⚡ ゲストプレイ"])
    
    with tab_login:
        with st.form("login_form"):
            input_user = st.text_input("ユーザーID", placeholder="例: user01")
            input_pass = st.text_input("パスワード", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("ログインする", use_container_width=True, type="primary")
            
            if submit_login:
                db = st.session_state.user_db
                if input_user in db and db[input_user]["password"] == input_pass:
                    st.session_state.logged_in = True
                    st.session_state.is_guest = False
                    st.session_state.username = input_user
                    st.session_state.display_name = db[input_user]["name"]
                    
                    if input_user not in st.session_state.all_users_weakness:
                        st.session_state.all_users_weakness[input_user] = {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
                        save_user_data() # ★ファイルへ同期
                    st.rerun()
                else:
                    st.error("エラー: IDまたはパスワードが一致しません。")
                    
    with tab_register:
        with st.form("register_form"):
            st.markdown("必要情報を入力して、新しい学習用アカウントを発行します。")
            reg_user = st.text_input("希望するユーザーID (英数字)", placeholder="例: study_user")
            reg_name = st.text_input("表示名（ニックネーム）", placeholder="例: 合格を目指す人")
            reg_pass = st.text_input("パスワード", type="password", placeholder="••••••••")
            submit_register = st.form_submit_button("新規登録を実行", use_container_width=True)
            
            if submit_register:
                if not reg_user or not reg_name or not reg_pass:
                    st.error("エラー: 全ての項目を入力してください。")
                elif reg_user in st.session_state.user_db:
                    st.error("エラー: そのユーザーIDは既に登録されています。")
                else:
                    st.session_state.user_db[reg_user] = {"password": reg_pass, "name": reg_name}
                    st.session_state.all_users_weakness[reg_user] = {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
                    
                    save_user_data() # ★新しく作成したアカウント情報を即座にファイルに保存
                    st.success("アカウントが作成されました！「ログイン」タブからログインしてください。")

    with tab_guest:
        st.markdown("アカウントを作成せず、すぐに模擬問題を体験できます（※学習履歴は保存されません）。")
        if st.button("ゲストモードで開始する", use_container_width=True, type="primary"):
            st.session_state.is_guest = True
            st.session_state.logged_in = False
            st.session_state.username = "guest_user"
            st.session_state.display_name = "ゲストユーザー"
            st.session_state.all_users_weakness["guest_user"] = {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
            st.rerun()
            
    st.stop()

current_weakness = st.session_state.all_users_weakness[st.session_state.username]

# ==========================================
# 6. アプリメニュー（サイドバー）
# ==========================================
status_label = "👤 正規ユーザー" if st.session_state.logged_in else "🔌 ゲスト"
st.sidebar.markdown(f"**{status_label}: {st.session_state.display_name}**")

if st.sidebar.button("🚪 ログアウト", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.is_guest = False
    st.session_state.username = None
    st.session_state.display_name = None
    back_to_home()

st.sidebar.divider()
if st.sidebar.button("🏠 ホーム画面に戻る", use_container_width=True):
    back_to_home()
    
st.sidebar.divider()
st.sidebar.markdown("📝 **テスト実行モード**")
if st.sidebar.button("📋 模擬試験 (100問)", use_container_width=True): start_quiz("100問シミュレーション", 100)
if sidebar_all := st.sidebar.button("🔥 全分野ランダム (10問)", use_container_width=True): start_quiz("全体出題", 10)

st.sidebar.divider()
st.sidebar.markdown("📂 **分野別ショートカット**")
if st.sidebar.button("🔮 単語暗記 (4択テスト)", use_container_width=True): start_vocab_mode()
if st.sidebar.button("🧮 計算問題 特訓コア", use_container_width=True): start_quiz("計算問題特訓", 10)
if st.sidebar.button("💼 マネジメント系問題", use_container_width=True): start_quiz("マネジメント系", 10)
if st.sidebar.button("💻 テクノロジ系問題", use_container_width=True): start_quiz("テクノロジ系", 10)
if st.sidebar.button("📈 ストラテジ系問題", use_container_width=True): start_quiz("ストラテジ系", 10)


# ==========================================
# 7. 画面分岐 1：メインホーム画面
# ==========================================
if st.session_state.app_mode == "home":
    user_badge = f"<span style='color: #f1f5f9; background: rgba(255,255,255,0.15); padding: 3px 12px; border-radius: 6px; font-size: 18px; font-weight: 600; margin-left: 10px; border: 1px solid rgba(255,255,255,0.1);'>{st.session_state.display_name}</span>"
    st.markdown(f"<h3 style='display: flex; align-items: center; margin-bottom: 20px;'>📊 弱点分析カルテ — {user_badge}</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, (cat, count) in enumerate(current_weakness.items()):
        with cols[i]:
            status_color = "#466b91" if count == 0 else ("#d97706" if count <= 2 else "#dc2626")
            alert_level = "良好 (CLEAR)" if count == 0 else ("要注意 (WARNING)" if count <= 2 else "苦手克服が必要 (CRITICAL)")
            st.markdown(
                f"""
                <div class="hud-panel" style="border-left: 6px solid {status_color}; height: 120px; padding: 15px 20px;">
                    <div style="font-size:13px; font-weight:bold; color:#64748b;">{cat}</div>
                    <div style="font-size:26px; font-weight:bold; color:{status_color}; margin: 2px 0;">誤答数: {count}</div>
                    <div style="font-size:11px; color:#64748b; font-weight:500;">ステータス: {alert_level}</div>
                </div>
                """, unsafe_allow_html=True
            )
            
    if st.session_state.is_guest:
        st.markdown("<p style='color:#cbd5e1; font-size:13px; margin-top:5px; font-weight:500;'>⚠️ ゲストモードのため、ログアウトすると学習履歴（誤答数）はクリアされます。</p>", unsafe_allow_html=True)
            
    st.divider()
    st.markdown("### 🚀 学習メニューを選択してください")
    
    if st.button("💻 本試験シミュレーション（模擬試験 100問）", use_container_width=True, type="primary"):
        start_quiz("100問シミュレーション", 100)
            
    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔥 ランダム 10問テスト", use_container_width=True): start_quiz("全体出題", 10)
        if st.button("💼 マネジメント系 (知識＋計算)", use_container_width=True): start_quiz("マネジメント系", 10)
        if st.button("💻 テクノロジ系 (知識＋計算)", use_container_width=True): start_quiz("テクノロジ系", 10)
    with col2:
        if st.button("🔮 重要単語 4択クイズ", use_container_width=True): start_vocab_mode()
        if st.button("📈 ストラテジ系 (知識＋計算)", use_container_width=True): start_quiz("ストラテジ系", 10)
        if st.button("🧮 計算問題だけを集中的に解く", use_container_width=True): start_quiz("計算問題特訓", 10)

# ==========================================
# 8. 画面分岐 2：クイズ実行中
# ==========================================
elif st.session_state.app_mode == "quiz":
    questions = st.session_state.shuffled_questions

    if st.session_state.current_index < len(questions):
        st.markdown(f"**分類:** {questions[st.session_state.current_index]['category']} ｜ **進行度:** {st.session_state.current_index + 1} / {len(questions)}")
        
        q = questions[st.session_state.current_index]
        st.markdown(f'<div class="hud-panel" style="border-top: 5px solid #1e2d42;"><div style="font-size: 18px; line-height:1.6; font-weight:500;">{q["text"]}</div></div>', unsafe_allow_html=True)
        
        choices = q["choices"]
        row1_cols = st.columns(2)
        row2_cols = st.columns(2)
        
        for i, choice in enumerate(choices):
            target_col = row1_cols[i] if i < 2 else row2_cols[i - 2]
            btn_type = "primary" if (st.session_state.answered and choice == q["answer"]) else "secondary"

            if target_col.button(choice, use_container_width=True, key=f"modern_btn_{st.session_state.current_index}_{i}", disabled=st.session_state.answered, type=btn_type):
                st.session_state.answered = True
                st.session_state.selected_choice = choice
                if choice == q["answer"]:
                    st.session_state.score += 1
                else:
                    st.session_state.wrong_questions.append(q)
                    if "テクノ" in q["category"]: target_cat = "テクノロジ系"
                    elif "ストラテジ" in q["category"]: target_cat = "ストラテジ系"
                    else: target_cat = "マネジメント系"
                    st.session_state.all_users_weakness[st.session_state.username][target_cat] += 1
                    save_user_data() # ★誤答カウントが増えたタイミングでファイルに即時書き込み
                st.rerun()

        if st.session_state.answered:
            st.write("")
            ans_box = st.container()
            with ans_box:
                if st.session_state.selected_choice == q["answer"]:
                    st.markdown("<h3 style='color:#86efac !important;'>⭕ 正解です！</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='color:#fca5a5 !important;'>❌ 不正解...</h3><p style='font-size:16px; color:#ffffff;'>正解: <b>「{q['answer']}」</b></p>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="explanation-box">
                    <b style="color:#1e2d42 !important;">【解説】</b><br>{q['explanation']}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("▶ 次の問題へ進む", use_container_width=True, type="primary"):
                    st.session_state.current_index += 1
                    st.session_state.answered = False
                    st.session_state.selected_choice = None
                    st.rerun()
    else:
        st.balloons() 
        st.markdown("## 🏁 テストが終了しました")
        st.markdown(f"#### あなたのスコア: `{st.session_state.score}` / {len(questions)} 問正解")
        st.divider()
        if len(st.session_state.wrong_questions) > 0:
            if st.button("🔄 間違えた問題だけにもう一度挑戦する", use_container_width=True, type="primary"): start_revenge_quiz()
        if st.button("🏠 ホーム画面に戻る", use_container_width=True): back_to_home()

# ==========================================
# 9. 画面分岐 3：単語暗記テストモード
# ==========================================
elif st.session_state.app_mode == "vocab":
    vocab_quizzes = st.session_state.vocab_quiz_list
    
    if st.session_state.vocab_index < len(vocab_quizzes):
        st.markdown(f"**単語テスト進行度:** {st.session_state.vocab_index + 1} / {len(vocab_quizzes)}")
        
        vq = vocab_quizzes[st.session_state.vocab_index]
        st.markdown(f'<div class="hud-panel" style="border-top: 5px solid #1e2d42;"><div style="font-size: 13px; color: #64748b; font-weight: bold;">[ 出題単語 ]</div><div style="font-size: 32px; font-weight: bold; color: #466b91 !important; margin-top:5px;">{vq["word"]}</div></div>', unsafe_allow_html=True)
        
        for idx, choice in enumerate(vq["choices"]):
            btn_type = "primary" if (st.session_state.vocab_answered and choice == vq["answer"]) else "secondary"
            if st.button(choice, use_container_width=True, key=f"v_btn_{st.session_state.vocab_index}_{idx}", disabled=st.session_state.vocab_answered, type=btn_type):
                st.session_state.vocab_answered = True
                st.session_state.vocab_selected_choice = choice
                if choice == vq["answer"]:
                    st.session_state.vocab_score += 1
                else:
                    st.session_state.weak_vocab_list.append(vq)
                    st.session_state.all_users_weakness[st.session_state.username][vq["category"]] += 1
                    save_user_data() # ★単語テストの誤答数もファイルに同期
                st.rerun()
                
        if st.session_state.vocab_answered:
            st.write("")
            if st.session_state.vocab_selected_choice == vq["answer"]:
                st.markdown("<h3 style='color:#86efac !important;'>⭕ 正解！</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='color:#fca5a5 !important;'>❌ 不正解...</h3><p style='font-size:16px; color:#ffffff;'>正解の意味:<br><b style='color:#cbd5e1;'>{vq['answer']}</b></p>", unsafe_allow_html=True)
                
            if st.button("▶ 次の単語へ進む", use_container_width=True, type="primary"):
                st.session_state.vocab_index += 1
                st.session_state.vocab_answered = False
                st.session_state.vocab_selected_choice = None
                st.rerun()
    else:
        st.markdown("## 🏁 単語テスト完了")
        st.markdown(f"#### スコア: `{st.session_state.vocab_score}` / {len(vocab_quizzes)} 単語正解")
        st.divider()
        if len(st.session_state.weak_vocab_list) > 0:
            st.markdown("### 📋 今回間違えた重要キーワード")
            for ww in st.session_state.weak_vocab_list:
                st.markdown(f"- **{ww['word']}**: {ww['answer']}")
        if st.button("🏠 ホーム画面に戻る", use_container_width=True):
            st.session_state.weak_vocab_list = []
            back_to_home()
