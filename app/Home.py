import streamlit as st
from pathlib import Path

# ------------------- Configuration -------------------
st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- Paths ------------------- 
BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = BASE_DIR / "styles" / "corporate.css"

# ------------------- Load CSS -------------------
def load_css():
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ------------------- Home Page Content -------------------
st.title("LionOps Automation Suite")
st.subheader("Automation & Advanced Analytics Platform")

st.markdown("""
Bienvenido a **LionOps Automation Suite**.

Seleccione un módulo desde el menú lateral para comenzar.
""")
