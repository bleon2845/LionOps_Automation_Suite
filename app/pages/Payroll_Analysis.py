from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # pages -> app -> root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from services.loader import load_excel
from services.validators import check_columns
from services.mergers import concat_dataframes, merge_dataframes
from services.payroll_rules import calcular_periodos_nomina
from services.filters import filter_dataframe
from services.columns import (change_to_datetime, delete_columns, delete_duplicate, filter_and_drop_duplicates,
                                modify_register, new_column, new_column_with_condition, order_columns, rename_columns, 
                                update_column)

DEV_MODE = True

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

DEV_DATA_PATH = PROJECT_ROOT / "dev" / "data"
@st.cache_data(show_spinner=False)

def load_dev_data() -> dict:
    """
    Loads all Excel files from dev/data and returns dict of dataframes.
    Cached to avoid re-reading on every rerun.
    """ 
    base_activos = DEV_DATA_PATH / "Base Activos - Retirados Meli.xlsx"
    conso_nomina = DEV_DATA_PATH / "Conso_Nomina.xlsx"
    pre_nomina = DEV_DATA_PATH / "Conso_PreNomina.xlsx"
    acumulado = DEV_DATA_PATH / "Acumulado_Mes.xlsx"
    agrupaciones = DEV_DATA_PATH / "Agrupaciones.xlsx"
    base_personal = DEV_DATA_PATH / "Base Personal Nacional.xlsx"
    funza = DEV_DATA_PATH / "Planta de personal DHL.xlsx"

    # Load activos/retirados from same file with 2 sheets
    dfs_act = load_excel(
        base_activos,
        sheets={"activos": "Activo", "retirados": "Retirado"},
        name="Base Activos - Retirados Meli"
    )

    return {
        "activos": dfs_act["activos"],
        "retirados": dfs_act["retirados"],
        "conso_nomina": load_excel(conso_nomina, name="Conso_Nomina"),
        "prenomina": load_excel(pre_nomina, name="Conso_PreNomina"),
        "acumulado": load_excel(acumulado, name="Acumulado_Mes"),
        "agrupaciones": load_excel(agrupaciones, sheet="Agrupaciones", name="Agrupaciones"),
        "personal_nacional": load_excel(base_personal, sheet="BD Personal DHL", name="Base Personal Nacional"),
        "personal_funza": load_excel(funza, sheet="RETIRADOS", name="Planta de personal DHL"),
    }

def dev_controls():
    st.sidebar.divider()
    st.sidebar.subheader("🧪 Dev Tools")

    if st.sidebar.button("🔄 Clear cache (reload Excels)"):
        st.cache_data.clear()
        st.success("Cache cleared. Reloading on next run.")

    if st.sidebar.button("🧹 Reset session"):
        st.session_state.clear()
        st.success("Session reset. Reload the page.")


# ------------------- Payroll Parameters -------------------
st.subheader("💰 Payroll Parameters")

if DEV_MODE:
    dev_controls()

    # salario fijo
    if "salary_base" not in st.session_state:
        st.session_state["salary_base"] = 1750000  # cambia a tu valor de prueba

    salary_base = st.session_state["salary_base"]
    st.info(f"🧪 DEV MODE – Base Salary fixed at ${salary_base:,.0f}")

else:
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

    if "salary_base" not in st.session_state:
        st.warning("Must confirm Base Salary to proceed.")
        st.stop()

    salary_base = st.session_state["salary_base"]
    st.info(f"Using Base Salary: ${salary_base:,.0f}")

st.divider()

# ============================================================
# Data input (DEV auto / PROD upload)
# ============================================================
st.subheader("📂 Required Files")

if DEV_MODE:
    # Validación básica de rutas
    if not DEV_DATA_PATH.exists():
        st.error(f"DEV data folder not found: {DEV_DATA_PATH}")
        st.stop()

    st.info("🧪 DEV MODE – Loading local files automatically from dev/data")

    with st.spinner("Loading local DEV files (cached)..."):
        dfs = load_dev_data()

    df_activos = dfs["activos"]
    df_retirados = dfs["retirados"]
    df_conso_nomina = dfs["conso_nomina"]
    df_prenomina = dfs["prenomina"]
    df_acumulado = dfs["acumulado"]
    df_agrupaciones = dfs["agrupaciones"]
    df_personalNacional = dfs["personal_nacional"]
    df_personalNacionalFunza = dfs["personal_funza"]

    st.success("✅ DEV files loaded")

