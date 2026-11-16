import streamlit as st
import sqlite3
from datetime import datetime
import pytz
import os

# Page configuration
st.set_page_config(page_title="AX AI WebApp", layout="wide")

# Database initialization
def init_db():
    conn = sqlite3.connect("myproject.db", check_same_thread=False)
    cursor = conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id_num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL,
            userid TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    # Inventory table (Survey)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id_num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            userid TEXT NOT NULL,
            q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
            q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    return sqlite3.connect("myproject.db", check_same_thread=False)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'userid' not in st.session_state:
    st.session_state['userid'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

# Sidebar Menu
st.sidebar.title("메뉴")
if st.session_state['logged_in']:
    st.sidebar.success(f"🔓 {st.session_state['username']}님 환영합니다.")
    menu = st.sidebar.radio("이동할 메뉴를 선택하세요", ["홈 랜딩페이지", "AX 전환 학생 인식 실태조사"])
    
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['userid'] = None
        st.session_state['username'] = None
        st.rerun()
else:
    st.sidebar.warning("🔒 로그인이 필요합니다.")
    menu = "홈 랜딩페이지"

# 1. Main Landing Page Logic
if menu == "홈 랜딩페이지":
    if not st.session_state['logged_in']:
        st.title("Welcome! AX 교육 플랫폼")
        st.write("본 웹앱은 머신러닝 학습 및 AX 전환 인식을 위한 공간입니다. 서비스 이용을 위해 로그인해 주세요.")
        
        tab1, tab2 = st.tabs(["로그인", "신규 회원가입"])
        
        with tab1:
            st.subheader("로그인")
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인 실행"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE userid=? AND password=?", (login_id, login_pw))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['userid'] = login_id
                    st.session_state['username'] = user[0]
                    st.success("로그인 성공!")
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                    
        with tab2:
            st.subheader("신규 회원가입")
            reg_name = st.text_input("이름/담당", key="reg_name")
            reg_id = st.text_input("사용할 아이디", key="reg_id")
            reg_pw = st.text_input("비밀번호 설정", type="password", key="reg_pw")
            
            if st.button("회원가입 완료"):
                if reg_name and reg_id and reg_pw:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        ktc_zone = pytz.timezone('Asia/Seoul')
                        now_ktc = datetime.now(ktc_zone).strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO users (username, userid, password, created_at) VALUES (?, ?, ?, ?)",
                                       (reg_name, reg_id, reg_pw, now_ktc))
                        conn.commit()
                        st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인 해주세요.")
                    except sqlite3.IntegrityError:
                        st.error("이미 존재하는 아이디입니다.")
                    finally:
                        conn.close()
                else:
                    st.error("모든 항목을 입력해주세요.")
    else:
        # Logged in main landing content (Provided base code integration)
        st.title("This is my first webapp")
        
        urls = [
            'https://www.youtube.com/watch?v=KR8ddnPjCtk', 
            'https://www.youtube.com/watch?v=CgSvahZkJmc', 
            'https://www.youtube.com/watch?v=CgSvahZkJmc'
        ]
        images = ['data:image/webp;base64,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']

        con1, con2 = st.columns((4, 1))
        with con1:
            with st.expander("Content..."):
                for i in range(len(urls)):
                    st.video(urls[i])

        with con2:
            with st.expander("Tips..."):
                st.image(images[0])

        con3, con4 = st.columns((4, 1))
        with con3:
            with st.expander('Content....'):
                import pandas as pd
                from pathlib import Path
                csv_path = Path(__file__).parent / "data.csv"
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    st.write(df)
                else:
                    st.info("data.csv 파일이 없습니다. 기본 예시 테이블을 노출합니다.")
                    df = pd.DataFrame({"번호": [1, 2], "내용": ["데이터1", "데이터2"]})
                    st.write(df)
        with con4:
            with st.expander("Tips..."):
                txt_path = Path(__file__).parent / "ml.txt"
                if txt_path.exists():
                    with open(txt_path, "r", encoding="utf8") as f:
                        mytxt = f.read()
                        st.markdown(mytxt)
                else:
                    st.markdown("### 머신러닝 가이드\nml.txt 파일 내용이 여기에 표시됩니다.")
                st.image(images[0])

# 2. Survey Page Logic
elif menu == "AX 전환 학생 인식 실태조사":
    st.title("📋 AX(AI 대전환)에 따른 학생 인식 실태조사")
    st.write("본 설문조사는 교육의 AI 대전환(AX)에 따른 학생들의 인식을 조사하기 위한 리커트 5단 척도 문항입니다.")
    
    questions = [
        "1. AI 기술이 학교 수업에 도입되는 것에 긍정적이다.",
        "2. AI 튜터나 챗봇이 나의 자기주도 학습에 도움이 된다고 생각한다.",
        "3. 맞춤형 AI 교육 시스템이 학업 성취도를 높여줄 것이다.",
        "4. 학교에 AI 기반 교육 인프라가 충분히 갖추어져 있다고 느낀다.",
        "5. 교과 선생님들이 AI 도구를 수업에 잘 활용하고 계신다.",
        "6. AI 교육 시스템을 사용할 때 개인정보 유출에 대한 우려가 없다.",
        "7. AI를 활용한 과제 및 평가 방식이 공정하다고 생각한다.",
        "8. 미래 직업 사회를 대비하기 위해 AI 교육은 필수적이다.",
        "9. AI 대전환(AX) 교육 시스템 사용법을 익히는 것은 쉽다.",
        "10. 전반적으로 AI 기반 학교 환경으로의 변화에 만족한다."
    ]
    
    responses = []
    options = {1: "매우 그렇지 않다", 2: "그렇지 않다", 3: "보통이다", 4: "그렇다", 5: "매우 그렇다"}
    
    with st.form("survey_form"):
        for i, q in enumerate(questions):
            score = st.radio(q, options=list(options.keys()), format_func=lambda x: f"{x} ({options[x]})", index=2, key=f"q_{i+1}")
            responses.append(score)
            
        submitted = st.form_submit_button("설문 제출하기")
        if submitted:
            conn = get_db_connection()
            cursor = conn.cursor()
            ktc_zone = pytz.timezone('Asia/Seoul')
            now_ktc = datetime.now(ktc_zone).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO inventory (userid, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (st.session_state['userid'], *responses, now_ktc))
            conn.commit()
            conn.close()
            st.success("🎉 실태조사 데이터가 안전하게 저장되었습니다. 참여해 주셔서 감사합니다!")
