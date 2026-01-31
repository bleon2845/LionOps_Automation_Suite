import streamlit as st

def check_columns(df, columnas_requeridas, nombre_df):
    cols_actuales = [c.upper() for c in df.columns]
    faltantes = [c for c in columnas_requeridas if c.upper() not in cols_actuales]

    if faltantes:
        st.error(f"❌ Columns are missing in {nombre_df}: {', '.join(faltantes)}")
        st.stop()
