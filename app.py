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
    st.plotly_chart(pie_fig, use_container_width=True)







