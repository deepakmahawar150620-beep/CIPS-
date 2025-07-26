import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

st.title("Pipeline Corrosion & Stress Analysis")

uploaded = st.file_uploader("Upload Excel (.xlsx) with data", type=["xlsx"])
if not uploaded:
    st.info("Please upload your Excel file.")
    st.stop()

df = pd.read_excel(BytesIO(uploaded.getvalue()), engine="openpyxl")
st.write(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns")
st.dataframe(df.head())

required = ["Stationing (m)", "ON PSP (VE V)", "OFF PSP (VE V)",
            "Soil Resistivity (Ω-cm)", "Hoop Stress(Mpa)", "Distance from Pump(KM)"]

if not all(col in df.columns for col in required):
    st.error(f"Missing columns. Required: {required}")
    st.stop()

df_clean = df[required].dropna(subset=["Stationing (m)"]).fillna(0)
df_clean = df_clean.astype({col: float for col in required})

# Melt for PSP plot
psp_long = df_clean.melt(
    id_vars="Stationing (m)",
    value_vars=["ON PSP (VE V)", "OFF PSP (VE V)"],
    var_name="PSP Type",
    value_name="PSP Value"
)

# Chart 1: PSP vs Stationing
psp_chart = alt.Chart(psp_long).mark_line(point=True).encode(
    x=alt.X("Stationing (m):Q", title="Stationing (m)"),
    y=alt.Y("PSP Value:Q", title="PSP (VE V)"),
    color="PSP Type:N"
).interactive()

st.subheader("PSP vs Stationing")
st.altair_chart(psp_chart, use_container_width=True)

# Chart 2: Soil Resistivity & Hoop Stress vs Stationing
sr_chart = alt.Chart(df_clean).transform_fold(
    ["Soil Resistivity (Ω-cm)", "Hoop Stress(Mpa)"],
    as_=["Metric", "Value"]
).mark_line(point=True).encode(
    x=alt.X("Stationing (m):Q", title="Stationing (m)"),
    y=alt.Y("Value:Q", title="Metric Value"),
    color="Metric:N"
).interactive()

st.subheader("Soil Resistivity & Hoop Stress vs Stationing")
st.altair_chart(sr_chart, use_container_width=True)

# Chart 3: Distance from Pump
dist_chart = alt.Chart(df_clean).mark_line(point=True, color='green').encode(
    x=alt.X("Stationing (m):Q"),
    y=alt.Y("Distance from Pump(KM):Q", title="Distance from Pump (km)")
).interactive()
st.subheader("Distance from Pump vs Stationing")
st.altair_chart(dist_chart, use_container_width=True)

# 🧠 Risk Scoring (simplified logic)
def compute_risk(row):
    rs = row["Soil Resistivity (Ω-cm)"]
    hs = row["Hoop Stress(Mpa)"]
    score = 0
    if rs < 3000: score += 1
    if hs > 0.3 * row.get("SMYS", hs*10): score += 1
    return "High" if score >= 2 else ("Medium" if score == 1 else "Low")

df_clean["Risk"] = df_clean.apply(compute_risk, axis=1)
st.subheader("Risk categorization (simple)")
st.dataframe(df_clean[["Stationing (m)", "Risk"]])
