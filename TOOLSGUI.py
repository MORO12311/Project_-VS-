import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the cleaned data (make sure this path is accessible or change to your saved path)
data_path = r"D:\\Downloads\\cleaned_jobs_data.csv"
df = pd.read_csv(data_path)
df.columns = df.columns.str.strip()


# === 7. تحديد مستوى الوظيفة ===
def determine_job_level(experience):
    if experience is None:
        return None
    if experience < 2:
        return "Junior"
    elif 2 <= experience < 5:
        return "Mid-Level"
    elif experience >= 5:
        return "Senior"
    return None

df["Job Level"] = df["Experience (Yrs)"].apply(lambda x: determine_job_level(x))
# Title
st.title("Job Data Analysis from Wuzzuf")
st.markdown("Interactively explore cleaned job data scraped from Wuzzuf.")

# Sidebar filters
st.sidebar.header("Filters")

# Job Level Filter
levels = df["Job Level"].unique().tolist()
selected_levels = st.sidebar.multiselect("Select Job Levels:", levels, default=levels)

# Work Type Filter
work_types = df["Work Type"].dropna().unique().tolist()
selected_work_types = st.sidebar.multiselect("Select Work Types:", work_types, default=work_types)

# City Filter
cities = df["City"].dropna().unique().tolist()
selected_cities = st.sidebar.multiselect("Select Cities:", cities, default=cities[:10])

# Filter data
filtered_df = df[
    (df["Job Level"].isin(selected_levels)) &
    (df["Work Type"].isin(selected_work_types)) &
    (df["City"].isin(selected_cities))
]

# Display basic stats
st.subheader("Basic Statistics")
st.metric("Total Jobs", len(filtered_df))
st.metric("Average Experience (Years)", round(filtered_df["Experience (Yrs)"].mean(), 2))

# Charts Section
st.subheader("Visualizations")

# Job Level Distribution
st.markdown("### Job Level Distribution")
fig1, ax1 = plt.subplots()
sns.countplot(data=filtered_df, x="Job Level", order=filtered_df["Job Level"].value_counts().index, ax=ax1)
ax1.set_title("Job Level Distribution")
st.pyplot(fig1)

# Work Type Distribution
st.markdown("### Work Type Frequency")
fig2, ax2 = plt.subplots()
filtered_df["Work Type"].value_counts().plot(kind="barh", ax=ax2, color=sns.color_palette("Set2"))
ax2.set_title("Work Type Frequency")
st.pyplot(fig2)

# Boxplot: Experience vs. Job Level
st.markdown("### Experience by Job Level")
fig3, ax3 = plt.subplots()
sns.boxplot(data=filtered_df, x="Job Level", y="Experience (Yrs)", ax=ax3)
ax3.set_title("Experience Distribution by Job Level")
st.pyplot(fig3)

# Top Cities with Jobs
st.markdown("### Top Cities with Jobs")
top_cities = filtered_df["City"].value_counts().head(10)
fig4, ax4 = plt.subplots()
top_cities.plot(kind="bar", ax=ax4, color=sns.color_palette("coolwarm", 10))
ax4.set_title("Top 10 Cities with Jobs")
ax4.set_ylabel("Count")
st.pyplot(fig4)

# Experience Histogram
st.markdown("### Distribution of Experience (Years)")
fig5, ax5 = plt.subplots()
sns.histplot(filtered_df["Experience (Yrs)"], bins=10, kde=True, color="#2a9d8f", ax=ax5)
ax5.set_title("Experience Distribution")
st.pyplot(fig5)

# Show raw data
with st.expander("🔍 Show Raw Data"):
    st.dataframe(filtered_df.reset_index(drop=True))
