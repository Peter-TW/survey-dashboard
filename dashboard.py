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
col1, col2 = st.columns(2)
nps_col = "How likely is it that you would recommend Hanson Wade to a friend or colleague? (10 being strongly recommend)"

nps_score = 0
if nps_col in df.columns and not df.empty:
    nps_series = pd.to_numeric(df[nps_col], errors='coerce')
    total_valid = len(nps_series.dropna())
    if total_valid > 0:
        promoters = (nps_series >= 9).sum()
        detractors = (nps_series <= 6).sum()
        nps_score = ((promoters / total_valid) - (detractors / total_valid)) * 100

col1.metric("Total Responses", len(df))
col2.metric("Net Promoter Score (NPS)", f"{nps_score:.0f}")

# Extract 1-5 scale questions for later analysis charts
numeric_cols = df.select_dtypes(include='number').columns
likert_cols = [c for c in numeric_cols if c != nps_col]

QUESTION_CATEGORIES = {
    "The pressure in my job feels manageable": "Role and Career Progression",
    "I am able to provide my customers with great service": "Role and Career Progression",
    "I believe Hanson Wade Group is a meritocracy": "Role and Career Progression",
    "I am happy in my job": "Role and Career Progression",
    "I am fairly rewarded for my role": "Role and Career Progression",
    "I receive sufficient training to help me achieve and advance in my role": "Role and Career Progression",
    "I am happy with my professional development so far": "Role and Career Progression",
    "I am happy with what my development looks like in the future": "Role and Career Progression",
    "My manager is invested in my development": "Manager",
    "My manager and I have a great working relationship": "Manager",
    "I feel comfortable questioning and challenging my manager": "Manager",
    "My team works well together": "Manager",
    "I have the time to do my job well": "Manager",
    "I have the resources to do my job well": "Manager",
    "I have the time and resources to do my job well": "Manager",
    "I understand the company strategy and direction": "Senior Management",
    "Senior Management and employees trust each other": "Senior Management",
    "There is transparent communication from Senior Management": "Senior Management",
    "How likely is it that you would recommend Hanson Wade to a friend or colleague? (10 being strongly recommend)": "Recommendation"
}

def get_category(q):
    return QUESTION_CATEGORIES.get(q, "Culture, Wellbeing and Inclusion")

if likert_cols:
    st.sidebar.divider()
    st.sidebar.subheader("Question Filters")
    all_categories = sorted(list(set([get_category(q) for q in likert_cols])))
    select_all_cat = st.sidebar.checkbox("Select all categories", value=True)

    if select_all_cat:
        selected_categories = st.sidebar.multiselect("Questions Category", options=all_categories, default=all_categories)
    else:
        selected_categories = st.sidebar.multiselect("Questions Category", options=all_categories)

    likert_cols = [q for q in likert_cols if get_category(q) in selected_categories]

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
    active_tenures = [t for t in tenure_order if t in tenure_avg['Tenure'].values] + sorted([t for t in tenure_avg['Tenure'].values if t not in tenure_order])
    
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
if likert_cols:
    counts = df[likert_cols].count().reset_index()
    counts.columns = ['Statement', 'Number of Responses']
    averages = df[likert_cols].mean().reset_index()
    averages.columns = ['Statement', 'Average Score']
    
    overview = pd.merge(averages, counts, on='Statement')
    overview['Category'] = overview['Statement'].apply(get_category)
    overview = overview[['Category', 'Statement', 'Number of Responses', 'Average Score']]
    overview = overview.sort_values(by=['Category', 'Average Score'], ascending=[True, False])
    
    st.dataframe(
        overview,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Category": st.column_config.TextColumn("Category"),
            "Statement": st.column_config.TextColumn("Statement"),
            "Number of Responses": st.column_config.NumberColumn(
                "Number of Responses",
                alignment="center"
            ),
            "Average Score": st.column_config.NumberColumn(
                "Average Score",
                format="%.2f",
                alignment="center"
            )
        }
    )
else:
    st.info("No categories selected.")

# --- NPS ANALYSIS ---
st.divider()
st.subheader("NPS Analysis")

def calc_nps(series):
    num_series = pd.to_numeric(series, errors='coerce')
    total = len(num_series.dropna())
    if total == 0: return 0
    promoters = (num_series >= 9).sum()
    detractors = (num_series <= 6).sum()
    return ((promoters / total) - (detractors / total)) * 100

if nps_col in df.columns:
    nps_col1, nps_col2 = st.columns(2)
    
    # Department NPS
    if dept_col in df.columns:
        dept_nps = df.groupby(dept_col)[nps_col].apply(calc_nps).reset_index()
        dept_nps.columns = ['Department', 'NPS Score']
        dept_nps['NPS Score Formatted'] = dept_nps['NPS Score'].round(0)
        dept_nps = dept_nps.sort_values(by='Department')
        
        fig_nps_dept = px.bar(
            dept_nps, 
            x='Department', 
            y='NPS Score',
            text='NPS Score Formatted',
            color_discrete_sequence=['#4B0082']
        )
        fig_nps_dept.update_traces(textposition='outside')
        fig_nps_dept.update_layout(xaxis_title="Department", yaxis_title="NPS Score", title="NPS by Department")
        nps_col1.plotly_chart(fig_nps_dept, use_container_width=True)
        
    # Tenure NPS
    if tenure_col in df.columns:
        tenure_nps = df.groupby(tenure_col)[nps_col].apply(calc_nps).reset_index()
        tenure_nps.columns = ['Tenure', 'NPS Score']
        tenure_nps['NPS Score Formatted'] = tenure_nps['NPS Score'].round(0)
        
        tenure_order = ["< 6 months", "6 months - 1 year", "1 - 3 years", "3 -5 years", "> 5 years"]
        active_nps_tenures = [t for t in tenure_order if t in tenure_nps['Tenure'].values] + sorted([t for t in tenure_nps['Tenure'].values if t not in tenure_order])
        
        tenure_nps['Tenure'] = pd.Categorical(tenure_nps['Tenure'], categories=active_nps_tenures, ordered=True)
        tenure_nps = tenure_nps.sort_values(by='Tenure')
        
        fig_nps_tenure = px.bar(
            tenure_nps, 
            x='Tenure', 
            y='NPS Score',
            text='NPS Score Formatted',
            category_orders={"Tenure": active_nps_tenures},
            color_discrete_sequence=['#1f77b4']
        )
        fig_nps_tenure.update_traces(textposition='outside')
        fig_nps_tenure.update_layout(xaxis_title="How long have you been with Group?", yaxis_title="NPS Score", title="NPS by Tenure")
        nps_col2.plotly_chart(fig_nps_tenure, use_container_width=True)
