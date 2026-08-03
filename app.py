import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(
    page_title="Addis Ababa Traffic Accident Analysis",
    layout="wide"
)

# Load your cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_rta_data.csv")
    return df
df2 = load_data()

st.title("🚦 Addis Ababa Traffic Accident Analysis")
st.markdown("Exploratory analysis of road traffic accidents (RTA dataset)")

# Sidebar filters
st.sidebar.header("Filters")

selected_days = st.sidebar.multiselect(
    "Day of Week",
    options=df2["Day_of_week"].unique(),
    default=df2["Day_of_week"].unique()
)

selected_severity = st.sidebar.multiselect(
    "Accident Severity",
    options=df2["Accident_severity"].unique(),
    default=df2["Accident_severity"].unique()
)

df_filtered = df2[
    (df2["Day_of_week"].isin(selected_days)) &
    (df2["Accident_severity"].isin(selected_severity))
]

st.sidebar.markdown(f"**Showing {len(df_filtered)} of {len(df2)} records**")

# Q1
st.header("1. Total Accidents Recorded")
st.metric("Total Accidents", len(df_filtered))

# Q2
st.header("2. Top Locations by Accident Count")
location_table = (df_filtered["Area_accident_occured"]
                   .value_counts()
                   .head(10)
                   .rename("Accident_Count")
                   .to_frame())
col1, col2 = st.columns([1, 2])
with col1:
    st.dataframe(location_table)
with col2:
    st.bar_chart(location_table)

# Q3
st.header("3. Accidents by Hour of Day")
df_filtered["Hour"] = pd.to_datetime(df_filtered["Time"], format="%H:%M:%S", errors="coerce").dt.hour
hourly = df_filtered.groupby("Hour", observed=True).size().sort_index()
st.line_chart(hourly)

# Q4
st.header("4. Accidents by Day of Week")
day_table = df_filtered["Day_of_week"].value_counts()
st.bar_chart(day_table)

# Q5
st.header("5. Leading Causes of Accidents")
cause_table = df_filtered["Cause_of_accident"].value_counts().head(10)
st.bar_chart(cause_table)

# Q6
st.header("6. Weather Conditions vs Severity")
weather_severity = (df_filtered.groupby("Weather_conditions", observed=True)["Accident_severity"]
                     .value_counts().unstack(fill_value=0))
st.dataframe(weather_severity)

# Q7
st.header("7. Accident Severity Distribution")
severity_counts = df_filtered["Accident_severity"].value_counts()
fig, ax = plt.subplots()
ax.pie(severity_counts, labels=severity_counts.index, autopct="%1.1f%%")
st.pyplot(fig)

# Q8
st.header("8. Vehicle Types Most Involved")
vehicle_table = df_filtered["Type_of_vehicle"].value_counts().head(10)
st.bar_chart(vehicle_table)

# Q9
st.header("9. Road Users Most Affected")
col1, col2 = st.columns(2)
with col1:
    st.subheader("By Sex")
    st.bar_chart(df_filtered["Sex_of_casualty"].value_counts())
with col2:
    st.subheader("By Age Band")
    st.bar_chart(df_filtered["Age_band_of_casualty"].value_counts())