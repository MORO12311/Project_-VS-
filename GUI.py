import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from pymongo import MongoClient

# ============ [1] Data Loading =============
st.title("📊 Job Listings Interactive Analysis")

uploaded_file = st.file_uploader("D:/Downloads/tools/project/ll.csv", type="csv")
if not uploaded_file:
    st.warning("Please upload a CSV file")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# ============ [2] Data Cleaning =============
try:
    # Basic cleaning
    df = df.dropna(axis=1, how='all')
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates()
    
    # Initialize cleaned dataframe
    df_final = df.copy()
    
    # Check required columns
    required_columns = {'Salary (USD)', 'Location', 'Job Title', 'Company Name', 'Link'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        st.error(f"Missing required columns: {missing}")
        st.stop()
    
    # Salary cleaning
    df_final["Salary (USD)"] = df_final["Salary (USD)"].astype(str).str.replace("[$,]", "", regex=True)
    df_final["Salary (USD)"] = pd.to_numeric(df_final["Salary (USD)"], errors="coerce")
    
    # Skills processing (if column exists)
    if "Skills" in df.columns:
        df_final["Location"] = df_final["Location"].str.replace("-", "").str.strip()
        df_final["Skills List"] = df_final["Skills"].str.split("\u00b7")
        df_final = df_final.drop_duplicates(subset=["Link"])
        df_final["Company Name"] = df_final["Company Name"].str.replace(r"\s*-\s*$", "", regex=True).str.strip()
        df_final = df_final.drop(columns=["Skills"]).rename(columns={"Skills List": "Skills"})
    
    # Location processing
    df_final["Country"] = df_final["Location"].str.extract(r',\s*(\w+)$')
    df_final["Seniority"] = df_final["Job Title"].str.extract(r'\b(Senior|Junior|Intern|Lead|Manager)\b', flags=re.IGNORECASE)
    df_final["City"] = df_final["Location"].str.extract(r'^([^,]+)')

except Exception as e:
    st.error(f"Error during data cleaning: {e}")
    st.stop()

# ============ [3] Filter Interface =============
st.sidebar.header("🔍 Filter Jobs")

# Get available options
available_countries = df_final['Country'].dropna().unique()
available_cities = df_final['City'].dropna().unique()
available_seniority = df_final['Seniority'].dropna().unique()

# Create filters
selected_country = st.sidebar.multiselect("Country", available_countries)
selected_city = st.sidebar.multiselect("City", available_cities)
selected_seniority = st.sidebar.multiselect("Seniority", available_seniority)

# Salary range filter
salary_min, salary_max = int(df_final['Salary (USD)'].min()), int(df_final['Salary (USD)'].max())
salary_range = st.sidebar.slider("Salary Range (USD)", salary_min, salary_max, (salary_min, salary_max))

# Apply filters
filtered_df = df_final.copy()
if selected_country:
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_country)]
if selected_city:
    filtered_df = filtered_df[filtered_df['City'].isin(selected_city)]
if selected_seniority:
    filtered_df = filtered_df[filtered_df['Seniority'].isin(selected_seniority)]
filtered_df = filtered_df[(filtered_df['Salary (USD)'] >= salary_range[0]) & 
                         (filtered_df['Salary (USD)'] <= salary_range[1])]

# ============ [4] Dashboard Visualizations =============
st.write(f"📊 Showing {len(filtered_df)} jobs matching your filters")

# Salary Statistics
st.subheader("💰 Salary Statistics")
if not filtered_df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Salary", f"${filtered_df['Salary (USD)'].mean():,.2f}")
    with col2:
        st.metric("Minimum Salary", f"${filtered_df['Salary (USD)'].min():,.2f}")
    with col3:
        st.metric("Maximum Salary", f"${filtered_df['Salary (USD)'].max():,.2f}")
else:
    st.warning("No data matches your filters")

# Top Cities Chart
if not filtered_df.empty and 'City' in filtered_df.columns:
    st.subheader("🏙️ Top 10 Cities by Job Count")
    city_counts = filtered_df['City'].value_counts().head(10)
    st.bar_chart(city_counts)

# Salary by Seniority Analysis
if not filtered_df.empty and 'Seniority' in filtered_df.columns:
    df_with_seniority = filtered_df[filtered_df['Seniority'].notna()]
    if not df_with_seniority.empty:
        st.subheader("📈 Salary by Seniority Level")
        
        # Summary table
        salary_by_seniority = df_with_seniority.groupby('Seniority')['Salary (USD)'].agg(
            ['mean', 'min', 'max', 'count']).sort_values('mean', ascending=False)
        st.dataframe(salary_by_seniority.style.format({
            'mean': '${:,.2f}',
            'min': '${:,.2f}',
            'max': '${:,.2f}'
        }))
        
        # Visualizations
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Job Distribution")
            fig1, ax1 = plt.subplots()
            df_with_seniority['Seniority'].value_counts().plot(
                kind='pie', autopct='%1.1f%%', startangle=140, 
                colors=sns.color_palette('pastel'), ax=ax1)
            ax1.set_ylabel('')
            st.pyplot(fig1)
        
        with col2:
            st.subheader("📦 Salary Distribution")
            fig2, ax2 = plt.subplots()
            sns.boxplot(data=df_with_seniority, x='Seniority', y='Salary (USD)', 
                        palette='coolwarm', ax=ax2)
            plt.xticks(rotation=45)
            st.pyplot(fig2)

# Skills Word Cloud
if not filtered_df.empty and 'Skills' in filtered_df.columns:
    st.subheader("☁️ Most In-Demand Skills")
    skills_series = filtered_df['Skills'].dropna().explode().str.strip().str.lower()
    if not skills_series.empty:
        skills_text = ' '.join(skills_series.tolist())
        wordcloud = WordCloud(width=800, height=400, 
                            background_color='white', 
                            colormap='tab10').generate(skills_text)
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        ax3.imshow(wordcloud, interpolation='bilinear')
        ax3.axis('off')
        st.pyplot(fig3)

# Job Listings Table
st.subheader("🗂️ Job Listings")
if not filtered_df.empty:
    display_columns = ['Job Title', 'Company Name', 'City', 'Country', 'Salary (USD)']
    if 'Seniority' in filtered_df.columns:
        display_columns.append('Seniority')
    if 'Skills' in filtered_df.columns:
        display_columns.append('Skills')
    
    st.dataframe(
        filtered_df[display_columns].sort_values('Salary (USD)', ascending=False),
        height=400
    )
else:
    st.warning("No job listings to display")

# MongoDB Storage Option
st.sidebar.header("💾 Data Storage")
if st.sidebar.button("⬆️ Store Data to MongoDB"):
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client["jobs_database"]
        collection = db["jobs_cleaned_data"]
        
        # Clear existing data
        collection.delete_many({})
        
        # Insert new data
        data_to_insert = df_final.to_dict("records")
        collection.insert_many(data_to_insert)
        
        st.sidebar.success("✅ Data successfully stored in MongoDB!")
    except Exception as e:
        st.sidebar.error(f"Failed to connect to MongoDB: {e}")