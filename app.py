import streamlit as st
import covid19pandas as cod
import pandas as pd
import plotly.express as px

os.environ["COVID19PANDAS_CACHE_DIR"] = "./covid_data"

# Load COVID-19 dataset
global_df = cod.get_data_jhu()

# Select only relevant columns
global_df = global_df[["date", "Country/Region", "Province/State", "Combined_Key", "cases", "deaths", "recovered"]]

# Convert 'date' to datetime format for filtering
global_df["date"] = pd.to_datetime(global_df["date"])

# ---- Streamlit Dashboard ----
st.title("Interactive COVID-19 Global Cases Dashboard")

# Introduction
st.markdown("""
This dashboard provides an interactive way to explore global COVID-19 cases, deaths, and recoveries.
Use the filters below to select a date range and case type to visualize trends over time.
""")

# Sidebar filters
st.sidebar.header("General Filters")

# Date range selection
start_date = st.sidebar.date_input("Start Date", global_df["date"].min())
end_date = st.sidebar.date_input("End Date", global_df["date"].max())

# Ensure the start date is before the end date
if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")

# Case type selection
case_type = st.sidebar.selectbox("Select Case Type", ["cases", "deaths", "recovered"])

# Filter data based on user selection
filtered_df = global_df[(global_df["date"] >= pd.to_datetime(start_date)) & 
                        (global_df["date"] <= pd.to_datetime(end_date))]

# Aggregate data by date for visualization
df_grouped = filtered_df.groupby("date")[case_type].sum().reset_index()

# ---- Visualization ----
st.subheader(f"Trend of {case_type.capitalize()} from {start_date} to {end_date}")

# Create a line chart using Plotly
fig = px.line(df_grouped, x="date", y=case_type, title=f"Global {case_type.capitalize()} Trends",
              labels={"date": "Date", case_type: f"Number of {case_type.capitalize()}"},
              template="plotly_dark")

st.plotly_chart(fig)

# # Display filtered data table (optional)
# st.subheader("Filtered Data")
# st.write(filtered_df)

# ----------------- Comparison between countries ----------------- #
st.subheader("Comparative Analysis of COVID-19 Cases Between Countries")

st.markdown("""
In this section, you can compare the total number of COVID-19 cases, deaths, and recoveries between two selected countries.
The visualizations below will help you analyze and compare the impact of COVID-19 in different regions.
""")

# Sidebar country selection
st.sidebar.header("Country Selection")
country1 = st.sidebar.selectbox("Select First Country", global_df["Country/Region"].unique(), index=0)
country2 = st.sidebar.selectbox("Select Second Country", global_df["Country/Region"].unique(), index=1)

# Filter data for selected countries
selected_countries = [country1, country2]
country_df = global_df[global_df["Country/Region"].isin(selected_countries)]

# Aggregate total cases, deaths, and recoveries for each country
country_summary = country_df.groupby("Country/Region")[["cases", "deaths", "recovered"]].sum().reset_index()

# ---- Comparative Pie Charts ----
st.subheader(f"COVID-19 Cases Comparison: {country1} vs {country2}")