else:
    col1, col2 = st.columns(2)

    with col1:
        f_activos_retirados = st.file_uploader("Base Activos - Retirados Meli.xlsx", type=["xlsx"])
        f_conso_nomina = st.file_uploader("Conso_Nomina.xlsx", type=["xlsx"])
        f_acumulado = st.file_uploader("Acumulado_Mes.xlsx", type=["xlsx"])
        f_personal_nacional = st.file_uploader("Base Personal Nacional.xlsx", type=["xlsx"])

    with col2:
        f_prenomina = st.file_uploader("Conso_PreNomina.xlsx", type=["xlsx"])
        f_agrupaciones = st.file_uploader("Agrupaciones.xlsx", type=["xlsx"])
        f_personal_nacionalFunza = st.file_uploader("Planta de personal DHL.xlsx", type=["xlsx"])

    all_files_ok = all([
        f_activos_retirados,
        f_conso_nomina,
        f_prenomina,
        f_acumulado,
        f_agrupaciones,
        f_personal_nacional,
        f_personal_nacionalFunza,
    ])

    if not all_files_ok:
        st.info("⬆️ Please upload all required files to proceed.")
        st.stop()

    run = st.button("Run analysis")
    if not run:
        st.info("Press **Run analysis** to load, validate and continue.")
        st.stop()

    with st.spinner("Loading and validating files..."):
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
        df_personalNacional = load_excel(f_personal_nacional, sheet="BD Personal DHL", name="Base Personal Nacional")
        df_personalNacionalFunza = load_excel(f_personal_nacionalFunza, sheet="RETIRADOS", name="Planta de personal DHL")

        st.success("✅ PROD files loaded")

