from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError
import streamlit as st


def render_color_theme(
    primary: tuple[int, int, int],
    secondary: tuple[int, int, int],
    background: tuple[int, int, int],
) -> None:
    """Display three colors as labeled theme swatches."""
    st.subheader("컬러 테마")
    columns = st.columns(3)
    colors = [
        ("기본색", primary),
        ("보조색", secondary),
        ("배경색", background),
    ]
    for column, (label, color) in zip(columns, colors, strict=True):
        hex_color = to_hex(color)
        column.markdown(
            f"""
            <div style="background:{hex_color}; height:110px; border-radius:12px;
                        border:1px solid rgba(0,0,0,.12);"></div>
            <div style="padding-top:8px"><strong>{label}</strong><br>
                 <code>{hex_color}</code></div>
            """,
            unsafe_allow_html=True,
        )


def to_hex(color: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*color)


def load_uploaded_image(uploaded_file) -> Image.Image:
    """Open an uploaded image, apply its orientation, and normalize transparency."""
    try:
        with Image.open(uploaded_file) as source:
            image = ImageOps.exif_transpose(source).convert("RGBA")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(
            "이미지를 읽을 수 없습니다. 다른 이미지 파일을 선택해 주세요."
        ) from error

    white_background = Image.new("RGBA", image.size, "white")
    return Image.alpha_composite(white_background, image).convert("RGB")


def extract_dominant_colors(
    image: Image.Image, count: int = 5
) -> list[tuple[int, int, int]]:
    """Return the most frequent colors in a resized, quantized image."""
    thumbnail = image.copy()
    thumbnail.thumbnail((256, 256))
    quantized = thumbnail.quantize(
        colors=count,
        method=Image.Quantize.MEDIANCUT,
    )
    palette = quantized.getpalette()
    color_counts = quantized.getcolors(maxcolors=256)
    if palette is None or color_counts is None:
        raise ValueError("이미지에서 주요 색상을 추출하지 못했습니다.")

    color_counts.sort(reverse=True)
    return [
        tuple(palette[index * 3 : index * 3 + 3])
        for _, index in color_counts[:count]
    ]


def image_to_png_bytes(image: Image.Image) -> bytes:
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