# Pie chart for cases
fig_cases = px.pie(country_summary, values="cases", names="Country/Region", title="Total Cases Comparison",
                    color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(fig_cases)

# Pie chart for deaths
fig_deaths = px.pie(country_summary, values="deaths", names="Country/Region", title="Total Deaths Comparison",
                    color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig_deaths)

# Pie chart for recovered
fig_recovered = px.pie(country_summary, values="recovered", names="Country/Region", title="Total Recovered Comparison",
                        color_discrete_sequence=px.colors.qualitative.Set1)
st.plotly_chart(fig_recovered)

# ---- Top N Countries Section ----
st.subheader("Top N Countries by COVID-19 Cases or Deaths")

st.markdown("""
Select the number of top affected countries and the case type (Cases or Deaths).
The graph below will display the most affected countries based on your selection.
""")

# Sidebar selection for number of top countries
n = st.sidebar.slider("Select Number of Top Countries (Global)", min_value=5, max_value=20, value=10, key="global_top_n_slider")

# Sidebar selection for case type
metric = st.sidebar.selectbox("Select Metric", ["cases", "deaths"])

# Get the latest available date in the dataset
latest_date = global_df["date"].max()

# Filter data for only the latest date
latest_df = global_df[global_df["date"] == latest_date]

# Get top N countries based on user selection
top_n_countries = latest_df.groupby("Country/Region")[metric].sum().reset_index()
top_n_countries = top_n_countries.sort_values(by=metric, ascending=False).head(n)

# Bar chart for top N countries
fig_top_n = px.bar(
    top_n_countries,
    x="Country/Region",
    y=metric,
    title=f"Top {n} Countries by {metric.capitalize()} (Latest Available Data: {latest_date.date()})",
    labels={"Country/Region": "Country", metric: f"Total {metric.capitalize()}"},
    color=metric,
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_top_n)

# ---- Daily New Cases Section ----
st.subheader("Daily New COVID-19 Cases, Deaths, and Recoveries")

st.markdown("""
This graph shows the daily increase in cases, deaths, or recoveries, rather than cumulative totals.
Observing daily trends helps identify surges, slowdowns, and patterns in the spread of COVID-19.
""")

# Sidebar selection for case type
daily_metric = st.sidebar.selectbox("Select Daily Metric", ["cases", "deaths", "recovered"])

# Compute daily change for the selected metric
global_df_sorted = global_df.sort_values(by=["Country/Region", "date"])  # Ensure data is sorted for correct calculations
global_df["daily_" + daily_metric] = global_df_sorted.groupby("Country/Region")[daily_metric].diff().fillna(0)

# Aggregate daily change globally
daily_global = global_df.groupby("date")["daily_" + daily_metric].sum().reset_index()

# Line chart for daily cases
fig_daily = px.line(
    daily_global,
    x="date",
    y="daily_" + daily_metric,
    title=f"Daily {daily_metric.capitalize()} Over Time",
    labels={"date": "Date", "daily_" + daily_metric: f"Daily {daily_metric.capitalize()}"},
    template="plotly_dark"
)

st.plotly_chart(fig_daily)

# ---- Daily New Cases for Top N Countries ----
st.subheader("Daily New COVID-19 Cases, Deaths, and Recoveries for Top N Countries")

st.markdown("""
This graph shows the daily increase in cases, deaths, or recoveries for the top affected countries.
You can select the number of countries and the case type to visualize trends across multiple regions.
""")

# Sidebar selection for case type
daily_metric = st.sidebar.selectbox("Select Daily Metric (Top N Countries)", ["cases", "deaths", "recovered"])

# Sidebar selection for number of top countries
# Sidebar selection for number of top countries (with unique key)
top_n = st.sidebar.slider("Select Number of Top Countries", min_value=5, max_value=20, value=10, key="top_n_countries_slider")

# Ensure data is sorted for correct daily change calculations
global_df_sorted = global_df.sort_values(by=["Country/Region", "date"])

# Compute daily change for each country
global_df["daily_" + daily_metric] = global_df_sorted.groupby("Country/Region")[daily_metric].diff().fillna(0)

# Get latest available data to rank top N countries
latest_date = global_df["date"].max()
latest_df = global_df[global_df["date"] == latest_date]

# Get top N countries based on total cases, deaths, or recovered
top_n_countries = latest_df.groupby("Country/Region")[daily_metric].sum().reset_index()
top_n_countries = top_n_countries.sort_values(by=daily_metric, ascending=False).head(top_n)["Country/Region"]

# Filter global data for only these top N countries
filtered_top_n_df = global_df[global_df["Country/Region"].isin(top_n_countries)]

# Line chart for daily cases of top N countries
fig_daily_top_n = px.line(
    filtered_top_n_df,
    x="date",
    y="daily_" + daily_metric,
    color="Country/Region",
    title=f"Daily {daily_metric.capitalize()} in Top {top_n} Countries",
    labels={"date": "Date", "daily_" + daily_metric: f"Daily {daily_metric.capitalize()}", "Country/Region": "Country"},
    template="plotly_dark"
)

st.plotly_chart(fig_daily_top_n)


# ---- Country-Specific Trends ----
st.subheader("COVID-19 Trends for a Selected Country")

# Information box
st.info("""
Understanding daily trends for a specific country helps in identifying infection surges, recovery rates, 
and effectiveness of interventions. It provides a clearer picture than cumulative numbers alone.
""")

# Sidebar selection for country
selected_country = st.sidebar.selectbox("Select a Country", global_df["Country/Region"].unique())

# Sidebar selection for case type
selected_metric = st.sidebar.selectbox("Select Data Type", ["cases", "deaths", "recovered"])

# Filter data for the selected country
country_data = global_df[global_df["Country/Region"] == selected_country][["date", selected_metric]]

# Ensure data is sorted before computing daily changes
country_data = country_data.sort_values(by="date")

# Compute daily new cases
country_data[f"new_{selected_metric}"] = country_data[selected_metric].diff().fillna(0)

# Reshape data for plotting
country_data_melted = country_data.melt(id_vars="date", var_name="count_type", value_name="count")

# Line chart visualization
fig_country = px.line(
    country_data_melted,
    x="date",
    y="count",
    color="count_type",
    title=f"COVID-19 {selected_metric.capitalize()} Trends in {selected_country}",
    labels={"date": "Date", "count": "Number of Cases", "count_type": "Type"},
    template="plotly_dark"
)

st.plotly_chart(fig_country)

#-----------Heat Map of the World Map------------

st.subheader("World Map of COVID-19 Cases, Deaths, and Recoveries")

fig = px.choropleth(global_df, 
                     locations="Country/Region", 
                     locationmode="country names",
                     color="cases",
                     hover_name="Country/Region",
                     color_continuous_scale="Reds",
                     title="COVID-19 Cases Heatmap")

st.plotly_chart(fig)
