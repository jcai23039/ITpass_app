import streamlit as st
import json
import random

# ==========================================
# ユーザー認証用の簡易データベースの初期化
# ==========================================
# セッションを跨いでアカウントを保持するため、Streamlitの初期化処理に入れます
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "user01": {"password": "password123", "name": "ALPHA_OPERATOR"},
        "user02": {"password": "password456", "name": "BETA_TESTER"}
    }

# ==========================================
# 1. データロード
# ==========================================
def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [
            {"category": "テクノロジ系", "text": "近距離無線通信技術の国際規格であり、非接触決済などに使われるのはどれか。", "choices": ["BLE", "LTE", "NFC", "Wi-Fi"], "answer": "NFC", "explanation": "NFCは近距離無線通信の規格です。"},
            {"category": "計算問題（テクノロジ系）", "text": "システムAの稼働率が0.9、Bが0.8のとき、直列に接続した全体の稼働率はいくらか。", "choices": ["0.72", "0.85", "0.98", "1.70"], "answer": "0.72", "explanation": "0.9 × 0.8 = 0.72 です。"}
        ]

def load_vocab_words():
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

# 全ユーザーの苦手分析を保持するデータベース
if "all_users_weakness" not in st.session_state:
    st.session_state.all_users_weakness = {}

if "vocab_quiz_list" not in st.session_state: st.session_state.vocab_quiz_list = []
if "vocab_index" not in st.session_state: st.session_state.vocab_index = 0
if "vocab_answered" not in st.session_state: st.session_state.vocab_answered = False
if "vocab_selected_choice" not in st.session_state: st.session_state.vocab_selected_choice = None
if "vocab_score" not in st.session_state: st.session_state.vocab_score = 0
if "weak_vocab_list" not in st.session_state: st.session_state.weak_vocab_list = []

st.set_page_config(layout="wide")

