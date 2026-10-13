import os
from datetime import date

import pandas as pd
import streamlit as st


CSV_PATH = "diary.csv"
COLUMNS = ["날짜", "제목", "내용", "날씨"]

st.title("📔 나의 일기장")

title = st.text_input("제목")
content = st.text_area("내용", height=150)
weather = st.selectbox("오늘의 날씨", ["맑음", "흐림", "비", "눈", "바람"])

if st.button("저장"):
    entry = pd.DataFrame(
        [[date.today().isoformat(), title, content, weather]],
        columns=COLUMNS,
    )
    write_header = not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0
    entry.to_csv(
        CSV_PATH,
        mode="a",
        header=write_header,
        index=False,
        encoding="utf-8-sig",
    )
    st.success("일기가 저장되었어요!")

if os.path.exists(CSV_PATH):
    diaries = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    st.dataframe(diaries)
else:
    st.write("아직 작성된 일기가 없어요.")
