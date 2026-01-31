from pathlib import Path
import streamlit as st

from services.loader import load_excel
from services.validators import check_columns

# ------------------- Page Configuration -------------------
st.set_page_config(
    page_title="Payroll Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- Load Corporate CSS -------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSS_PATH = BASE_DIR / "styles" / "corporate.css"

def load_css():
    if CSS_PATH.exists():
        with open(CSS_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ------------------- Page Header -------------------
st.title("Payroll Analysis")
st.write("Upload the required payroll files to start the analysis.")

st.divider()

# ------------------- File Uploads -------------------
st.subheader("📂 Required Files")

col1, col2 = st.columns(2)

with col1:
    f_activos_retirados = st.file_uploader(
    "Base Activos - Retirados Meli.xlsx",
    type=["xlsx"]
    )

    f_conso_nomina = st.file_uploader(
        "Conso_Nomina.xlsx",
        type=["xlsx"]
    )

    f_acumulado = st.file_uploader(
        "Acumulado_Mes.xlsx",
        type=["xlsx"]
    )


with col2:
    f_personal_nacional = st.file_uploader(
        "Base Personal Nacional.xlsx",
        type=["xlsx"]
    )
        
    f_prenomina = st.file_uploader(
        "Conso_PreNomina.xlsx",
        type=["xlsx"]
    )

    f_agrupaciones = st.file_uploader(
        "Agrupaciones.xlsx",
        type=["xlsx"]
    )

# ------------------- Validation & Load -------------------
if all([
    f_activos_retirados,
    f_conso_nomina,
    f_prenomina,
    f_acumulado,
    f_agrupaciones,
    f_personal_nacional
]):
    st.success("✅ All files uploaded successfully")

    with st.spinner("Loading and validating files..."):

        # -------- Load files --------
        dfs = load_excel(
            f_activos_retirados,
            sheets={
                "activos": "Activo",
                "retirados": "Retirado"
            },
            name="Base Activos - Retirados Meli"
        )

        df_activos = dfs["activos"]
        df_retirados = dfs["retirados"]

        df_conso_nomina = load_excel(
            f_conso_nomina, name="Conso_Nomina"
        )

        df_prenomina = load_excel(
            f_prenomina, name="Conso_PreNomina"
        )

        df_acumulado = load_excel(
            f_acumulado, name="Acumulado_Mes"
        )

        df_agrupaciones = load_excel(
            f_agrupaciones, sheet="Agrupaciones", name="Agrupaciones"
        )

        df_personal_nacional = load_excel(
            f_personal_nacional, sheet="BD Personal DHL", name="Base Personal Nacional"
        )

        # -------- Column validation --------
        check_columns(
            df_activos,
            ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"],
            "Base Activos - Activo"
        )

        check_columns(
            df_retirados,
            ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA"],
            "Base Activos - Retirado"
        )

        check_columns(
            df_conso_nomina,
            ["CEDULA", "CARGO NOMINA", "SALARIO BASICO"],
            "Conso_Nomina"
        )

        check_columns(
            df_prenomina,
            ["CEDULA", "BASICO"],
            "Conso_PreNomina"
        )

        check_columns(
            df_personal_nacional,
            ["OPERACION", "ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"],
            "Base Personal Nacional"
        )

        check_columns(
            df_agrupaciones,
            ["CONCEPTO", "DESCRIPCION", "AGRUPACION"],
            "Agrupaciones"
        )

        check_columns(
            df_acumulado,
            [
                "NÓMINA", "PROCESO", "AÑO PROCESO", "PERIODO PROCESO", "MES PROCESO",
                "NUMERO DOCUMENTO", "PRIMER APELLIDO", "SEGUNDO APELLIDO", "NOMBRES",
                "CONCEPTO", "DESCRIPCIÓN", "CANTIDAD", "MONTO", "NETO", "SMRU"
            ],
            "Acumulado_Mes"
        )

    st.success("🚀 Files loaded and validated successfully. Ready for analysis.")

else:
    st.info("⬆️ Please upload all required files to proceed.")
