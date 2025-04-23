import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title="COVID-19 Dashboard - Sri Lanka", layout="wide")

def load_data():
    df = pd.read_csv("monthly data.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()


st.title ("COVID-19 Dashboard - Sri Lanka")
st.markdown("This dashboard provides insights on COVID-19 cases across different districs in Sri Lanka.")

with st.expander("View raw data"):
    st.dataframe(df)

#sliderbar filter
st.sidebar.header("Filter Data")
districts = st.sidebar.multiselect(
    "Select Distric(s):", options=sorted(df["Distric"].unique()), default=sorted(df["Distric"].unique()))
months = st.sidebar.multiselect(
    "Select Month(s):", options=sorted(df["Month"].unique()), default=sorted(df["Month"].unique()))

#Filtered data
filtered_df = df[(df["Distric"].isin(districts)) & (df["Month"].isin(months))]

#Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizations", "📊 Heatmap", "🧾 Data Table", "⬇️ Export"])

#Key matrics
with tab1:
    st.subheader("Key Metrics")
    total_cases = filtered_df["Cases"].sum()
    avg_cases = filtered_df["Cases"].mean()
    most_affected = filtered_df.groupby("Distric")["Cases"].sum().idxmax()
    highest_month = filtered_df.groupby("Month")["Cases"].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cases", f"{total_cases:,}")
    col2.metric("Average Monthly", f"{avg_cases:.2f}")
    col3.metric("Most Affected District", most_affected)
    col4.metric("Month with Highest Cases", highest_month)

    #Line chart
    st.markdown("### Monthly Trend by District")
    line_fig =px.line(filtered_df,x="Month", y="Cases", color="Distric", markers=True)
    st.plotly_chart(line_fig, use_container_width=True)

    #Bar chart
    st.markdown("### Total Cases by District")
    bar_df = filtered_df.groupby("Distric")["Cases"].sum().reset_index().sort_values(by="Cases", ascending=False)
    bar_fig = px.bar(bar_df, x="Distric", y="Cases", color="Distric", text="Cases")
    st.plotly_chart(bar_fig, use_container_width=True)

    #Pie chart
    st.markdown("### Case Distribution by District")
    pie_fig = px.pie(bar_df, names="Distric", values="Cases", title="Proportion of Cases by District")

    top_10 = bar_df.sort_values(by="Cases", ascending=False). head(10)
    other_sum = bar_df.sort_values(by="Cases", ascending=False).iloc[10:]["Cases"].sum()
    top_10.loc[len(top_10.index)] = ['others', other_sum]

    pie_fig = px.pie(
        top_10,
        names="Distric",
        values="Cases",
        title="Proportion of Cases by Top 10 Districts",
        hole=0.3)
    pie_fig.update_traces(textinfo='percent+label')
    st.plotly_chart(pie_fig, use_container_width=True)


#Heatmap
with tab2:
    st.subheader("Monthly Cases Heatmap by District")

    pivot_df = filtered_df.pivot_table(index="Distric", columns="Month", values="Cases", aggfunc="sum").fillna(0)
    pivot_df = pivot_df.sort_index(axis=1)

    fig, ax = plt.subplots(figsize=(14,6))
    sns.heatmap(pivot_df, annot=True, fmt=".0f", cmap="OrRd", linewidths=0.5, ax=ax)
    plt.title("COVID-19 Monthly Case Distribution by District", fontsize=16)
    plt.xlabel("Month")
    plt.ylabel("District")
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    st.pyplot(fig)





