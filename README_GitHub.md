# 📊 Engagement Survey Dashboard

Welcome to the **Engagement Survey Dashboard** repository! 

This project is a real-time, interactive data dashboard built to visualize the results of our Engagement Survey. It dynamically connects to a live Google Sheet to pull in new responses the moment they are submitted via our Google Form.

## 🚀 Features
- **Live Syncing**: Automatically updates as soon as new data comes into the Google Sheet.
- **Dynamic Questions**: Automatically detects new questions and answers added to the survey without requiring any code changes.
- **Interactive Visualizations**: View average scores and distribution of responses across a 5-point scale (Strongly Disagree ➡️ Strongly Agree) using beautiful Plotly charts.
- **Net Promoter Score (NPS) Calculation**: Automatically calculates the true NPS using the standard methodology:
  - **Promoters** (Score 9-10): Loyal enthusiasts.
  - **Passives** (Score 7-8): Satisfied but unenthusiastic.
  - **Detractors** (Score 0-6): Unhappy customers.
  - **Formula**: 
    - `% of Promoters = (No. of Promoters / No. of respondents) × 100%`
    - `% of Detractors = (No. of Detractors / No. of respondents) × 100%`
    - `NPS = % of Promoters - % of Detractors`

## 🛠️ Technology Stack
- **Python**: Core data processing.
- **Streamlit**: Web framework for the interactive dashboard.
- **Pandas**: Data manipulation and fetching from Google Sheets.
- **Plotly Express**: Interactive chart generation.

## 🌐 Live Deployment
This dashboard is deployed out-of-the-box using the **Streamlit Community Cloud**, allowing team members to securely access the latest survey analytics via a public web browser from anywhere without needing a Python environment.
