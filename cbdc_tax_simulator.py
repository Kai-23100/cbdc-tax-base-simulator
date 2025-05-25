import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile

# App Title and Description
st.set_page_config(page_title="CBDC Tax Base Impact Simulator - Uganda", layout="wide")
st.title("📊 CBDC Impact on Tax Base Expansion in Uganda")
st.markdown("""
This app simulates the potential increase in Uganda’s tax base due to the introduction of a Central Bank Digital Currency (CBDC).
Adjust the parameters below to explore different economic scenarios.
""")

# Sidebar Inputs
st.sidebar.header("Simulation Parameters")

baseline_tax_base = st.sidebar.number_input(
    "Baseline Annual Tax Base (UGX Billions)", min_value=100.0, value=5000.0, step=100.0
)

adoption_rate = st.sidebar.slider("CBDC Adoption Rate (%)", min_value=0, max_value=100, value=50)

compliance_increase = st.sidebar.slider(
    "Tax Compliance Improvement Due to CBDC (%)", min_value=0, max_value=100, value=20
)

tax_rate = st.sidebar.slider("Effective Tax Rate (%)", min_value=0, max_value=50, value=15)

time_horizon = st.sidebar.slider("Time Horizon (Years)", min_value=1, max_value=10, value=5)

alpha = 0.5  # Sensitivity coefficient

# Simulation Logic
years = np.arange(1, time_horizon + 1)
expansion_multiplier = 1 + alpha * (adoption_rate / 100) * (compliance_increase / 100) * years
tax_base_over_time = baseline_tax_base * expansion_multiplier
tax_revenue_over_time = tax_base_over_time * (tax_rate / 100)

df = pd.DataFrame({
    "Year": years,
    "Tax Base (UGX Bn)": tax_base_over_time,
    "Tax Revenue (UGX Bn)": tax_revenue_over_time
})

# Output Section
st.subheader("📈 Simulation Results Over Time")
st.line_chart(df.set_index("Year"))

st.dataframe(df.style.format({"Tax Base (UGX Bn)": "{:.2f}", "Tax Revenue (UGX Bn)": "{:.2f}"}))

# PDF Export
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CBDC Tax Base Simulation Report - Uganda", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Baseline Tax Base: {baseline_tax_base:.2f} UGX Bn", 0, 1)
    pdf.cell(0, 10, f"CBDC Adoption Rate: {adoption_rate}%", 0, 1)
    pdf.cell(0, 10, f"Compliance Increase: {compliance_increase}%", 0, 1)
    pdf.cell(0, 10, f"Tax Rate: {tax_rate}%", 0, 1)
    pdf.cell(0, 10, f"Time Horizon: {time_horizon} years", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(30, 10, "Year", 1)
    pdf.cell(70, 10, "Tax Base (UGX Bn)", 1)
    pdf.cell(70, 10, "Tax Revenue (UGX Bn)", 1)
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(30, 10, str(int(row["Year"])), 1)
        pdf.cell(70, 10, f"{row['Tax Base (UGX Bn)']:.2f}", 1)
        pdf.cell(70, 10, f"{row['Tax Revenue (UGX Bn)']:.2f}", 1)
        pdf.ln()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

if st.button("📄 Download Simulation Report as PDF"):
    pdf_file = generate_pdf(df)
    with open(pdf_file, "rb") as f:
        st.download_button("Download PDF", data=f, file_name="CBDC_Uganda_Tax_Report.pdf", mime="application/pdf")
