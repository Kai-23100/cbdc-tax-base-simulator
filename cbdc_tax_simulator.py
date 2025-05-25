import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CBDC Tax Base Impact Simulator - Uganda", layout="wide")
st.title("📊 CBDC Impact on Tax Base Expansion in Uganda")
st.markdown("Compare two economic scenarios with different CBDC adoption strategies.")

# Sidebar inputs for Scenario A
st.sidebar.header("Scenario A Parameters")
baseline_a = st.sidebar.number_input("Baseline Tax Base A (UGX Billions)", min_value=100.0, value=5000.0, step=100.0)
adoption_a = st.sidebar.slider("CBDC Adoption Rate A (%)", 0, 100, 50)
compliance_a = st.sidebar.slider("Compliance Improvement A (%)", 0, 100, 20)
tax_rate_a = st.sidebar.slider("Tax Rate A (%)", 0, 50, 15)

# Sidebar inputs for Scenario B
st.sidebar.header("Scenario B Parameters")
baseline_b = st.sidebar.number_input("Baseline Tax Base B (UGX Billions)", min_value=100.0, value=5000.0, step=100.0)
adoption_b = st.sidebar.slider("CBDC Adoption Rate B (%)", 0, 100, 70)
compliance_b = st.sidebar.slider("Compliance Improvement B (%)", 0, 100, 30)
tax_rate_b = st.sidebar.slider("Tax Rate B (%)", 0, 50, 20)

# Time horizon input
time_horizon = st.sidebar.slider("Time Horizon (Years)", 1, 10, 5)

# Sensitivity coefficient
alpha = 0.5

years = np.arange(1, time_horizon + 1)

def simulate_tax(base, adoption, compliance, tax_rate):
    expansion = 1 + alpha * (adoption / 100) * (compliance / 100) * years
    tax_base = base * expansion
    tax_revenue = tax_base * (tax_rate / 100)
    df = pd.DataFrame({
        "Year": years,
        "Tax Base (UGX Bn)": tax_base,
        "Tax Revenue (UGX Bn)": tax_revenue
    })
    return df

df_a = simulate_tax(baseline_a, adoption_a, compliance_a, tax_rate_a)
df_b = simulate_tax(baseline_b, adoption_b, compliance_b, tax_rate_b)

# Plot comparison
st.subheader("📈 Tax Revenue Over Time: Scenario A vs Scenario B")
plt.figure(figsize=(10, 5))
plt.plot(df_a["Year"], df_a["Tax Revenue (UGX Bn)"], label="Scenario A", marker='o')
plt.plot(df_b["Year"], df_b["Tax Revenue (UGX Bn)"], label="Scenario B", marker='o')
plt.xlabel("Year")
plt.ylabel("Tax Revenue (UGX Billions)")
plt.legend()
plt.grid(True)
st.pyplot(plt)

# Final year comparison
final_year_data = {
    "Scenario": ["A", "B"],
    "Tax Base (UGX Bn)": [df_a["Tax Base (UGX Bn)"].iloc[-1], df_b["Tax Base (UGX Bn)"].iloc[-1]],
    "Tax Revenue (UGX Bn)": [df_a["Tax Revenue (UGX Bn)"].iloc[-1], df_b["Tax Revenue (UGX Bn)"].iloc[-1]]
}
final_df = pd.DataFrame(final_year_data)

# Make sure columns are numeric for formatting
final_df["Tax Base (UGX Bn)"] = pd.to_numeric(final_df["Tax Base (UGX Bn)"])
final_df["Tax Revenue (UGX Bn)"] = pd.to_numeric(final_df["Tax Revenue (UGX Bn)"])

st.subheader("📋 Final Year Comparison")
st.table(final_df.style.format({"Tax Base (UGX Bn)": "{:.2f}", "Tax Revenue (UGX Bn)": "{:.2f}"}))
