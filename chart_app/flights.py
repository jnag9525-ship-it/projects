import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="✈️ 항공 승객 분석", layout="wide")

flights = sns.load_dataset("flights")
month_order = list(flights["month"].cat.categories)
month_numbers = {month: number for number, month in enumerate(month_order, start=1)}

st.title("✈️ 항공 승객 분석")

metric_columns = st.columns(3)
metric_columns[0].metric("총 행 수", f"{len(flights):,}")
metric_columns[1].metric(
    "연도 범위",
    f"{flights['year'].min()}–{flights['year'].max()}",
)
metric_columns[2].metric("최대 승객 수", f"{flights['passengers'].max():,}")

month_range = st.sidebar.slider(
    "월 범위",
    min_value=1,
    max_value=12,
    value=(1, 12),
    format="%d월",
)

filtered_flights = flights[
    flights["month"]
    .map(month_numbers)
    .astype("int64")
    .between(month_range[0], month_range[1])
]
yearly_passengers = (
    filtered_flights.groupby("year", as_index=False, observed=True)["passengers"]
    .mean()
    .rename(columns={"passengers": "평균 승객 수"})
    .sort_values("year")
)
yearly_passengers["3년 이동평균"] = yearly_passengers["평균 승객 수"].rolling(
    window=3
).mean()
yearly_chart_data = yearly_passengers.melt(
    id_vars="year",
    value_vars=["평균 승객 수", "3년 이동평균"],
    var_name="구분",
    value_name="승객 수",
)

st.subheader("연도별 평균 승객 수")
yearly_fig = px.line(
    yearly_chart_data,
    x="year",
    y="승객 수",
    color="구분",
    line_dash="구분",
    line_dash_map={"평균 승객 수": "solid", "3년 이동평균": "dot"},
    labels={"year": "연도", "승객 수": "평균 승객 수", "구분": ""},
)
st.plotly_chart(yearly_fig, use_container_width=True)

monthly_average = (
    flights.groupby("month", as_index=False, observed=True)["passengers"]
    .mean()
    .rename(columns={"passengers": "평균 승객 수"})
)
monthly_average["month"] = pd.Categorical(
    monthly_average["month"], categories=month_order, ordered=True
)
monthly_average = monthly_average.sort_values("month")

st.subheader("월별 평균 승객 수")
monthly_bar_fig = px.bar(
    monthly_average,
    x="month",
    y="평균 승객 수",
    category_orders={"month": month_order},
    labels={"month": "월"},
)
st.plotly_chart(monthly_bar_fig, use_container_width=True)

st.subheader("월별 승객 수 분포")
monthly_box_fig = px.box(
    flights,
    x="month",
    y="passengers",
    category_orders={"month": month_order},
    labels={"month": "월", "passengers": "승객 수"},
)
st.plotly_chart(monthly_box_fig, use_container_width=True)

passenger_pivot = flights.pivot_table(
    index="year",
    columns="month",
    values="passengers",
    aggfunc="mean",
    observed=True,
).reindex(columns=month_order)

st.subheader("연도·월별 승객 수")
heatmap_fig = px.imshow(
    passenger_pivot,
    text_auto=".0f",
    x=passenger_pivot.columns,
    y=passenger_pivot.index,
    color_continuous_scale="Blues",
    labels={"x": "월", "y": "연도", "color": "승객 수"},
    aspect="auto",
)
st.plotly_chart(heatmap_fig, use_container_width=True)
