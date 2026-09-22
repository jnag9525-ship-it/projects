import streamlit as st

# 페이지 설정
st.set_page_config(page_title="자기소개 앱", page_icon="👋", layout="centered")

# 타이틀
st.title("👋 자기소개 앱")
st.write("아래 항목을 입력하고 버튼을 눌러 자기소개를 확인해 보세요!")

st.divider()

# 사용자 입력 양식
with st.form(key="intro_form"):
    name = st.text_input("이름", placeholder="예: 홍길동")
    job = st.text_input("직업", placeholder="예: 개발자")
    hobby = st.text_input("취미", placeholder="예: 독서 및 영화 감상")

    # 제출 버튼
    submit_button = st.form_submit_button(label="소개 보기")

# 버튼 클릭 시 출력 처리
if submit_button:
    # 빈 값이 있는지 확인
    if not name.strip() or not job.strip() or not hobby.strip():
        st.warning("⚠️ 모든 항목(이름, 직업, 취미)을 입력해 주세요.")
    else:
        st.success("✨ 자기소개가 완성되었습니다!")
        st.info(f"저는 **{job}**으로 일하는 **{name}**입니다. 취미는 **{hobby}**예요.")
        