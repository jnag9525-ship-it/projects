import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="항공 승객 · 레스토랑 팁 분석", layout="wide")

flights = sns.load_dataset("flights")
month_order = list(flights["month"].cat.categories)
month_numbers = {month: number for number, month in enumerate(month_order, start=1)}

tips = sns.load_dataset("tips")
group_options = {
    "성별(sex)": "sex",
    "흡연여부(smoker)": "smoker",
    "요일(day)": "day",
    "시간대(time)": "time",
}

st.title("데이터 분석 대시보드")
flights_tab, tips_tab = st.tabs(["✈️ 항공 승객 분석", "🍽️ 레스토랑 팁 분석"])

month_range = st.sidebar.slider(
    "항공 분석 월 범위",
    min_value=1,
    max_value=12,
    value=(1, 12),
    format="%d월",
)
scatter_color_label = st.sidebar.selectbox(
    "팁 산점도 색상 기준",
    options=["성별(sex)", "흡연여부(smoker)", "요일(day)", "시간대(time)"],
)
bar_group_label = st.sidebar.selectbox(
    "팁 막대차트 그룹 기준",
    options=["요일(day)", "성별(sex)", "시간대(time)", "흡연여부(smoker)"],
)

with flights_tab:
    metric_columns = st.columns(3)
    metric_columns[0].metric("총 행 수", f"{len(flights):,}")
    metric_columns[1].metric(
        "연도 범위",
        f"{flights['year'].min()}–{flights['year'].max()}",
    )
    metric_columns[2].metric("최대 승객 수", f"{flights['passengers'].max():,}")

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

with tips_tab:
    metric_columns = st.columns(4)
    metric_columns[0].metric("총 데이터 수", f"{len(tips):,}")
    metric_columns[1].metric("평균 식사 금액", f"${tips['total_bill'].mean():.2f}")
    metric_columns[2].metric("평균 팁 금액", f"${tips['tip'].mean():.2f}")
    average_tip_rate = tips["tip"].div(tips["total_bill"]).mean() * 100
    metric_columns[3].metric("평균 팁 비율", f"{average_tip_rate:.2f}%")
    st.dataframe(tips.describe(), use_container_width=True)

    st.subheader("금액 vs 팁")
    scatter_color_column = group_options[scatter_color_label]
    scatter_fig = px.scatter(
        tips,
        x="total_bill",
        y="tip",
        color=scatter_color_column,
        trendline="ols",
        hover_data={
            "total_bill": ":.2f",
            "tip": ":.2f",
            "size": True,
        },
        labels={
            "total_bill": "식사 금액 ($)",
            "tip": "팁 금액 ($)",
            "size": "인원수",
            scatter_color_column: scatter_color_label,
        },
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.subheader("조건별 합계")
    bar_group_column = group_options[bar_group_label]
    bill_totals = (
        tips.groupby(bar_group_column, observed=True)["total_bill"]
        .sum()
        .reset_index(name="총 식사 금액")
        .rename(columns={bar_group_column: "그룹"})
    )
    bill_totals["합계 표시"] = bill_totals["총 식사 금액"].map(
        lambda amount: f"${amount:.2f}"
    )
    bar_fig = px.bar(
        bill_totals,
        x="그룹",
        y="총 식사 금액",
        text="합계 표시",
        title="선택 기준별 총 식사 금액 합계",
        labels={"그룹": bar_group_label, "총 식사 금액": "총 식사 금액 ($)"},
    )
    bar_fig.update_traces(textposition="outside")
    st.plotly_chart(bar_fig, use_container_width=True)
