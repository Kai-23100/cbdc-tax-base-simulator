import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="CBDC Tax Base Simulator with Economic Factors - Uganda", layout="wide")

st.title("🇺🇬 CBDC Impact Simulator on Uganda's Tax Base with Economic Factors")

st.markdown("""
This simulator models the potential impact of CBDC adoption on Uganda's tax base expansion,
incorporating inflation, population growth, and GDP impact with **real-time economic data** from World Bank.
""")

# --- Fetch real-time Uganda GDP and Population from World Bank API ---
@st.cache_data(ttl=3600)
def fetch_world_bank_data(indicator_code):
    url = f"http://api.worldbank.org/v2/country/UGA/indicator/{indicator_code}?format=json&per_page=1&date=2023"
    try:
        res = requests.get(url)
        data = res.json()
        value = data[1][0]['value']
        return value
    except Exception:
        return None

latest_gdp = fetch_world_bank_data("NY.GDP.MKTP.CD")  # GDP current US$
latest_population = fetch_world_bank_data("SP.POP.TOTL")  # Total population

# Display real-time data in sidebar
with st.sidebar.expander("Real-time Economic Data (2023):", expanded=True):
    st.write(f"🇺🇬 Uganda GDP (current US$): **{latest_gdp:,.0f}**" if latest_gdp else "GDP data unavailable")
    st.write(f"🇺🇬 Uganda Population: **{latest_population:,.0f}**" if latest_population else "Population data unavailable")

# --- User Inputs ---
st.sidebar.header("Simulation Parameters")

baseline_tax_base = st.sidebar.number_input(
    "Baseline Annual Tax Base (UGX Billions)", min_value=100.0, value=5000.0, step=100.0,
    help="Current estimated tax base in Uganda"
)

cbdc_adoption_rate = st.sidebar.slider("CBDC Adoption Rate (%)", min_value=0, max_value=100, value=50)
compliance_improvement = st.sidebar.slider("Tax Compliance Improvement Due to CBDC (%)", min_value=0, max_value=100, value=20)
effective_tax_rate = st.sidebar.slider("Effective Tax Rate (%)", min_value=0, max_value=50, value=15)
time_horizon = st.sidebar.slider("Time Horizon (Years)", min_value=1, max_value=10, value=5)

# Additional economic factors inputs
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
population_growth_rate = st.sidebar.slider("Annual Population Growth Rate (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.1)

# GDP impact factor (0-1) representing how much GDP growth affects tax base growth
gdp_impact_factor = st.sidebar.slider("GDP Impact Factor on Tax Base (0-1)", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

# Constants
alpha = 0.5  # CBDC sensitivity coefficient

# --- Calculate baseline annual GDP growth rate from World Bank if data is available ---
def estimate_gdp_growth_rate():
    # For demo, assume 5% if no data
    # In practice, fetch historical data for growth calculation
    return 0.05

gdp_growth_rate = estimate_gdp_growth_rate()

# --- Simulation logic ---
years = np.arange(1, time_horizon + 1)

# Calculate yearly factors
inflation_factor = (1 + inflation_rate / 100) ** years
population_factor = (1 + population_growth_rate / 100) ** years
gdp_factor = (1 + gdp_growth_rate) ** years * gdp_impact_factor + (1 - gdp_impact_factor)

# CBDC related expansion multiplier
cbdc_multiplier = 1 + alpha * (cbdc_adoption_rate / 100) * (compliance_improvement / 100) * years

# Combine all multipliers for tax base growth
total_growth_multiplier = cbdc_multiplier * inflation_factor * population_factor * gdp_factor

# Project tax base and revenue over time
tax_base_over_time = baseline_tax_base * total_growth_multiplier
tax_revenue_over_time = tax_base_over_time * (effective_tax_rate / 100)

# Results DataFrame
df_results = pd.DataFrame({
    "Year": years,
    "Tax Base (UGX Billions)": tax_base_over_time,
    "Tax Revenue (UGX Billions)": tax_revenue_over_time,
    "Inflation Factor": inflation_factor,
    "Population Factor": population_factor,
    "GDP Factor": gdp_factor,
    "CBDC Impact Multiplier": cbdc_multiplier
})

# --- Outputs ---
st.subheader("📈 Tax Base & Revenue Projection")

st.line_chart(df_results.set_index("Year")[["Tax Base (UGX Billions)", "Tax Revenue (UGX Billions)"]])

st.dataframe(df_results.style.format({
    "Tax Base (UGX Billions)": "{:,.2f}",
    "Tax Revenue (UGX Billions)": "{:,.2f}",
    "Inflation Factor": "{:.3f}",
    "Population Factor": "{:.3f}",
    "GDP Factor": "{:.3f}",
    "CBDC Impact Multiplier": "{:.3f}"
}))

# --- PDF Report Generation ---
def generate_pdf_report(df, params):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CBDC Tax Base Impact Simulation Report - Uganda", 0, 1, "C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 10, "Simulation Parameters:", 0, 1)
    for k, v in params.items():
        pdf.cell(0, 8, f"{k}: {v}", 0, 1)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(20, 10, "Year", 1)
    pdf.cell(50, 10, "Tax Base (UGX Bn)", 1)
    pdf.cell(50, 10, "Tax Revenue (UGX Bn)", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for _, row in df.iterrows():
        pdf.cell(20, 10, str(int(row["Year"])), 1)
        pdf.cell(50, 10, f"{row['Tax Base (UGX Billions)']:.2f}", 1)
        pdf.cell(50, 10, f"{row['Tax Revenue (UGX Billions)']:.2f}", 1)
        pdf.ln()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

# Prepare parameters for PDF
params = {
    "Baseline Tax Base (UGX Billions)": f"{baseline_tax_base:,.2f}",
    "CBDC Adoption Rate (%)": f"{cbdc_adoption_rate}%",
    "Compliance Improvement (%)": f"{compliance_improvement}%",
    "Effective Tax Rate (%)": f"{effective_tax_rate}%",
    "Time Horizon (Years)": f"{time_horizon}",
    "Inflation Rate (%)": f"{inflation_rate}%",
    "Population Growth Rate (%)": f"{population_growth_rate}%",
    "GDP Impact Factor": f"{gdp_impact_factor}",
}

if st.button("📄 Download PDF Report"):
    pdf_path = generate_pdf_report(df_results, params)
    with open(pdf_path, "rb") as f:
        st.download_button("Download Report", f, file_name="CBDC_Uganda_Tax_Simulation_Report.pdf", mime="application/pdf")
