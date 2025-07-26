import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt

st.title("PSP vs Stationing Chart")

uploaded = st.file_uploader("Upload Excel (.xlsx) with required columns", type=["xlsx"])
if uploaded:
    df = pd.read_excel(BytesIO(uploaded.getvalue()), engine="openpyxl")
    st.write("Loaded data preview:", df.head(), use_container_width=True)

    required = ["Stationing (m)", "ON PSP (VE V)", "OFF PSP (VE V)"]
    if all(col in df.columns for col in required):
        df_clean = df[required].dropna(subset=["Stationing (m)"]).fillna(0)
        df_clean = df_clean.astype({
            "Stationing (m)": float,
            "ON PSP (VE V)": float,
            "OFF PSP (VE V)": float
        })

        df_long = df_clean.melt(
            id_vars="Stationing (m)",
            value_vars=["ON PSP (VE V)", "OFF PSP (VE V)"],
            var_name="PSP Type",
            value_name="PSP Value"
        )

        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x=alt.X("Stationing (m):Q", title="Stationing (m)"),
            y=alt.Y("PSP Value:Q", title="PSP (VE V)"),
            color=alt.Color("PSP Type:N", title="")
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.error(f"Excel file must contain columns: {required}")
else:
    st.info("Upload your Excel (.xlsx) file containing the data.")
