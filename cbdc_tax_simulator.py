import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import json
import tempfile

# --- App Config ---
st.set_page_config(page_title="CBDC Tax Base Simulator - Uganda", layout="wide")

# --- Helper Functions ---

def simulate_tax_base(baseline, adoption_rate, compliance_increase, tax_rate, years, alpha=0.5):
    years_arr = np.arange(1, years + 1)
    multiplier = 1 + alpha * (adoption_rate / 100) * (compliance_increase / 100) * years_arr
    tax_base = baseline * multiplier
    tax_revenue = tax_base * (tax_rate / 100)
    df = pd.DataFrame({
        "Year": years_arr,
        "Tax Base (UGX Bn)": tax_base,
        "Tax Revenue (UGX Bn)": tax_revenue
    })
    return df

def generate_pdf(scenario_a, scenario_b, params_a, params_b, time_horizon):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CBDC Tax Base Simulation Report - Uganda", 0, 1, "C")
    pdf.ln(5)

    def add_scenario_to_pdf(title, df, params):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, 0, 1)
        pdf.set_font("Arial", size=12)
        for k, v in params.items():
            pdf.cell(0, 8, f"{k}: {v}", 0, 1)
        pdf.ln(3)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(25, 8, "Year", 1)
        pdf.cell(50, 8, "Tax Base (UGX Bn)", 1)
        pdf.cell(50, 8, "Tax Revenue (UGX Bn)", 1)
        pdf.ln()
        pdf.set_font("Arial", size=12)
        for _, row in df.iterrows():
            pdf.cell(25, 8, str(int(row["Year"])), 1)
            pdf.cell(50, 8, f"{row['Tax Base (UGX Bn)']:.2f}", 1)
            pdf.cell(50, 8, f"{row['Tax Revenue (UGX Bn)']:.2f}", 1)
            pdf.ln()
        pdf.ln(8)

    add_scenario_to_pdf("Scenario A Parameters & Results", scenario_a, params_a)
    add_scenario_to_pdf("Scenario B Parameters & Results", scenario_b, params_b)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

def save_simulation(params_a, params_b, time_horizon):
    data = {
        "scenario_a": params_a,
        "scenario_b": params_b,
        "time_horizon": time_horizon
    }
    json_str = json.dumps(data)
    return json_str

def load_simulation(json_str):
    try:
        data = json.loads(json_str)
        return data.get("scenario_a"), data.get("scenario_b"), data.get("time_horizon")
    except Exception:
        return None, None, None

# --- UI ---

st.title("📊 CBDC Impact on Tax Base Expansion in Uganda")
st.markdown("""
Compare two economic scenarios with different CBDC adoption strategies.
Use the controls below to adjust parameters and explore outcomes.
""")

# Mobile friendly: use columns for input grouping
col1, col2 = st.columns(2)

with col1:
    st.header("Scenario A")
    baseline_a = st.number_input("Baseline Tax Base A (UGX Billions)", min_value=100.0, value=5000.0, step=100.0, key="ba")
    adoption_a = st.slider("CBDC Adoption Rate A (%)", 0, 100, 50, key="aa")
    compliance_a = st.slider("Compliance Improvement A (%)", 0, 100, 20, key="ca")
    tax_rate_a = st.slider("Effective Tax Rate A (%)", 0, 50, 15, key="tra")

with col2:
    st.header("Scenario B")
    baseline_b = st.number_input("Baseline Tax Base B (UGX Billions)", min_value=100.0, value=5000.0, step=100.0, key="bb")
    adoption_b = st.slider("CBDC Adoption Rate B (%)", 0, 100, 50, key="ab")
    compliance_b = st.slider("Compliance Improvement B (%)", 0, 100, 20, key="cb")
    tax_rate_b = st.slider("Effective Tax Rate B (%)", 0, 50, 15, key="trb")

time_horizon = st.slider("Time Horizon (Years)", 1, 10, 5, key="th")

# Run simulations
df_a = simulate_tax_base(baseline_a, adoption_a, compliance_a, tax_rate_a, time_horizon)
df_b = simulate_tax_base(baseline_b, adoption_b, compliance_b, tax_rate_b, time_horizon)

# Display charts side by side
st.subheader("📈 Tax Base Over Time")
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.line_chart(df_a.set_index("Year")["Tax Base (UGX Bn)"], use_container_width=True)
    st.caption("Scenario A Tax Base")
