import streamlit as st

# Check login status
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.error("🔒 접근 권한이 없습니다. 랜딩페이지(run.py)에서 로그인을 먼저 완료해 주세요.")
    st.stop()

st.subheader('머신러닝의 개념')
st.write("정상적으로 인증된 사용자 분들에게만 제공되는 세부 콘텐츠 영역입니다.")
