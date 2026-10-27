import plotly.express as px
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="🍽️ 레스토랑 팁 분석", layout="wide")

tips = sns.load_dataset("tips")
group_options = {
    "성별(sex)": "sex",
    "흡연여부(smoker)": "smoker",
    "요일(day)": "day",
    "시간대(time)": "time",
}

st.title("🍽️ 레스토랑 팁 분석")

st.sidebar.subheader("차트 설정")
scatter_color_label = st.sidebar.selectbox(
    "산점도 색상 기준",
    options=["성별(sex)", "흡연여부(smoker)", "요일(day)", "시간대(time)"],
)
bar_group_label = st.sidebar.selectbox(
    "막대차트 그룹 기준",
    options=["요일(day)", "성별(sex)", "시간대(time)", "흡연여부(smoker)"],
)

st.subheader("기술 통계 요약")
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
