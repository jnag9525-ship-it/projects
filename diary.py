import calendar
import json
import os
from datetime import date

import pandas as pd
import streamlit as st


CSV_PATH = "diary.csv"
SETTINGS_PATH = "settings.json"
COLUMNS = ["날짜", "제목", "내용", "날씨", "작성자", "기분", "먹은 음식"]
DEFAULT_SETTINGS = {"author": "", "theme": "파랑", "last_viewed_date": ""}
THEMES = {
    "파랑": "#2878B5",
    "초록": "#39845A",
    "보라": "#7952A3",
    "주황": "#D9822B",
    "빨강": "#C74440",
}


def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, encoding="utf-8") as settings_file:
            saved_settings = json.load(settings_file)
        if not isinstance(saved_settings, dict):
            raise ValueError("Settings must be a JSON object")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        st.warning("설정 파일이 손상되어 기본값으로 초기화했어요.")
        return DEFAULT_SETTINGS.copy()

    return {**DEFAULT_SETTINGS, **saved_settings}


def save_settings(settings):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, ensure_ascii=False, indent=4)


settings = load_settings()
first_visit = not settings.get("last_viewed_date")
today = date.today().isoformat()
settings["last_viewed_date"] = today

with st.sidebar:
    st.subheader("설정")
    author = st.text_input("작성자 이름", value=settings.get("author", ""))
    if st.button("저장"):
        settings["author"] = author
        st.success("이름이 저장되었어요!")

    theme_options = list(THEMES)
    current_theme = settings.get("theme", "파랑")
    if current_theme not in theme_options:
        current_theme = "파랑"
    theme = st.selectbox(
        "테마 색상",
        theme_options,
        index=theme_options.index(current_theme),
    )

settings["theme"] = theme
save_settings(settings)

st.markdown(
    f'<div style="height: 12px; background-color: {THEMES[theme]}; '
    'border-radius: 4px; margin-bottom: 1rem;"></div>',
    unsafe_allow_html=True,
)

st.title("📔 나의 일기장")

title = st.text_input("제목")
content = st.text_area("내용", height=150)
weather = st.selectbox("오늘의 날씨", ["맑음", "흐림", "비", "눈", "바람"])
mood = st.selectbox(
    "오늘의 기분",
    ["😊 행복", "😴 피곤", "😡 화남", "🥺 우울", "😐 보통", "😌 평온", "🤩 신남"],
)
food = st.text_area("오늘 먹은 음식", height=100)

if st.button("저장"):
    entry = pd.DataFrame(
        [[today, title, content, weather, settings.get("author", ""), mood, food]],
        columns=COLUMNS,
    )
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        diaries = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        diaries = diaries.reindex(columns=COLUMNS, fill_value="")
        entry = pd.concat([diaries, entry], ignore_index=True)
    entry.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    st.success("일기가 저장되었어요!")

if os.path.exists(CSV_PATH):
    diaries = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
else:
    diaries = pd.DataFrame(columns=COLUMNS)

diaries = diaries.reindex(columns=COLUMNS, fill_value="")

if diaries.empty:
    st.write("아직 작성된 일기가 없어요.")
else:
    st.subheader("작성한 일기")
    editor_data = diaries.assign(삭제=False)
    edited_diaries = st.data_editor(
        editor_data,
        column_config={
            "삭제": st.column_config.CheckboxColumn("삭제", help="삭제할 일기를 선택하세요.")
        },
        disabled=COLUMNS,
        hide_index=True,
        key="diary_entries",
    )
    if st.button("선택한 일기 삭제"):
        selected = edited_diaries["삭제"].fillna(False)
        if selected.any():
            diaries = diaries.drop(index=edited_diaries.index[selected]).reset_index(drop=True)
            diaries.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
            st.rerun()
        else:
            st.warning("삭제할 일기를 먼저 선택해주세요.")

def select_calendar_date(selected_date):
    st.session_state["calendar_date"] = selected_date
    st.session_state["selected_calendar_date"] = selected_date


st.subheader("일기 달력")
if "calendar_date" not in st.session_state:
    st.session_state["calendar_date"] = date.today()
calendar_date = st.date_input("달력 기준 날짜", key="calendar_date")
year, month = calendar_date.year, calendar_date.month
st.caption(f"{year}년 {month}월 기록 건수")

daily_counts = (
    pd.to_datetime(diaries["날짜"], errors="coerce")
    .dt.strftime("%Y-%m-%d")
    .value_counts()
    .to_dict()
)
weekday_columns = st.columns(7)
for column, weekday in zip(weekday_columns, ["월", "화", "수", "목", "금", "토", "일"]):
    column.caption(weekday)

selected_calendar_date = st.session_state.get("selected_calendar_date")
for week in calendar.monthcalendar(year, month):
    day_columns = st.columns(7)
    for column, day in zip(day_columns, week):
        if day == 0:
            continue
        day_date = date(year, month, day)
        day_key = day_date.isoformat()
        count = daily_counts.get(day_key, 0)
        column.button(
            f"{day}일 · {count}건",
            key=f"calendar_day_{day_key}",
            help=f"{day_key} 일기 보기",
            type="primary" if day_date == selected_calendar_date else "secondary",
            width="stretch",
            on_click=select_calendar_date,
            args=(day_date,),
        )

selected_calendar_date = st.session_state.get("selected_calendar_date")
if selected_calendar_date:
    st.subheader(f"{selected_calendar_date.isoformat()} 일기")
    selected_diaries = diaries[diaries["날짜"].astype(str) == selected_calendar_date.isoformat()]
    if selected_diaries.empty:
        st.info("이 날짜에는 작성된 일기가 없어요.")
    else:
        st.dataframe(selected_diaries, hide_index=True)

if first_visit:
    st.write("처음 방문이에요! 일기를 써봐요 🌱")
else:
    st.write(f"마지막으로 일기를 확인한 날: {today}")
