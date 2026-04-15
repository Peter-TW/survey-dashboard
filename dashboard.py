import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page aesthetic
st.set_page_config(page_title="Hanson Wade Survey Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- DATA LOADING ---
# To use your live Google Sheet, change this URL. 
# 1. Share your Google Sheet as "Anyone with the link can view".
# 2. Get the Sheet ID from the URL and use the format below:
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1zxVOFaptCR50SZ4tCS0lkiV7zkbyGeigHrEd8QWdfSs/export?format=csv"

@st.cache_data(ttl=60)  # cache data for 1 minute
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df, True
    except Exception as e:
        # Fallback to generated dummy data to showcase the dashboard
        return generate_dummy_data(), False

def generate_dummy_data():
    questions = [
        "Hanson Wade Group cares about my wellbeing",
        "The pressure in my job feels manageable",
        "I am able to provide my customers with great service",
        "I believe Hanson Wade Group is a meritocracy",
        "I am happy in my job"
    ]
    np.random.seed(42)
    data = {"Timestamp": pd.date_range("2024-01-01", periods=100, freq='D')}
    for q in questions:
        # scale 1-5
        data[q] = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.2, 0.45, 0.2], size=100)
    data["How likely is it that you would recommend Hanson Wade to a friend or colleague? (10 being strongly recommend)"] = np.random.choice(range(1, 11), size=100)
    data["Which team do you sit in?"] = np.random.choice(["IT", "HR", "Sales", "Marketing", "Production"], size=100)
    return pd.DataFrame(data)

st.title("📊 Hanson Wade Engagement Survey")
st.markdown("Monitor and analyze employee engagement metrics derived directly from the Google Form.")

df, is_live = load_data(GOOGLE_SHEET_CSV_URL)

if not is_live:
    st.warning("⚠️ **Note:** Currently showing **Mock Data**. Please update `GOOGLE_SHEET_CSV_URL` in `dashboard.py` to see live results.")

st.sidebar.header("Filters")

dept_col = "Which team do you sit in?"
if dept_col in df.columns:
    all_depts = sorted(df[dept_col].dropna().unique().tolist())
    
    # Implementing "Select All" behavior
    select_all = st.sidebar.checkbox("Select all departments", value=True)
    if select_all:
        selected_depts = st.sidebar.multiselect("Select Department(s)", options=all_depts, default=all_depts)
    else:
        selected_depts = st.sidebar.multiselect("Select Department(s)", options=all_depts)
        
    # Apply filter
    df = df[df[dept_col].isin(selected_depts)]
else:
    st.sidebar.markdown("Use this to filter by date or department (if added to the form later).")

st.divider()

# --- OVERALL METRICS ---
col1, col2, col3 = st.columns(3)
nps_col = "How likely is it that you would recommend Hanson Wade to a friend or colleague? (10 being strongly recommend)"
nps_avg = df[nps_col].mean() if nps_col in df.columns and not df.empty else 0

col1.metric("Total Responses", len(df))
col2.metric("Average Recommendation (NPS Proxy)", f"{nps_avg:.1f} / 10")

# Calculate average across 1-5 scale questions
numeric_cols = df.select_dtypes(include='number').columns
likert_cols = [c for c in numeric_cols if c != nps_col]
if likert_cols:
    overall_avg = df[likert_cols].mean().mean() if not df.empty else 0
    col3.metric("Overall Engagement Score", f"{overall_avg:.1f} / 5")

st.divider()

if dept_col in df.columns:
    st.subheader("Responses by Department")
    dept_counts = df[dept_col].value_counts().reset_index()
    dept_counts.columns = ['Department', 'Number of Responses']
    
    fig_dept = px.bar(
        dept_counts, 
        x='Department', 
        y='Number of Responses',
        title="Total Responses per Department",
        color_discrete_sequence=['#4B0082']
    )
    st.plotly_chart(fig_dept, use_container_width=True)
    st.divider()

# --- DISTRIBUTION CHARTS ---
st.subheader("Statement Analysis")
selected_q = st.selectbox("Select a statement to analyze:", likert_cols)

if selected_q:
    fig = px.histogram(
        df, 
        x=selected_q, 
        nbins=5, 
        range_x=[0.5, 5.5],
        color_discrete_sequence=['#4B0082'],
        title=f"Response Distribution for: {selected_q}"
    )
    fig.update_layout(xaxis_title="Rating (1 = Strongly Disagree, 5 = Strongly Agree)", yaxis_title="Number of Responses")
    st.plotly_chart(fig, use_container_width=True)

# Heatmap or averages table
st.subheader("All Ratings Overview")
averages = df[likert_cols].mean().reset_index()
averages.columns = ['Statement', 'Average Score']
averages = averages.sort_values(by='Average Score', ascending=False)
st.dataframe(averages, use_container_width=True)
