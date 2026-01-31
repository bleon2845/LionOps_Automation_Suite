import streamlit as st
import pandas as pd

def load_excel(file, sheet=None, sheets: dict = None, name: str = ""):
    try:
        # -------- Multiple sheets --------
        if sheets:
            data = pd.read_excel(file, sheet_name=list(sheets.values()))
            return {
                key: data[sheet_name]
                for key, sheet_name in sheets.items()
            }

        # -------- Single sheet --------
        if sheet:
            return pd.read_excel(file, sheet_name=sheet)

        # -------- Full file --------
        return pd.read_excel(file)

    except Exception as e:
        st.error(f"❌ Error loading {name}: {e}")
        st.stop()