# ==========================================
# 4. サイバーパンクCSS
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0a0a0c !important;
        background-image: linear-gradient(rgba(0, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px) !important;
        background-size: 40px 40px !important;
        font-family: 'Courier New', Courier, monospace !important;
        color: #39ff14 !important;
    }
    .hud-panel {
        background: rgba(10, 25, 47, 0.8);
        border: 1px solid #00d4ff;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        margin-bottom: 20px;
    }
    div.stButton > button {
        font-family: 'Courier New', Courier, monospace !important;
        border-radius: 0 !important;
        border: 1px solid #00ffff !important;
        background: #000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("IT-PASSPORT_SYSTEM_V.3.5")
st.divider()

# ==========================================
# 5. ログインチェック & 認証・アカウント作成画面
# ==========================================
if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown("<h3 style='color:#00ffff;'>🔐 ACCESS SECURITY GATE (認証セキュリティゲート)</h3>", unsafe_allow_html=True)
    
    # タブを使ってログインとサインアップ、ゲストアクセスをスマートに配置
    tab_login, tab_register, tab_guest = st.tabs(["🔑 OPERATOR LOGIN", "➕ CREATE NEW ACCOUNT", "⚡ GUEST ACCESSS"])
    
    # --- タブ1：ログイン ---
    with tab_login:
        with st.form("login_form"):
            input_user = st.text_input("USER ID (ユーザーID)", placeholder="例: user01")
            input_pass = st.text_input("PASSWORD (パスワード)", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("認証シークエンス実行", use_container_width=True)
            
            if submit_login:
                db = st.session_state.user_db
                if input_user in db and db[input_user]["password"] == input_pass:
                    st.session_state.logged_in = True
                    st.session_state.is_guest = False
                    st.session_state.username = input_user
                    st.session_state.display_name = db[input_user]["name"]
                    
                    if input_user not in st.session_state.all_users_weakness:
                        st.session_state.all_users_weakness[input_user] = {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
                    st.rerun()
                else:
                    st.error("INVALID CREDENTIALS: IDまたはパスワードが一致しません。")
                    
    # --- タブ2：新規アカウント作成 ---
    with tab_register:
        with st.form("register_form"):
            st.markdown("<p style='color:#00ffff;'>新しいオペレーター情報をホストに登録します。</p>", unsafe_allow_html=True)
            reg_user = st.text_input("希望のUSER ID (英数字のみ)", placeholder="例: cyber_stud88")
            reg_name = st.text_input("表示されるオペレーター名 (自由)", placeholder="例: 🚀超高速学習者")
            reg_pass = st.text_input("PASSWORD (パスワード)", type="password", placeholder="••••••••")
            submit_register = st.form_submit_button("新規オペレーターとして登録申請", use_container_width=True)
            
            if submit_register:
                if not reg_user or not reg_name or not reg_pass:
                    st.error("入力エラー: 全ての項目を入力してください。")
                elif reg_user in st.session_state.user_db:
                    st.error("REGISTRATION REJECTED: そのユーザーIDは既にシステムに登録されています。")
                else:
                    # ユーザーデータベース（セッション）に追加
                    st.session_state.user_db[reg_user] = {"password": reg_pass, "name": reg_name}
                    # 苦手カウンターも同時に初期化
                    st.session_state.all_users_weakness[reg_user] = {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
                    st.success(f"SUCCESS: 登録が完了しました！上の『LOGIN』タブからログインしてください。")

    # --- タブ3：ゲストプレイ ---
    with tab_guest:
        st.markdown("<p style='color:#ffaa00;'>アカウントを作らず、一時的なセクションとして即座に演習コアを立ち上げます。</p>", unsafe_allow_html=True)
        if st.button("⚡ GUEST BOOT SEQUENCE (ゲスト接続開始)", use_container_width=True):
            st.session_state.is_guest = True
            st.session_state.logged_in = False
            st.session_state.username = "guest_user"
            st.session_state.display_name = "GUEST_OPERATOR"
            st.session_state.all_users_weakness["guest_user"] = {"テクノロジ系": 0, "ストラテジ系": 0, "マネジメント系": 0}
            st.rerun()
            
    st.stop()  # ゲートを通過するまで以降のメインコンテンツは非表示

# 現在アクティブなプレイヤーのカルテを抽出
current_weakness = st.session_state.all_users_weakness[st.session_state.username]

# ==========================================
# 6. アプリメニュー（サイドバー）
# ==========================================
status_label = "👤 REG_OPERATOR" if st.session_state.logged_in else "🔌 GUEST_MODE"
st.sidebar.markdown(f"<span style='color:#39ff14;'>{status_label}: {st.session_state.display_name}</span>", unsafe_allow_html=True)

if st.sidebar.button("🚪 LOGOUT (システム切断)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.is_guest = False
    st.session_state.username = None
    st.session_state.display_name = None
    back_to_home()

st.sidebar.divider()
if st.sidebar.button("🏠 RETURN TO HOME", use_container_width=True):
    back_to_home()
    
st.sidebar.divider()
st.sidebar.markdown("<p style='color:#00ffff;'>🔄 CORE MODES</p>", unsafe_allow_html=True)
if st.sidebar.button("⚡ 100 QUESTIONS MOCK", use_container_width=True): start_quiz("100問シミュレーション", 100)
if st.sidebar.button("🔥 ALL CATEGORIES (10Q)", use_container_width=True): start_quiz("全体出題", 10)

st.sidebar.divider()
st.sidebar.markdown("<p style='color:#00ffff;'>📂 DATABASE DIRECT LINKS</p>", unsafe_allow_html=True)
if st.sidebar.button("🔮 WORD INTERFERENCE (単語)", use_container_width=True): start_vocab_mode()
if st.sidebar.button("🧮 COMPUTATION CORE (計算)", use_container_width=True): start_quiz("計算問題特訓", 10)
if st.sidebar.button("💼 MANAGEMENT (マネジメント)", use_container_width=True): start_quiz("マネジメント系", 10)
if st.sidebar.button("💻 TECHNOLOGY (テクノロジ)", use_container_width=True): start_quiz("テクノロジ系", 10)
if st.sidebar.button("📈 STRATEGY (ストラテジ)", use_container_width=True): start_quiz("ストラテジ系", 10)


# ==========================================
# 7. 画面分岐 1：メインホーム画面
# ==========================================
if st.session_state.app_mode == "home":
    user_tag = f"[{st.session_state.display_name}]"
    st.markdown(f"<h3 style='color:#00ffff;'>📊 WEAKNESS DETECTION {user_tag}</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, (cat, count) in enumerate(current_weakness.items()):
        with cols[i]:
            status_color = "#39ff14" if count == 0 else ("#ffaa00" if count <= 2 else "#ff007f")
            alert_level = "CLEAR" if count == 0 else ("WARNING" if count <= 2 else "CRITICAL")
            st.markdown(
                f"""
                <div class="hud-panel" style="border-color: {status_color}; height: 120px;">
                    <div style="font-size:12px; color:{status_color};">{cat}</div>
                    <div style="font-size:24px; font-weight:bold; color:#fff;">ERROR: {count}</div>
                    <div style="font-size:11px; color:{status_color}; letter-spacing:1px;">STATUS: {alert_level}</div>
                </div>
                """, unsafe_allow_html=True
            )
            
    if st.session_state.is_guest:
        st.markdown("<p style='color:#ffaa00; font-size:12px;'>⚠️ ※ゲストモードの一時データです。ログアウトまたは画面を閉じるとエラー数はリセットされます。</p>", unsafe_allow_html=True)
            
    st.divider()
    st.markdown("<h3 style='color:#00ffff;'>挑戦したいシステムを選択してください</h3>", unsafe_allow_html=True)
    
    if st.button("💻 模擬試験（100問）💻", use_container_width=True, type="primary"):
        start_quiz("100問シミュレーション", 100)
            
    st.write("") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔥 全体出題 (10問)", use_container_width=True): start_quiz("全体出題", 10)
        if st.button("💼 マネジメント系 (知識+計算10問)", use_container_width=True): start_quiz("マネジメント系", 10)
        if st.button("💻 テクノロジ系 (知識+計算10問)", use_container_width=True): start_quiz("テクノロジ系", 10)
    with col2:
        if st.button("🔮 単語暗記テスト (4択モード)", use_container_width=True): start_vocab_mode()
        if st.button("📈 ストラテジ系 (知識+計算10問)", use_container_width=True): start_quiz("ストラテジ系", 10)
        if st.button("🧮 計算問題特訓専用コア (10問)", use_container_width=True): start_quiz("計算問題特訓", 10)

# ==========================================
# 8. 画面分岐 2：クイズ実行中
# ==========================================
elif st.session_state.app_mode == "quiz":
    questions = st.session_state.shuffled_questions

    if st.session_state.current_index < len(questions):
        q = questions[st.session_state.current_index]
        st.markdown(f"<span style='color:#00ffff;'>◆ CATEGORY:</span> {q['category']} ｜ <span style='color:#00ffff;'>◆ TASK:</span> {st.session_state.current_index + 1} / {len(questions)}", unsafe_allow_html=True)
        st.markdown(f'<div class="hud-panel"><div style="font-size: 12px; color: #00d4ff; margin-bottom: 5px;">[Question]</div><div style="font-size: 20px; color: #ffffff;">{q["text"]}</div></div>', unsafe_allow_html=True)
        
        choices = q["choices"]
        row1_cols = st.columns(2)
        row2_cols = st.columns(2)
        
        for i, choice in enumerate(choices):
            target_col = row1_cols[i] if i < 2 else row2_cols[i - 2]
            btn_type = "primary" if (st.session_state.answered and choice == q["answer"]) else "secondary"

            if target_col.button(choice, use_container_width=True, key=f"cyber_btn_{st.session_state.current_index}_{i}", disabled=st.session_state.answered, type=btn_type):
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
                st.rerun()

        if st.session_state.answered:
            st.write("")
            ans_col1, ans_col2 = st.columns([2, 1])
            with ans_col1:
                if st.session_state.selected_choice == q["answer"]:
                    st.markdown("<h3 style='color:#39ff14; text-shadow: 0 0 10px #39ff14;'>▶ 正解！</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='color:#ff007f; text-shadow: 0 0 10px #ff007f;'>▶ 不正解...</h3><p style='color:#00ffff;'>正解: 「{q['answer']}」</p>", unsafe_allow_html=True)
                st.markdown("<span style='color:#00ffff;'>【解説】</span>", unsafe_allow_html=True)
                st.write(q['explanation'])
            with ans_col2:
                if st.button("▶ 次へ", use_container_width=True, type="primary"):
                    st.session_state.current_index += 1
                    st.session_state.answered = False
                    st.session_state.selected_choice = None
                    st.rerun()
    else:
        st.balloons() 
        st.markdown("<h2 style='color:#00ffff; text-shadow: 0 0 10px #00ffff;'>▶ クイズシミュレーション終了</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#00ffff; font-size:20px;'>SCORE: {st.session_state.score} / {len(questions)} </div>", unsafe_allow_html=True)
        st.divider()
        if len(st.session_state.wrong_questions) > 0:
            if st.button("▶ 不正解問題のみリトライ ◀", use_container_width=True, type="primary"): start_revenge_quiz()
        if st.button("🏠 タイトルへ戻る 🏠", use_container_width=True): back_to_home()

# ==========================================
# 9. 画面分岐 3：単語暗記テストモード
# ==========================================
elif st.session_state.app_mode == "vocab":
    vocab_quizzes = st.session_state.vocab_quiz_list
    
    if st.session_state.vocab_index < len(vocab_quizzes):
        vq = vocab_quizzes[st.session_state.vocab_index]
        st.markdown(f"<span style='color:#bd00ff;'>◆ VOCAB SIGNAL:</span> {st.session_state.vocab_index + 1} / {len(vocab_quizzes)}", unsafe_allow_html=True)
        st.markdown(f'<div class="hud-panel" style="border-color: #bd00ff;"><div style="font-size: 12px; color: #bd00ff;">[ TARGET WORD ]</div><div style="font-size: 36px; font-weight: bold; color: #ffffff;">{vq["word"]}</div></div>', unsafe_allow_html=True)
        
        for idx, choice in enumerate(vq["choices"]):
            btn_type = "primary" if (st.session_state.vocab_answered and choice == vq["answer"]) else "secondary"
            if st.button(choice, use_container_width=True, key=f"vocab_btn_{st.session_state.vocab_index}_{idx}", disabled=st.session_state.vocab_answered, type=btn_type):
                st.session_state.vocab_answered = True
                st.session_state.vocab_selected_choice = choice
                if choice == vq["answer"]:
                    st.session_state.vocab_score += 1
                else:
                    st.session_state.weak_vocab_list.append(vq)
                    st.session_state.all_users_weakness[st.session_state.username][vq["category"]] += 1
                st.rerun()
                
        if st.session_state.vocab_answered:
            st.write("")
            v_ans_col1, v_ans_col2 = st.columns([2, 1])
            with v_ans_col1:
                if st.session_state.vocab_selected_choice == vq["answer"]:
                    st.markdown("<h3 style='color:#39ff14; text-shadow: 0 0 10px #39ff14;'>▶ SIGNAL CLEAR（正解）</h3>", unsafe_allow_html=True)
                else:
                    st.markdown("<h3 style='color:#ff007f; text-shadow: 0 0 10px #ff007f;'>▶ SIGNAL ERROR（不正解）</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#00ffff;'>正解の意味:<br>{vq['answer']}</p>", unsafe_allow_html=True)
            with v_ans_col2:
                if st.button("▶ 次の単語へ", use_container_width=True, type="primary"):
                    st.session_state.vocab_index += 1
                    st.session_state.vocab_answered = False
                    st.session_state.vocab_selected_choice = None
                    st.rerun()
    else:
        st.markdown("<h2 style='color:#bd00ff; text-shadow: 0 0 10px #bd00ff;'>▶ FLASH MEMORY SEQUENCE COMPLETE</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#bd00ff; font-size:20px;'>SCORE: {st.session_state.vocab_score} / {len(vocab_quizzes)} </div>", unsafe_allow_html=True)
        st.divider()
        if len(st.session_state.weak_vocab_list) > 0:
            st.markdown(f"### 📋 今回誤認したクリティカルワード ({len(st.session_state.weak_vocab_list)}語)")
            for ww in st.session_state.weak_vocab_list:
                st.markdown(f"- <span style='color:#ff007f; font-weight:bold;'>{ww['word']}</span>: {ww['answer']}", unsafe_allow_html=True)
        if st.button("🏠 ホームへ戻る", use_container_width=True):
            st.session_state.weak_vocab_list = []
            back_to_home()
