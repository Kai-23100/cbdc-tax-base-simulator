import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Title ---
st.set_page_config(page_title="CBDC Tax Base Impact Simulator", layout="wide")
st.title("📊 CBDC Impact on Tax Base Expansion in Uganda")
st.markdown("Compare two economic scenarios with different CBDC adoption strategies.")

# --- Layout ---
col1, col2 = st.columns(2)

# --- Scenario A Inputs ---
with col1:
    st.subheader("Scenario A")
    baseline_a = st.number_input("Baseline Tax Base A (UGX Bn)", 100.0, value=5000.0, step=100.0, key="baseline_a")
    adoption_a = st.slider("CBDC Adoption Rate A (%)", 0, 100, 40, key="adopt_a")
    compliance_a = st.slider("Compliance Improvement A (%)", 0, 100, 15, key="comp_a")
    rate_a = st.slider("Tax Rate A (%)", 0, 50, 15, key="rate_a")

# --- Scenario B Inputs ---
with col2:
    st.subheader("Scenario B")
    baseline_b = st.number_input("Baseline Tax Base B (UGX Bn)", 100.0, value=5000.0, step=100.0, key="baseline_b")
    adoption_b = st.slider("CBDC Adoption Rate B (%)", 0, 100, 70, key="adopt_b")
    compliance_b = st.slider("Compliance Improvement B (%)", 0, 100, 25, key="comp_b")
    rate_b = st.slider("Tax Rate B (%)", 0, 50, 20, key="rate_b")

# --- Common Inputs ---
time_horizon = st.slider("Time Horizon (Years)", 1, 10, 5)
alpha = 0.5

# --- Simulation Function ---
def simulate_tax(baseline, adoption, compliance, rate):
    years = np.arange(1, time_horizon + 1)
    multiplier = 1 + alpha * (adoption / 100) * (compliance / 100) * years
    tax_base = baseline * multiplier
    tax_revenue = tax_base * (rate / 100)
    return pd.DataFrame({
        "Year": years,
        "Tax Base (UGX Bn)": tax_base,
        "Tax Revenue (UGX Bn)": tax_revenue
    })

# --- Run Simulations ---
df_a = simulate_tax(baseline_a, adoption_a, compliance_a, rate_a)
df_b = simulate_tax(baseline_b, adoption_b, compliance_b, rate_b)

# --- Chart ---
st.subheader("📈 Tax Revenue Comparison")
chart_df = pd.DataFrame({
    "Year": df_a["Year"],
    "Scenario A": df_a["Tax Revenue (UGX Bn)"],
    "Scenario B": df_b["Tax Revenue (UGX Bn)"]
}).set_index("Year")

st.line_chart(chart_df)

# --- Comparison Table ---
st.subheader("📋 Final Year Comparison")
final_df = pd.DataFrame({
    "Scenario": ["A", "B"],
    "Final Tax Base (UGX Bn)": [df_a["Tax Base (UGX Bn)"].iloc[-1], df_b["Tax Base (UGX Bn)"].iloc[-1]],
    "Final Tax Revenue (UGX Bn)": [df_a["Tax Revenue (UGX Bn)"].iloc[-1], df_b["Tax Revenue (UGX Bn)"].iloc[-1]]
})
st.table(final_df.style.format("{:.2f}"))