# ============================================================
# Validation (both DEV & PROD)
# ============================================================
with st.spinner("Validating columns..."):
    check_columns(df_activos, ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"], "Base Activos - Activo")
    check_columns(df_retirados, ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA"], "Base Activos - Retirado")
    check_columns(df_conso_nomina, ["CEDULA", "CARGO NOMINA", "SALARIO BASICO"], "Conso_Nomina")
    check_columns(df_prenomina, ["CEDULA", "BASICO"], "Conso_PreNomina")
    check_columns(df_personalNacional, ["OPERACION", "ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"], "Base Personal Nacional")
    check_columns(df_agrupaciones, ["CONCEPTO", "DESCRIPCION", "AGRUPACION"], "Agrupaciones")
    check_columns(df_acumulado, ["NÓMINA", "PROCESO", "AÑO PROCESO", "PERIODO PROCESO", "MES PROCESO",
                                 "NUMERO DOCUMENTO", "PRIMER APELLIDO", "SEGUNDO APELLIDO", "NOMBRES",
                                 "CONCEPTO", "DESCRIPCIÓN", "CANTIDAD", "MONTO", "NETO", "SMRU"], "Acumulado_Mes")
    check_columns(df_personalNacionalFunza, ["CEDULA", "CARGO DHL", "FECHA INGRESO", "FECHA RETIRO"], "Planta de personal DHL")

st.success("🚀 Files loaded and validated successfully. Ready for analysis.")
st.divider()

# ------------------- Calculate Payroll Periods -------------------
periodos = calcular_periodos_nomina(df_acumulado)
st.write("📌 Periodos calculados:", periodos)

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
    df_personalNacional,
    columns=[
        col for col in df_personalNacional.columns
        if col not in ["OPERACION","ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"]
    ]
)


# ------------------- Insert New Columns -------------------
df_activos = new_column(df_activos, "FECHA DE BAJA", "1990-01-01 00:00:00")
df_personalNacionalFunza = new_column(df_personalNacionalFunza, "OPERACION", "Funza") 

# ------------------- Select Relevant Columns -------------------
df_personalNacionalFunza = delete_columns(
    df_personalNacionalFunza,
    columns=[
        col for col in df_personalNacionalFunza.columns
        if col not in ["OPERACION", "CEDULA", "CARGO DHL", "FECHA INGRESO", "FECHA RETIRO"]
    ]
)

#--------------- CONSOLIDAR DATA DE EMPLEADOS ACTIVOS RETIRADOS ---------------
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

# ------------------- Delete Column -------------------
df_retirados = delete_columns(df_retirados, columns=["SALARIO BASICO", "Basico","Cedula"])

# ------------------- Select Relevant Columns -------------------
df_activos = delete_columns(
    df_activos,
    columns=[
        col for col in df_activos.columns
        if col not in ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA", "SALARIO MENSUAL"]
    ]
)

# ------------------- Concat DataFrames -------------------
df_activos = concat_dataframes(df_activos, df_retirados, axis=0)

# -------------- UNIR BASES NACIONAL AMERICAS Y FUNZA  ---------------
# ------------------- Rename Columns -------------------
df_personalNacionalFunza = rename_columns(df_personalNacionalFunza, columns_mapping={
    "CEDULA": "ID",
    "CARGO DHL": "CARGO NÓMINA",
    "FECHA INGRESO": "FECHA DE INGRESO",
    "FECHA RETIRO": "FECHA DE RETIRO"
})

# ------------------- Delete Duplicates -------------------
df_personalNacional = delete_duplicate(df_personalNacional, column_name="ID", default_value="last")
df_personalNacionalFunza = delete_duplicate(df_personalNacionalFunza, column_name="ID", default_value="last")

# ------------------- Concat DataFrames -------------------
df_personalNacional = concat_dataframes(df_personalNacional, df_personalNacionalFunza, axis=0)

# --------------- ELIMINAR DUPLICADOS DE BASE NACIONAL Y RETIRADOS -----------

# ------------------- Delete Duplicates -------------------
df_personalNacionalRetirados = filter_and_drop_duplicates(df_personalNacional, filter_column="FECHA DE RETIRO",
                                                filter_value="1990-01-01 00:00:00",operator="!=", duplicate_column="ID",
                                                keep="last")

# ------------------- Order Columns -------------------
df_personalNacionalRetirados = order_columns(df_personalNacionalRetirados, column_name="FECHA DE RETIRO", ascending=True)
df_personalNacional = order_columns(df_personalNacional, column_name="FECHA DE RETIRO", ascending=True)

# ------------------- Delete Duplicates -------------------
df_personalNacional = delete_duplicate(df_personalNacional, column_name="ID", default_value="last")
df_personalNacionalRetirados = delete_duplicate(df_personalNacionalRetirados, column_name="ID", default_value="last")

#--------------- VERIFICAR CARGO FECHAS DE INGRESO Y RETIRO DE EMPLEADOS ---------------
# ------------------- Merge DataFrames -------------------
df_activos = merge_dataframes(
    df_left=df_activos,
    df_right=df_personalNacionalRetirados,
    left_key="CEDULA",
    right_key="ID",
    how="left",
    merge_name="Activos vs Personal Nacional"
)

# ------------------- Delete Columns -------------------
df_activos = delete_columns(df_activos, columns=["CARGO NÓMINA", "OPERACION", "CARGO MELI"])

# ------------------- Change Register in Column -------------------
df_activos = modify_register(df_activos, column_name="NOMBRE DEL PUESTO", condition=".", position=1)

# ------------------- Change Register to DateTime -------------------
df_activos = change_to_datetime(df_activos, column_name="FECHA DE INGRESO_x")
df_activos = change_to_datetime(df_activos, column_name="FECHA DE INGRESO_y")

# ------------------- Update Column with Condition -------------------
fecha_vacia = "1990-01-01 00:00:00"

df_activos = update_column(df_activos,column_name="FECHA DE BAJA",
    condition=df_activos["FECHA DE BAJA"].isna() | (df_activos["FECHA DE BAJA"] == fecha_vacia),
    new_value=df_activos["FECHA DE RETIRO"]
)

df_activos = update_column(df_activos,column_name="FECHA DE INGRESO_x",
    condition=df_activos["FECHA DE INGRESO_x"].isna() | (df_activos["FECHA DE INGRESO_x"] == fecha_vacia),
    new_value=df_activos["FECHA DE INGRESO_y"]
)

# ------------------- Delete Columns -------------------
df_activos = delete_columns(df_activos, columns=["FECHA DE INGRESO_y", "ID", "FECHA DE RETIRO"])

# ------------------- Rename Columns -------------------
df_activos = rename_columns(df_activos, columns_mapping={"FECHA DE INGRESO_x": "FECHA DE INGRESO"})


    








# ------------------- Display Preview -------------------
st.divider()
st.subheader("📋 Preview – Retired Employees (df_retirados)")


st.dataframe(
    df_activos,
    use_container_width=True
)

