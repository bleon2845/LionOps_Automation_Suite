from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # pages -> app -> root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from services.loader import load_excel
from services.validators import check_columns
from services.mergers import merge_dataframes
from services.payroll_rules import calcular_periodos_nomina
from services.filters import filter_dataframe
from services.columns import delete_columns, delete_duplicate, new_column, new_column_with_condition, update_column

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
st.subheader("Payroll Data Upload & Validation")
st.divider()
# ------------------- Payroll Parameters -------------------
st.subheader("💰 Payroll Parameters")

with st.form("salary_form", clear_on_submit=False):
    salary = st.number_input(
        "Monthly Base Salary Input / SMLV",
        min_value=0,
        step=50_000,
        format="%d",
        help="Input the current legal minimum wage (SMLV) for calculations",
    )
    confirm = st.form_submit_button("Confirm Base Salary")

if confirm:
    if salary <= 0:
        st.error("❌ Please enter a valid salary greater than 0.")
        st.stop()
    st.session_state["salary_base"] = int(salary)
    st.success(f"✅ Base Salary confirmed: ${salary:,.0f}")

# If salary not confirmed, prompt user
if "salary_base" not in st.session_state:
    st.warning("Must confirm Base Salary to proceed.")
    st.stop()

salary_base = st.session_state["salary_base"]
st.info(f"Using Base Salary: ${salary_base:,.0f}")

st.divider()

# ------------------- Instructions -------------------
st.subheader("📄 Instructions")
st.write("Upload the required payroll files to start the analysis.")
st.divider()

# ------------------- File Uploads -------------------
st.subheader("📂 Required Files")

col1, col2 = st.columns(2)

with col1:
    f_activos_retirados = st.file_uploader("Base Activos - Retirados Meli.xlsx",type=["xlsx"])
    f_conso_nomina = st.file_uploader("Conso_Nomina.xlsx",type=["xlsx"])
    f_acumulado = st.file_uploader("Acumulado_Mes.xlsx",type=["xlsx"])

with col2:
    f_personal_nacional = st.file_uploader("Base Personal Nacional.xlsx",type=["xlsx"])        
    f_prenomina = st.file_uploader("Conso_PreNomina.xlsx",type=["xlsx"])
    f_agrupaciones = st.file_uploader("Agrupaciones.xlsx",type=["xlsx"])

# ------------------- Validation & Load -------------------
all_files_ok = all([
    f_activos_retirados,
    f_conso_nomina,
    f_prenomina,
    f_acumulado,
    f_agrupaciones,
    f_personal_nacional
])

if not all_files_ok:
    st.info("⬆️ Please upload all required files to proceed.")
    st.stop()

st.success("✅ All files uploaded successfully")

run = st.button("Run analysis")

if not run:
    st.info("Press **Run analysis** to load, validate and continue.")
    st.stop()

