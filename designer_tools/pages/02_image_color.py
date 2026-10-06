from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from designer_tools.utils import (
    extract_dominant_colors,
    load_uploaded_image,
    render_color_theme,
    to_hex,
)


st.set_page_config(page_title="이미지 컬러 추출", page_icon="🖼️", layout="wide")
st.title("🖼️ 이미지 컬러 추출")
st.write("이미지를 올리면 주요 색상 최대 5개를 찾아 컬러 테마로 정리합니다.")

uploaded_file = st.file_uploader(
    "이미지 업로드",
    type=["png", "jpg", "jpeg", "webp", "bmp"],
)

if uploaded_file is not None:
    try:
        image = load_uploaded_image(uploaded_file)
        colors = extract_dominant_colors(image)
    except ValueError as error:
        st.error(str(error))
    else:
        st.image(image, caption="업로드한 이미지", use_container_width=True)
        st.subheader("주요 색상 (최대 5개)")
        if len(colors) < 5:
            st.caption(
                f"서로 다른 색상이 {len(colors)}개 감지되어 해당 색상만 표시합니다."
            )
        swatches = st.columns(len(colors))
        for column, color in zip(swatches, colors, strict=True):
            hex_color = to_hex(color)
            column.markdown(
                f"""
                <div style="background:{hex_color}; height:100px; border-radius:10px;
                            border:1px solid rgba(0,0,0,.12);"></div>
                <div style="padding-top:6px"><code>{hex_color}</code></div>
                """,
                unsafe_allow_html=True,
            )
        primary = colors[0]
        secondary = (
            colors[1]
            if len(colors) > 1
            else tuple(255 - value for value in primary)
        )
        background = (
            colors[2]
            if len(colors) > 2
            else tuple(round(value + (255 - value) * 0.92) for value in primary)
        )
        render_color_theme(primary, secondary, background)
