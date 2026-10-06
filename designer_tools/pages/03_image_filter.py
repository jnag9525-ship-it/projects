from pathlib import Path
import sys

from PIL import ImageFilter, ImageOps
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from designer_tools.utils import image_to_png_bytes, load_uploaded_image


st.set_page_config(page_title="이미지 필터", page_icon="🪄", layout="wide")
st.title("🪄 이미지 필터")
st.write("이미지를 업로드하고 필터를 적용한 다음 PNG 파일로 다운로드하세요.")

uploaded_file = st.file_uploader(
    "이미지 업로드",
    type=["png", "jpg", "jpeg", "webp", "bmp"],
)

if uploaded_file is not None:
    try:
        original = load_uploaded_image(uploaded_file)
    except ValueError as error:
        st.error(str(error))
    else:
        filter_name = st.selectbox(
            "필터 선택",
            ["원본", "흑백", "세피아", "블러", "선명하게", "반전"],
        )
        if filter_name == "원본":
            filtered = original
        elif filter_name == "흑백":
            filtered = ImageOps.grayscale(original).convert("RGB")
        elif filter_name == "세피아":
            grayscale = ImageOps.grayscale(original)
            filtered = ImageOps.colorize(
                grayscale,
                black="#3B2416",
                white="#F4D6A0",
            )
        elif filter_name == "블러":
            radius = st.slider("블러 강도", min_value=1, max_value=20, value=5)
            filtered = original.filter(ImageFilter.GaussianBlur(radius=radius))
        elif filter_name == "선명하게":
            filtered = original.filter(ImageFilter.SHARPEN)
        else:
            filtered = ImageOps.invert(original)

        preview_columns = st.columns(2)
        preview_columns[0].image(
            original,
            caption="원본",
            use_container_width=True,
        )
        preview_columns[1].image(
            filtered,
            caption=f"결과: {filter_name}",
            use_container_width=True,
        )
        st.download_button(
            "결과 이미지 다운로드",
            data=image_to_png_bytes(filtered),
            file_name="filtered_image.png",
            mime="image/png",
        )
