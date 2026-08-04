import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from scipy.stats import chi2_contingency

# Page setup
st.set_page_config(
    page_title="Addis Ababa Traffic Accident Analysis",
    layout="wide"
)

# A bold, distinct color sequence used across all charts for a colorful look
COLOR_SEQUENCE = px.colors.qualitative.Bold

# Load your cleaned data from the Data folder
@st.cache_data
def load_data():
    df = pd.read_csv("Data/cleaned_rta_data.csv")
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
                   .to_frame()
                   .reset_index())
location_table.columns = ["Area_accident_occured", "Accident_Count"]

col1, col2 = st.columns([1, 2])
with col1:
    st.dataframe(location_table.set_index("Area_accident_occured"))
with col2:
    fig = px.bar(
        location_table,
        x="Accident_Count",
        y="Area_accident_occured",
        orientation="h",
        color="Area_accident_occured",
        color_discrete_sequence=COLOR_SEQUENCE,
        title="Top 10 Locations by Accident Count"
    )
    fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width="stretch")

# Q3
st.header("3. Accidents by Hour of Day")
df_filtered["Hour"] = pd.to_datetime(
    df_filtered["Time"], format="%H:%M:%S", errors="coerce"
).dt.hour
hourly = (df_filtered.groupby("Hour", observed=True)
          .size()
          .reset_index(name="Accident_Count")
          .sort_values("Hour"))

fig = px.line(
    hourly,
    x="Hour",
    y="Accident_Count",
    markers=True,
    title="Accidents by Hour of Day",
    color_discrete_sequence=[COLOR_SEQUENCE[0]]
)
fig.update_traces(line=dict(width=3), marker=dict(size=8, color=COLOR_SEQUENCE[1]))
st.plotly_chart(fig, width="stretch")

# Q4
st.header("4. Accidents by Day of Week")
day_table = (df_filtered["Day_of_week"]
             .value_counts()
             .reset_index())
day_table.columns = ["Day_of_week", "Accident_Count"]

fig = px.bar(
    day_table,
    x="Day_of_week",
    y="Accident_Count",
    color="Day_of_week",
    color_discrete_sequence=COLOR_SEQUENCE,
    title="Accidents by Day of Week"
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

# Q5
st.header("5. Leading Causes of Accidents")
cause_table = (df_filtered["Cause_of_accident"]
               .value_counts()
               .head(10)
               .reset_index())
cause_table.columns = ["Cause_of_accident", "Accident_Count"]

fig = px.bar(
    cause_table,
    x="Accident_Count",
    y="Cause_of_accident",
    orientation="h",
    color="Cause_of_accident",
    color_discrete_sequence=COLOR_SEQUENCE,
    title="Top 10 Leading Causes of Accidents"
)
fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, width="stretch")

# Q6
st.header("6. Weather Conditions vs Severity")
weather_severity = (df_filtered.groupby("Weather_conditions", observed=True)["Accident_severity"]
                     .value_counts()
                     .unstack(fill_value=0))
st.dataframe(weather_severity)

weather_long = weather_severity.reset_index().melt(
    id_vars="Weather_conditions", var_name="Accident_severity", value_name="Count"
)
fig = px.bar(
    weather_long,
    x="Weather_conditions",
    y="Count",
    color="Accident_severity",
    color_discrete_sequence=COLOR_SEQUENCE,
    barmode="stack",
    title="Weather Conditions vs Accident Severity"
)
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig, width="stretch")

# Q7
st.header("7. Accident Severity Distribution")
severity_counts = df_filtered["Accident_severity"].value_counts()
severity_percent = (severity_counts / severity_counts.sum() * 100).round(2)

severity_table = pd.DataFrame({
    "Count": severity_counts,
    "Percentage": severity_percent
})
st.dataframe(severity_table)

fig = px.pie(
    values=severity_counts.values,
    names=severity_counts.index,
    color_discrete_sequence=COLOR_SEQUENCE,
    title="Distribution of Accident Severity",
    hole=0.35
)
st.plotly_chart(fig, width="stretch")

# Q8
st.header("8. Vehicle Types Most Involved")
vehicle_table = (df_filtered["Type_of_vehicle"]
                  .value_counts()
                  .head(10)
                  .reset_index())
vehicle_table.columns = ["Type_of_vehicle", "Accident_Count"]

fig = px.bar(
    vehicle_table,
    x="Accident_Count",
    y="Type_of_vehicle",
    orientation="h",
    color="Type_of_vehicle",
    color_discrete_sequence=COLOR_SEQUENCE,
    title="Top 10 Vehicle Types Involved in Accidents"
)
fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, width="stretch")

# Q9
st.header("9. Road Users Most Affected")
col1, col2 = st.columns(2)

with col1:
    st.subheader("By Sex")
    sex_counts = df_filtered["Sex_of_casualty"].value_counts().reset_index()
    sex_counts.columns = ["Sex_of_casualty", "Count"]
    fig = px.bar(
        sex_counts,
        x="Sex_of_casualty",
        y="Count",
        color="Sex_of_casualty",
        color_discrete_sequence=COLOR_SEQUENCE,
        title="Casualties by Sex"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("By Age Band")
    age_counts = df_filtered["Age_band_of_casualty"].value_counts().reset_index()
    age_counts.columns = ["Age_band_of_casualty", "Count"]
    fig = px.bar(
        age_counts,
        x="Age_band_of_casualty",
        y="Count",
        color="Age_band_of_casualty",
        color_discrete_sequence=COLOR_SEQUENCE,
        title="Casualties by Age Band"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

# Q10 - Association between key categorical variables (Cramér's V)
st.header("10. Association Between Key Categorical Variables")
st.markdown(
    "Since most variables in this dataset are categorical, **Cramér's V** is used "
    "instead of a standard correlation to measure the strength of association "
    "between each pair of variables. Values range from 0 (no association) to 1 "
    "(very strong association)."
)

def cramers_v(x, y):
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    if n == 0:
        return 0.0
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)
    
    denominator = min((kcorr - 1), (rcorr - 1))
    if denominator <= 0:
        return 0.0
        
    return np.sqrt(phi2corr / denominator)

association_cols = [
    "Age_band_of_driver",
    "Sex_of_driver",
    "Driving_experience",
    "Type_of_vehicle",
    "Area_accident_occured",
    "Road_surface_conditions",
    "Light_conditions",
    "Weather_conditions",
    "Cause_of_accident",
    "Accident_severity"
]

@st.cache_data
def compute_association_matrix(data, cols):
    matrix = pd.DataFrame(np.zeros((len(cols), len(cols))), index=cols, columns=cols)
    for col1 in cols:
        for col2 in cols:
            matrix.loc[col1, col2] = cramers_v(data[col1], data[col2])
    return matrix

association_matrix = compute_association_matrix(df_filtered, association_cols)

fig = px.imshow(
    association_matrix,
    text_auto=".2f",
    color_continuous_scale="Turbo",
    aspect="auto",
    title="Cramér's V — Association Between Key Categorical Variables"
)
fig.update_layout(height=700)
st.plotly_chart(fig, width="stretch")

st.markdown(
    "The strongest association observed is between **Road Surface Conditions** and "
    "**Weather Conditions**, which makes sense since weather directly affects whether "
    "roads are wet, icy, or dry. Most other variable pairs show weak associations, "
    "suggesting accident severity is driven by a combination of factors rather than "
    "any single variable."
)