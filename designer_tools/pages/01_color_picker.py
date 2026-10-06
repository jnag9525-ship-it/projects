import colorsys
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from designer_tools.utils import render_color_theme, to_hex


def classify_color_family(color: tuple[int, int, int]) -> str:
    if max(color) - min(color) <= 24:
        return "무채색 계열"

    hue = colorsys.rgb_to_hsv(*(channel / 255 for channel in color))[0] * 360
    if hue < 15 or hue >= 345:
        return "빨강 계열"
    if hue < 75:
        return "노랑 계열"
    if hue < 165:
        return "초록 계열"
    if hue < 255:
        return "파랑 계열"
    return "보라 계열"


st.set_page_config(page_title="컬러 피커", page_icon="🎚️", layout="wide")
st.title("🎚️ 컬러 피커")
st.write("RGB 슬라이더를 움직여 원하는 색과 어울리는 테마를 찾아보세요.")

red_column, green_column, blue_column = st.columns(3)
red = red_column.slider("Red", min_value=0, max_value=255, value=92)
green = green_column.slider("Green", min_value=0, max_value=255, value=126)
blue = blue_column.slider("Blue", min_value=0, max_value=255, value=184)

primary = (red, green, blue)
hue, saturation, lightness = colorsys.rgb_to_hls(
    red / 255,
    green / 255,
    blue / 255,
)
secondary = tuple(
    round(channel * 255)
    for channel in colorsys.hls_to_rgb(
        (hue + 0.5) % 1,
        lightness,
        saturation,
    )
)
background = tuple(round(channel + (255 - channel) * 0.92) for channel in primary)

st.markdown(
    f"""
    <div style="background:{to_hex(primary)}; padding:24px; border-radius:12px;
                color:white; font-size:1.2rem;">
        선택한 색상&nbsp; <strong>{to_hex(primary)}</strong>
    </div>
    """,
    unsafe_allow_html=True,
)
st.info(f"색상 계열: **{classify_color_family(primary)}**")
render_color_theme(primary, secondary, background)
