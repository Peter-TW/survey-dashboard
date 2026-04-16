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

You can access your live dashboard here:
**[https://survey-dashboard-dcsflr69neosjrzu67ej5z.streamlit.app/](https://survey-dashboard-dcsflr69neosjrzu67ej5z.streamlit.app/)**

---

## 🏗️ Project Setup & Creation Guide

This section contains the automated tools and instructions to create and visualize your Engagement Survey from scratch.

### 1. Create the Google Form

Because the script is generated locally on your computer, you need to run the code in your Google account to get the official form URL.

**Instructions:**
1. Navigate to your Google Apps Script dashboard: [https://script.google.com/](https://script.google.com/)
2. Click **New Project** and name it something like *Survey Generator*.
3. Open `CreateForm.gs` from this folder and copy all the code inside it.
4. Delete the default code in your Apps Script project and paste the copied code.
5. Click **Save** 💾 and then **Run** ▶️.
6. **Where is my Form URL?** Check the **Execution Log** at the bottom of the screen. Look for `Form edit URL:` and `Form published URL:`. It will also print out the `Linked Spreadsheet URL:` which you will need for the dashboard!
   *(Note: You will be asked to grant permission the first time you run it. Click "Review Permissions" > "Advanced" > "Go to script")*

### 2. Where is the Data Stored?

When anyone fills out and submits your Google Form, their responses are instantly and securely saved into the **Google Sheet** that was generated automatically with the form.
- The link to this Google Sheet is printed in the Execution Log (`Linked Spreadsheet URL:`) from Step 1.
- You can also find it in your Google Drive, named `Hanson Wade Engagement Survey Responses`.
- This Google Sheet acts as your live, continuously updating database. No manual CSV exporting is required!

### 3. Connect the Dashboard

Once the form is created and you have the Google Sheet URL from the step above, you must link it to the Streamlit Dashboard.

1. Open your newly generated **Google Sheet**.
2. Click the **Share** button in the top right and set the access to **"Anyone with the link"** as a Viewer.
3. Copy the Sheet ID from the URL (The long string of random characters between `/d/` and `/edit`).
4. Open `dashboard.py` in your text editor.
5. Around **Line 12**, replace `YOUR_SHEET_ID_HERE` with your actual Sheet ID.
6. Save the file.

### 4. How to Add or Update Questions

If you want to update existing questions or add new ones in the future, you have two options:

#### Option A: The Easy Way (Edit the Google Form directly)
The Streamlit Python Dashboard is designed to be **dynamic**. It will automatically adapt to your form!
1. Open your **Google Form Edit URL**.
2. **To Update:** Modify the text of an existing question directly in the form builder.
3. **To Add New:** Click the **"+"** button on the right side of the Google Form to add a new question (make sure it's a 1-5 Scale Question).
4. The Google Form syncs seamlessly to the Google Sheet. New responses will populate there, and your Streamlit Dashboard will automatically scan for new questions and add them to your charts!

#### Option B: The Automated Way (Re-run the scripts from your Excel File)
If you made massive changes to your original `Survey Statements.xlsx` Excel document and want to build a brand new Form from scratch:
1. Update your statements in `Survey Statements.xlsx`.
2. Open your terminal in your Survey folder and rebuild the scripts by running:
   ```bash
   powershell -ExecutionPolicy Bypass -File .\extract.ps1
   py generate_gs.py
   ```
3. This creates a newly updated `CreateForm.gs` file.
4. Repeat **Step 1** at the top of this document to publish a brand new Google Form and Sheet!