# ------------------- Validation & Load -------------------
with st.spinner("Loading and validating files..."):

    # ------------------- Load files -------------------
    dfs = load_excel(
        f_activos_retirados,
        sheets={"activos": "Activo", "retirados": "Retirado"},
        name="Base Activos - Retirados Meli"
    )
    df_activos = dfs["activos"]
    df_retirados = dfs["retirados"]

    df_conso_nomina = load_excel(f_conso_nomina, name="Conso_Nomina")
    df_prenomina = load_excel(f_prenomina, name="Conso_PreNomina")
    df_acumulado = load_excel(f_acumulado, name="Acumulado_Mes")
    df_agrupaciones = load_excel(f_agrupaciones, sheet="Agrupaciones", name="Agrupaciones")
    df_personal_nacional = load_excel(f_personal_nacional, sheet="BD Personal DHL", name="Base Personal Nacional")

    # ------------------- Column validation -------------------
    check_columns(df_activos, ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"], "Base Activos - Activo")
    check_columns(df_retirados, ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA"], "Base Activos - Retirado")
    check_columns(df_conso_nomina, ["CEDULA", "CARGO NOMINA", "SALARIO BASICO"], "Conso_Nomina")
    check_columns(df_prenomina, ["CEDULA", "BASICO"], "Conso_PreNomina")
    check_columns(df_personal_nacional, ["OPERACION", "ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"], "Base Personal Nacional")
    check_columns(df_agrupaciones, ["CONCEPTO", "DESCRIPCION", "AGRUPACION"], "Agrupaciones")
    check_columns(df_acumulado,["NÓMINA", "PROCESO", "AÑO PROCESO", "PERIODO PROCESO", "MES PROCESO","NUMERO DOCUMENTO", "PRIMER APELLIDO", "SEGUNDO APELLIDO", "NOMBRES","CONCEPTO", "DESCRIPCIÓN", "CANTIDAD", "MONTO", "NETO", "SMRU"],"Acumulado_Mes")
    
    st.success("🚀 Files loaded and validated successfully. Ready for analysis.")

    st.session_state["dfs_loaded"] = {
        "activos": df_activos,
        "retirados": df_retirados,
        "conso_nomina": df_conso_nomina,
        "prenomina": df_prenomina,
        "acumulado": df_acumulado,
        "agrupaciones": df_agrupaciones,
        "personal_nacional": df_personal_nacional
    }

# ------------------- Calculate Payroll Periods -------------------
periodos = calcular_periodos_nomina(df_acumulado)

nMesActual = periodos["n_mes_actual"]
nMesAnterior = periodos["n_mes_anterior"]
nombreMesActual = periodos["nombre_mes_actual"]
nomMesAnterior = periodos["nombre_mes_anterior"]
nomMesIBC = periodos["nombre_mes_ibc"]
corteNomina1 = periodos["corte_nomina_1"]
corteNomina2 = periodos["corte_nomina_2"]

# ------------------- Filter DataFrames by Periods -------------------
df_consoNomina = filter_dataframe(
    df=df_conso_nomina,
    column="MES",
    values=periodos["nombre_mes_anterior"]
)

df_prenomina = filter_dataframe(
    df=df_prenomina,
    column="Periodo",
    values=[
        periodos["corte_nomina_1"],
        periodos["corte_nomina_2"]
    ]
)

# ------------------- Select Relevant Columns -------------------
df_activos = delete_columns(
    df_activos,
    columns=[
        col for col in df_activos.columns
        if col not in ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"]
    ]
)

df_retirados = delete_columns(
    df_retirados,
    columns=[
        col for col in df_retirados.columns
        if col not in ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA"]
    ]
)

df_consoNomina = delete_columns(
    df_conso_nomina,
    columns=[
        col for col in df_conso_nomina.columns
        if col not in ["CEDULA", "CARGO NOMINA", "SALARIO BASICO"]
    ]
)

df_preNomina = delete_columns(
    df_prenomina,
    columns=[
        col for col in df_prenomina.columns
        if col not in ["Cedula", "Basico"]
    ]
)

df_personalNacional = delete_columns(
    df_personal_nacional,
    columns=[
        col for col in df_personal_nacional.columns
        if col not in ["OPERACION","ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"]
    ]
)

# ------------------- Insert New Columns -------------------
df_activos = new_column(df_activos, "FECHA DE BAJA", "1990-01-01 00:00:00")

# ------------------- Consolidate DataFrames -------------------
df_retirados = merge_dataframes(
    df_left=df_retirados,
    df_right=df_consoNomina,
    left_key="CEDULA",
    right_key="CEDULA",
    how="left",
    merge_name="Retirados vs Conso_Nomina")

df_retirados = merge_dataframes(
    df_left=df_retirados,
    df_right=df_preNomina,
    left_key="CEDULA",
    right_key="Cedula",
    how="left",
    merge_name="Retirados vs PreNomina"
)

# ------------------- Delete Column -------------------
df_retirados = delete_columns(df_retirados, columns=["CARGO NOMINA"])

# ------------------- Delete Duplicates -------------------
df_retirados = delete_duplicate(df_retirados, column_name="CEDULA", default_value="first")

# ------------------- Insert New Columns with Condition -------------------
df_retirados = new_column_with_condition(
    df_retirados,
    column_name="SALARIO MENSUAL",
    condition=df_retirados["SALARIO BASICO"] != "",
    value_if_true=df_retirados["SALARIO BASICO"],
    value_if_false=df_retirados["Basico"]
)

# ------------------- Update Columns -------------------
df_retirados = update_column(
    df_retirados,
    column_name="SALARIO MENSUAL",
    condition=df_retirados["SALARIO BASICO"].isna(),
    new_value=df_retirados["Basico"]
)





# ------------------- Display Preview -------------------
st.divider()
st.subheader("📋 Preview – Retired Employees (df_retirados)")

st.dataframe(
    df_retirados,
    use_container_width=True
)