with chart_col2:
    st.line_chart(df_b.set_index("Year")["Tax Base (UGX Bn)"], use_container_width=True)
    st.caption("Scenario B Tax Base")

st.subheader("📈 Tax Revenue Over Time")
rev_col1, rev_col2 = st.columns(2)
with rev_col1:
    st.line_chart(df_a.set_index("Year")["Tax Revenue (UGX Bn)"], use_container_width=True)
    st.caption("Scenario A Tax Revenue")
with rev_col2:
    st.line_chart(df_b.set_index("Year")["Tax Revenue (UGX Bn)"], use_container_width=True)
    st.caption("Scenario B Tax Revenue")

# Final Year Summary
st.subheader("📋 Final Year Comparison")
final_a = df_a.iloc[-1]
final_b = df_b.iloc[-1]

final_df = pd.DataFrame({
    "Scenario": ["A", "B"],
    "Tax Base (UGX Bn)": [final_a["Tax Base (UGX Bn)"], final_b["Tax Base (UGX Bn)"]],
    "Tax Revenue (UGX Bn)": [final_a["Tax Revenue (UGX Bn)"], final_b["Tax Revenue (UGX Bn)"]],
})

st.table(final_df.style.format({"Tax Base (UGX Bn)": "{:.2f}", "Tax Revenue (UGX Bn)": "{:.2f}"}))

# Save/load favorite simulations (simple JSON export/import)

with st.expander("💾 Save / Load Favorite Simulations"):
    col_save, col_load = st.columns(2)

    with col_save:
        if st.button("Save Current Simulation"):
            params_a = {
                "Baseline Tax Base (UGX Bn)": baseline_a,
                "CBDC Adoption Rate (%)": adoption_a,
                "Compliance Improvement (%)": compliance_a,
                "Tax Rate (%)": tax_rate_a
            }
            params_b = {
                "Baseline Tax Base (UGX Bn)": baseline_b,
                "CBDC Adoption Rate (%)": adoption_b,
                "Compliance Improvement (%)": compliance_b,
                "Tax Rate (%)": tax_rate_b
            }
            json_str = save_simulation(params_a, params_b, time_horizon)
            st.download_button("Download Simulation JSON", data=json_str, file_name="cbdc_simulation.json")

    with col_load:
        uploaded_file = st.file_uploader("Upload Simulation JSON", type=["json"])
        if uploaded_file is not None:
            content = uploaded_file.read().decode("utf-8")
            loaded_a, loaded_b, loaded_th = load_simulation(content)
            if loaded_a and loaded_b and loaded_th:
                st.success("Loaded saved simulation!")
                # Set session state to update inputs
                st.session_state.ba = loaded_a["Baseline Tax Base (UGX Bn)"]
                st.session_state.aa = loaded_a["CBDC Adoption Rate (%)"]
                st.session_state.ca = loaded_a["Compliance Improvement (%)"]
                st.session_state.tra = loaded_a["Tax Rate (%)"]

                st.session_state.bb = loaded_b["Baseline Tax Base (UGX Bn)"]
                st.session_state.ab = loaded_b["CBDC Adoption Rate (%)"]
                st.session_state.cb = loaded_b["Compliance Improvement (%)"]
                st.session_state.trb = loaded_b["Tax Rate (%)"]

                st.session_state.th = loaded_th
                st.experimental_rerun()
            else:
                st.error("Failed to load simulation file.")

# PDF Report Generation and Download
if st.button("📄 Download Combined Simulation Report (PDF)"):
    params_a = {
        "Baseline Tax Base": f"{baseline_a:.2f} UGX Bn",
        "CBDC Adoption Rate": f"{adoption_a}%",
        "Compliance Improvement": f"{compliance_a}%",
        "Tax Rate": f"{tax_rate_a}%",
        "Time Horizon": f"{time_horizon} years"
    }
    params_b = {
        "Baseline Tax Base": f"{baseline_b:.2f} UGX Bn",
        "CBDC Adoption Rate": f"{adoption_b}%",
        "Compliance Improvement": f"{compliance_b}%",
        "Tax Rate": f"{tax_rate_b}%",
        "Time Horizon": f"{time_horizon} years"
    }
    pdf_path = generate_pdf(df_a, df_b, params_a, params_b, time_horizon)
    with open(pdf_path, "rb") as f:
        st.download_button("Download PDF", data=f, file_name="CBDC_Simulation_Report_Uganda.pdf", mime="application/pdf")

st.markdown("---")
st.caption("Developed for Uganda CBDC Tax Base Expansion Simulation")

