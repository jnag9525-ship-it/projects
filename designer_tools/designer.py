import streamlit as st


st.set_page_config(
    page_title="디자이너 컬러 툴킷",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 디자이너 컬러 툴킷")
st.write("색을 고르고, 이미지에서 팔레트를 찾고, 다양한 필터를 적용해 보세요.")

apps = [
    (
        "🎚️",
        "컬러 피커",
        "RGB 값을 조정해 나만의 기본색·보조색·배경색 테마를 만들어 보세요.",
        "pages/01_color_picker.py",
    ),
    (
        "🖼️",
        "이미지 컬러 추출",
        "이미지에서 가장 많이 사용된 색상 5개와 컬러 테마를 확인하세요.",
        "pages/02_image_color.py",
    ),
    (
        "🪄",
        "이미지 필터",
        "흑백, 세피아, 블러 등 필터를 적용하고 결과를 다운로드하세요.",
        "pages/03_image_filter.py",
    ),
]

columns = st.columns(3)
for column, (icon, title, description, page) in zip(columns, apps, strict=True):
    with column:
        with st.container(border=True):
            st.subheader(f"{icon} {title}")
            st.write(description)
            st.page_link(page, label="앱 열기", icon="➡️")
