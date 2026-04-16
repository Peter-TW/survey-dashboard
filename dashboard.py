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
    data["How long have you been with Group?"] = np.random.choice(["< 6 months", "6 months - 1 year", "1 - 3 years", "3 -5 years", "> 5 years"], size=100)
    return pd.DataFrame(data)

st.title("📊 Engagement Survey")
st.markdown("Monitor and analyze employee engagement metrics derived directly from the Google Form.")

df, is_live = load_data(GOOGLE_SHEET_CSV_URL)

if not is_live:
    st.warning("⚠️ **Note:** Currently showing **Mock Data**. Please update `GOOGLE_SHEET_CSV_URL` in `dashboard.py` to see live results.")

st.sidebar.header("Filters")

dept_col = "Which team do you sit in?"
tenure_col = "How long have you been with Group?"

if dept_col in df.columns:
    all_depts = sorted(df[dept_col].dropna().unique().tolist())
    
    # Implementing "Select All" behavior for Departments
    select_all_dept = st.sidebar.checkbox("Select all departments", value=True)
    if select_all_dept:
        selected_depts = st.sidebar.multiselect("Select Department(s)", options=all_depts, default=all_depts)
    else:
        selected_depts = st.sidebar.multiselect("Select Department(s)", options=all_depts)
        
    # Apply filter
    df = df[df[dept_col].isin(selected_depts)]

if tenure_col in df.columns:
    base_tenure_order = ["< 6 months", "6 months - 1 year", "1 - 3 years", "3 -5 years", "> 5 years"]
    unique_tenures = df[tenure_col].dropna().unique().tolist()
    all_tenures = [t for t in base_tenure_order if t in unique_tenures] + sorted([t for t in unique_tenures if t not in base_tenure_order])
    
    # Implementing "Select All" behavior for Tenure
    select_all_tenure = st.sidebar.checkbox("Select all tenures", value=True)
    if select_all_tenure:
        selected_tenures = st.sidebar.multiselect("Select Tenure(s)", options=all_tenures, default=all_tenures)
    else:
        selected_tenures = st.sidebar.multiselect("Select Tenure(s)", options=all_tenures)
        
    # Apply filter
    df = df[df[tenure_col].isin(selected_tenures)]

if dept_col not in df.columns and tenure_col not in df.columns:
    st.sidebar.markdown("Use this to filter by date or department or tenure (if added to the form later).")

st.divider()

# --- OVERALL METRICS ---
col1, col2, col3 = st.columns(3)
nps_col = "How likely is it that you would recommend Hanson Wade to a friend or colleague? (10 being strongly recommend)"

nps_score = 0
if nps_col in df.columns and not df.empty:
    total_valid = len(df[nps_col].dropna())
    if total_valid > 0:
        promoters = len(df[df[nps_col] >= 9])
        detractors = len(df[df[nps_col] <= 6])
        nps_score = ((promoters / total_valid) - (detractors / total_valid)) * 100

col1.metric("Total Responses", len(df))
col2.metric("Net Promoter Score (NPS)", f"{nps_score:.0f}")

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
    dept_counts = dept_counts.sort_values(by='Department')
    
    fig_dept = px.bar(
        dept_counts, 
        x='Department', 
        y='Number of Responses',
        text='Number of Responses',
        color_discrete_sequence=['#4B0082']
    )
    fig_dept.update_traces(textposition='outside')
    st.plotly_chart(fig_dept, use_container_width=True)
    st.divider()

# --- DISTRIBUTION CHARTS ---
st.subheader("Statement Analysis")
selected_q = st.selectbox("Select a statement to analyze:", likert_cols)

if selected_q and dept_col in df.columns:
    dept_avg = df.groupby(dept_col)[selected_q].mean().reset_index()
    dept_avg.columns = ['Department', 'Average Score']
    dept_avg['Average Score Formatted'] = dept_avg['Average Score'].round(2)
    dept_avg = dept_avg.sort_values(by='Department')
    
    fig = px.bar(
        dept_avg, 
        x='Department', 
        y='Average Score',
        text='Average Score Formatted',
        range_y=[0, 5.5],
        color_discrete_sequence=['#4B0082']
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_title="Department", yaxis_title="Average Rating")
    st.plotly_chart(fig, use_container_width=True)

if selected_q and tenure_col in df.columns:
    tenure_avg = df.groupby(tenure_col)[selected_q].mean().reset_index()
    tenure_avg.columns = ['Tenure', 'Average Score']
    tenure_avg['Average Score Formatted'] = tenure_avg['Average Score'].round(2)
    
    tenure_order = ["< 6 months", "6 months - 1 year", "1 - 3 years", "3 -5 years", "> 5 years"]
    active_tenures = [t for t in tenure_order if t in tenure_avg['Tenure'].values]
    
    tenure_avg['Tenure'] = pd.Categorical(tenure_avg['Tenure'], categories=active_tenures, ordered=True)
    tenure_avg = tenure_avg.sort_values(by='Tenure')
    
    fig_tenure = px.bar(
        tenure_avg, 
        x='Tenure', 
        y='Average Score',
        text='Average Score Formatted',
        range_y=[0, 5.5],
        category_orders={"Tenure": active_tenures},
        color_discrete_sequence=['#1f77b4']
    )
    fig_tenure.update_traces(textposition='outside')
    fig_tenure.update_layout(xaxis_title="How long have you been with Group?", yaxis_title="Average Rating")
    st.plotly_chart(fig_tenure, use_container_width=True)

if selected_q and dept_col not in df.columns and tenure_col not in df.columns:
    st.info("Department and Tenure data are required to view breakdown analysis.")

# Heatmap or averages table
st.subheader("All Ratings Overview")
averages = df[likert_cols].mean().reset_index()
averages.columns = ['Statement', 'Average Score']
averages = averages.sort_values(by='Average Score', ascending=False)
st.dataframe(
    averages,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Statement": st.column_config.TextColumn("Statement"),
        "Average Score": st.column_config.NumberColumn(
            "Average Score",
            format="%.2f",
            alignment="center"
        )
    }
)
