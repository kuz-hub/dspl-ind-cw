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
    df["Distric"] = df["Distric"].astype(str).str.strip().str.title()
    return df

df = load_data()



st.title ("COVID-19 Dashboard - Sri Lanka")
st.markdown("This dashboard provides insights on COVID-19 cases across different districs in Sri Lanka.")

with st.expander("View raw data"):
    st.dataframe(df)

#sliderbar filter
st.sidebar.header("Filter Data")
districts = st.sidebar.multiselect(
    "Select Distric(s):", options=sorted(df["Distric"].unique()), default=[]
    )
months = st.sidebar.multiselect(
    "Select Month(s):", options=sorted(df["Month"].unique()), default=[]
    )


#Filtered data
filtered_df = df[(df["Distric"].isin(districts)) & (df["Month"].isin(months))]

#Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizations", "📊 Heatmap", "🧾 Data Table", "⬇️ Export"])

#Key matrics
with tab1:
    total_cases = df["Cases"].sum()
    avg_cases = df.groupby(["Year", "Month"])["Cases"].sum().mean()

    most_affected = df.groupby("Distric")["Cases"].sum().idxmax()
    
    df["Month_Year"] = df["Month"] + " " + df["Year"].astype(str)
    highest_month = df.groupby("Month_Year")["Cases"].sum().idxmax() 

    # Display Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cases", f"{total_cases:,}")
    col2.metric("Average Monthly", f"{avg_cases:.2f}")
    col3.metric("Most Affected District", most_affected)
    col4.metric("Month with Highest Cases", highest_month)



    #Line chart 
    # Line Chart: Top 10 or All Districts Toggle
    st.markdown("### 📉 Monthly COVID-19 Cases by Districts")
    
    show_all = st.sidebar.checkbox("Show All Districts in Line Chart", value=False)
    
    if districts or months:
        if show_all:
            display_df = filtered_df.copy()
            chart_title = "Monthly COVID-19 Cases - All Districts"
        else:
            top_10_districts = (
            filtered_df.groupby("Distric")["Cases"].sum()
            .sort_values(ascending=False)
            .head(10)
            .index.tolist()
            )
            display_df = filtered_df[filtered_df["Distric"].isin(top_10_districts)]
            chart_title = "Monthly COVID-19 Cases - Top 10 Districts"
    else:
        if show_all:
            display_df = df.copy()
            chart_title = "Monthly COVID-19 Cases - All Districts"
        else:
            top_10_districts = (
                df.groupby("Distric")["Cases"].sum()
                .sort_values(ascending=False)
                .head(10)
                .index.tolist()
            )
            display_df = df[df["Distric"].isin(top_10_districts)]
            chart_title = "Monthly COVID-19 Cases - Top 10 Districts (Default)"
     

    line_fig = px.line(
        display_df,
        x="Month",
        y="Cases",
        color="Distric",
        markers=True,
        title=chart_title,
        color_discrete_sequence=px.colors.qualitative.Set2  # Use a calm, distinct palette
        )
    
    line_fig.update_layout(
        legend_title="District",
        template="plotly_white",
        xaxis_title="Month",
        yaxis_title="Number of Cases",
        title_x=0.5
        )
    
    st.plotly_chart(line_fig, use_container_width=True)


    #Bar chart
    st.markdown("### Total Cases by District")

    if districts or months:
        base_df = filtered_df.copy()
        chart_title = "Total case by district (Filtered)"

    else:
        base_df = df.copy()
        chart_title = "Top 5 Districts by Total Cases"
    
    base_df = base_df[base_df["Distric"].notna()]
    base_df ["Cases"] = pd.to_numeric(base_df["Cases"], errors="coerce")
    base_df = base_df.dropna(subset=["Cases"])

    bar_df = base_df.groupby("Distric", as_index=False)["Cases"].sum()
    bar_df = bar_df.sort_values (by="Cases", ascending=False)

    if not (districts or months):
        bar_df = bar_df.head(5)

    
    bar_fig = px.bar(
        bar_df,
        x="Distric",
        y="Cases",
        color="Distric",
        text="Cases",
        title=chart_title
        )
    
    bar_fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
        )
    bar_fig.update_layout(
        xaxis_title="District",
        yaxis_title="Total Cases",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        template="plotly_white"
        )
    st.plotly_chart(bar_fig, use_container_width=True)

    #Pie ch-art
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
    st.subheader("🌡️ Monthly COVID-19 Cases Heatmap by District")

    # ✅ Reload the original dataset directly inside this block
    heatmap_df = pd.read_csv("monthly data.csv")
    heatmap_df.columns = heatmap_df.columns.str.strip()

    # ✅ Convert Month-Year to datetime
    heatmap_df["Month"] = pd.to_datetime(heatmap_df["Month"] + "-" + heatmap_df["Year"].astype(str), format="%B-%Y")
    heatmap_df = heatmap_df.sort_values(["Year", "Month"])

    # ✅ Create pivot table for heatmap
    pivot_df = heatmap_df.pivot_table(index="Distric", columns="Month", values="Cases", aggfunc="sum").fillna(0)
    pivot_df.columns = pivot_df.columns.strftime("%b-%y")

    # ✅ Plot the heatmap
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.heatmap(
        pivot_df,
        annot=True,
        fmt=".0f",
        cmap="YlOrRd",
        linewidths=0.3,
        linecolor='white',
        cbar_kws={'label': 'Number of Cases'},
        annot_kws={"size": 8}
    )

    plt.title("COVID-19 Monthly Case Distribution by District", fontsize=18, pad=20)
    plt.xlabel("Month", fontsize=14)
    plt.ylabel("District", fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()

    st.pyplot(fig)


#Data table
with tab3:
    st.subheader("Filtered Data Table")

    if districts or months:
        table_df = filtered_df.copy()
    else:
        table_df = df.copy()
        
    st.dataframe(table_df.sort_values(by=["Year", "Month"]))

#Export
with tab4:
    st.subheader("Dowload Filtered Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download csv", data=csv, file_name='filtered_covid_data.csv', mime='text/csv')

    st.expander("Insights Summary", expanded=True)

    if districts or months:
        base_df = filtered_df.copy()
    else:
        base_df = df.copy()

    if not base_df.empty:
        base_df = base_df.sort_values(by="Month")  # ensure sorted for iloc[-1]
        latest_month = base_df["Month"].iloc[-1]
        last_month_df = base_df[base_df["Month"] == latest_month]

        top_district = last_month_df.sort_values("Cases", ascending=False).iloc[0]["Distric"]
        top_district_cases = last_month_df.sort_values("Cases", ascending=False).iloc[0]["Cases"]

        st.markdown(f"🧠 In **{latest_month}**, the district with the highest cases was **{top_district}** with **{int(top_district_cases):,} cases**.")

        monthly_trend = base_df.groupby("Month")["Cases"].sum().diff().dropna()
        if not monthly_trend.empty:
            trend_direction = "📈 Increased" if monthly_trend.iloc[-1] > 0 else "📉 Decreased"
            st.markdown(f"{trend_direction} cases compared to the previous month.")         



with tab2:
    # Map Section
    st.subheader("📍 COVID-19 Case Distribution on Map")

    if districts or months:
        map_df = filtered_df.copy()
    else:
        map_df = df.copy()

    # Clean up
    map_df = map_df[map_df["Distric"].notna()]
    map_df["Distric"] = map_df["Distric"].astype(str).str.strip().str.title()

    # Use latest month’s data only for mapping
    latest_map_month = map_df["Month"].max()
    latest_map_df = map_df[map_df["Month"] == latest_map_month]


    # Coordinates
    district_coords = {
        "Ampara": [7.2910, 81.6725],
        "Anuradhapura": [8.3114, 80.4037],
        "Badulla": [6.9934, 81.0540],
        "Batticaloa": [7.7333, 81.7000],
        "Colombo": [6.9271, 79.8612],
        "Galle": [6.0535, 80.2210],
        "Gampaha": [7.0855, 80.0088],
        "Hambantota": [6.1240, 81.1185],
        "Jaffna": [9.6615, 80.0255],
        "Kalutara": [6.5854, 79.9607],
        "Kandy": [7.2906, 80.6337],
        "Kegalle": [7.2514, 80.3464],
        "Kilinochchi": [9.3962, 80.4071],
        "Kurunegala": [7.4863, 80.3647],
        "Mannar": [8.9763, 79.9044],
        "Matale": [7.4675, 80.6234],
        "Matara": [5.9549, 80.5550],
        "Monaragala": [6.8728, 81.3509],
        "Mullaitivu": [9.2670, 80.8128],
        "Nuwara Eliya": [6.9708, 80.7829],
        "Polonnaruwa": [7.9403, 81.0188],
        "Puttalam": [8.0352, 79.8452],
        "Ratnapura": [6.7050, 80.3847],
        "Trincomalee": [8.5874, 81.2152],
        "Vavuniya": [8.7510, 80.4970]
    }

    map_df["lat"] = map_df["Distric"].map(lambda d: district_coords.get(d, [None, None])[0])
    map_df["lon"] = map_df["Distric"].map(lambda d: district_coords.get(d, [None, None])[1])
    map_df = map_df.dropna(subset=["lat", "lon"])

    map_fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="Cases",
        color="Distric",
        hover_name="Distric",
        hover_data={"Cases": True, "lat": False, "lon": False},
        zoom=6,
        height=500,
        mapbox_style="carto-positron"
    )

    st.plotly_chart(map_fig, use_container_width=True)
