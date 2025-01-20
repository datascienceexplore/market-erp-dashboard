import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# App Configuration
st.set_page_config(page_title="ERP Dashboard", page_icon="📊", layout="wide")

# Sidebar Navigation
st.sidebar.title("ERP Dashboard")
section = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard Overview",
        "Data Management",
        "Call Management",
        "Marketer Management",
        "Inquiry Tracking",
        "Reporting and Analytics",
    ]
)

# File Upload
st.sidebar.title("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.session_state["data"] = data
    st.sidebar.success("File uploaded successfully!")
else:
    st.sidebar.warning("Please upload a dataset to continue.")
    st.stop()

# Ensure required columns are present
required_columns = [
    "ID", "Date", "Name", "Age", "Father's Name", "Father's Occupation",
    "Address", "City", "State", "Pincode", "School Name", "Board", "Course",
    "Email ID", "Ph No", "Gender", "Specialization", "How did they know about the college",
    "Talk Start Duration", "Talk End Duration", "Marketer Assigned", "Call Outcome"
]
missing_columns = [col for col in required_columns if col not in data.columns]
for col in missing_columns:
    data[col] = None

# Dashboard Overview
if section == "Dashboard Overview":
    st.title("Dashboard Overview")

    # High-Level Metrics
    st.subheader("Key Metrics")
    total_inquiries = len(data)
    total_calls = len(data.dropna(subset=["Talk Start Duration", "Talk End Duration"]))
    interested_candidates = len(data[data["Call Outcome"] == "Interested"])
    brochures_sent = len(data[data["Call Outcome"] == "Brochure Sent"])
    completed_calls = len(data[data["Call Outcome"] == "Completed"])
    pending_calls = total_calls - completed_calls

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Inquiries", total_inquiries)
    col2.metric("Total Calls Made", total_calls)
    col3.metric("Interested Candidates", interested_candidates)
    col4.metric("Brochures Sent", brochures_sent)
    col5.metric("Calls Completed", completed_calls)

    # Charts
    st.subheader("Visual Analytics")
    col6, col7 = st.columns(2)
    with col6:
        call_success_chart = data["Call Outcome"].value_counts().reset_index()
        call_success_chart.columns = ["Outcome", "Count"]
        fig = px.bar(call_success_chart, x="Outcome", y="Count", title="Call Success Rates")
        st.plotly_chart(fig)
    with col7:
        age_distribution = px.histogram(data, x="Age", title="Candidate Age Distribution", nbins=10)
        st.plotly_chart(age_distribution)

# Data Management
elif section == "Data Management":
    st.title("Data Management")
    st.subheader("Candidate Information")
    st.dataframe(data)

    # Edit/Delete Functionality
    if st.button("Save Changes"):
        st.success("Changes saved!")

    # Export Data
    st.download_button(
        label="Download Updated Data as CSV",
        data=data.to_csv(index=False),
        file_name="updated_data.csv",
        mime="text/csv"
    )

# Call Management
elif section == "Call Management":
    st.title("Call Management")
    st.subheader("Leads per Marketer")

    marketers = data["Marketer Assigned"].dropna().unique()
    for marketer in marketers:
        st.subheader(f"Leads for {marketer}")
        leads = data[data["Marketer Assigned"] == marketer]
        edited_leads = st.experimental_data_editor(leads, num_rows="dynamic")
        if st.button(f"Save Changes for {marketer}"):
            data.update(edited_leads)
            st.success(f"Leads updated for {marketer}")

# Marketer Management
elif section == "Marketer Management":
    st.title("Marketer Management")
    st.subheader("Performance Metrics")

    performance = data.groupby("Marketer Assigned").size().reset_index(name="Calls Made")
    st.dataframe(performance)

    st.subheader("Assign Leads")
    new_marketer = st.text_input("Enter Marketer Name")
    if new_marketer and st.button("Assign Leads"):
        data.loc[data["Marketer Assigned"].isna(), "Marketer Assigned"] = new_marketer
        st.success(f"Leads assigned to {new_marketer}")

# Inquiry Tracking
elif section == "Inquiry Tracking":
    st.title("Inquiry Tracking")
    st.subheader("Follow-Ups")
    follow_up_candidates = data[data["Call Outcome"].isna()]
    st.table(follow_up_candidates)

# Reporting and Analytics
elif section == "Reporting and Analytics":
    st.title("Reporting and Analytics")

    st.subheader("Key Performance Indicators")
    call_success_rate = len(data[data["Call Outcome"] == "Success"]) / total_calls * 100 if total_calls else 0
    st.metric("Call Success Rate", f"{call_success_rate:.2f}%")

    st.subheader("Custom Reports")
    st.download_button(
        label="Download Report as CSV",
        data=data.to_csv(index=False),
        file_name="report.csv",
        mime="text/csv"
    )
