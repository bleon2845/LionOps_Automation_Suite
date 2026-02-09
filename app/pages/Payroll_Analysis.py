from pathlib import Path
import sys
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[2]  # pages -> app -> root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from services.loader import load_excel
from services.validators import check_columns
from services.mergers import concat_dataframes, merge_dataframes
from services.payroll_rules import calcular_periodos_nomina, calculate_for_concept, check_quantity_with_salary, config_days_month_rules, execute_analysis_days_payroll, get_days_month, pivot_sum, total_by_group_first_row, validate_days_by_novedades, validate_offboarding_weekdays, validate_salary_role_previous_month, validate_vinculation_change
from services.filters import filter_dataframe, filter_by_operator, filter_by_prefix
import services.columns as col

DEV_MODE = True

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    page_title="Payroll Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- LOAD CORPORATE CSS -------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSS_PATH = BASE_DIR / "styles" / "corporate.css"

def load_css():
    if CSS_PATH.exists():
        with open(CSS_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ------------------- PAGE HEADER -------------------
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
    cifras = DEV_DATA_PATH / "Cifras de cierre Meli.xlsx"
    temporales = DEV_DATA_PATH / "Plantillas Facturacion y Nómina 2025 - Mercado libre.xlsx"
    acumulado_año = DEV_DATA_PATH / "Acumulado_Año.xlsx"
    
    

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
        "cifras_mes": load_excel(cifras, sheet="Base", name="Cifras de cierre Meli"),
        "temporales": load_excel(temporales, name="Plantillas Facturacion y Nómina 2025 - Mercado libre"),
        "acumulado_año": load_excel(acumulado_año, name="Acumulado_Año"),
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

# Payroll Parameters
st.subheader("💰 Payroll Parameters")

if DEV_MODE:
    dev_controls()

    # ---------------- SALARY BASE (DEV) ----------------
    if "salary_base" not in st.session_state:
        st.session_state["salary_base"] = 1_750_000  # valor de prueba

    salary_base = st.session_state["salary_base"]
    st.info(f"🧪 DEV MODE – Base Salary fixed at ${salary_base:,.0f}")

    # ---------------- SALARY TARGET (DEV) ----------------
    if "salary_target" not in st.session_state:
        st.session_state["salary_target"] = 1_000_000  # valor de prueba

    salary_target = st.session_state["salary_target"]
    st.info(f"🧪 DEV MODE – Target Salary fixed at ${salary_target:,.0f}")

else:
    with st.form("salary_form", clear_on_submit=False):

        # ---------------- SALARY BASE (PROD) ----------------
        salary_base_input = st.number_input(
            "Monthly Base Salary Input / SMLV",
            min_value=0,
            step=50_000,
            format="%d",
            help="Input the current legal minimum wage (SMLV) for calculations",
        )

        # ---------------- SALARY TARGET (PROD) ----------------
        salary_target_input = st.number_input(
            "Monthly Target Salary",
            min_value=0,
            step=50_000,
            format="%d",
            help="Input the target salary for payroll validations",
        )

        confirm = st.form_submit_button("Confirm Salaries")

    if confirm:
        if salary_base_input <= 0 or salary_target_input <= 0:
            st.error("❌ Please enter valid salaries greater than 0.")
            st.stop()

        st.session_state["salary_base"] = int(salary_base_input)
        st.session_state["salary_target"] = int(salary_target_input)

        st.success(
            f"✅ Salaries confirmed:"
            f"\n• Base Salary: ${salary_base_input:,.0f}"
            f"\n• Target Salary: ${salary_target_input:,.0f}"
        )

    # ---------------- VALIDACIONES ----------------
    if "salary_base" not in st.session_state or "salary_target" not in st.session_state:
        st.warning("Must confirm both Base Salary and Target Salary to proceed.")
        st.stop()

    salary_base = st.session_state["salary_base"]
    salary_target = st.session_state["salary_target"]

    st.info(
        f"Using Salaries:"
        f"\n• Base Salary: ${salary_base:,.0f}"
        f"\n• Target Salary: ${salary_target:,.0f}"
    )

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
    df_agrp = dfs["agrupaciones"]
    df_personalNacional = dfs["personal_nacional"]
    df_personalNacionalFunza = dfs["personal_funza"]
    df_cifrasMes = dfs["cifras_mes"]
    df_temp = dfs["temporales"]
    df_acumuladoAño = dfs["acumulado_año"]
    
    st.success("✅ DEV files loaded")

else:
    col1, col2 = st.columns(2)

    with col1:
        f_activos_retirados = st.file_uploader("Base Activos - Retirados Meli.xlsx", type=["xlsx"])
        f_conso_nomina = st.file_uploader("Conso_Nomina.xlsx", type=["xlsx"])
        f_acumulado = st.file_uploader("Acumulado_Mes.xlsx", type=["xlsx"])
        f_personal_nacional = st.file_uploader("Base Personal Nacional.xlsx", type=["xlsx"])
        f_temporales = st.file_uploader("Plantillas Facturacion y Nómina 2025 - Mercado libre.xlsx", type=["xlsx"])

    with col2:
        f_prenomina = st.file_uploader("Conso_PreNomina.xlsx", type=["xlsx"])
        f_agrupaciones = st.file_uploader("Agrupaciones.xlsx", type=["xlsx"])
        f_personal_nacionalFunza = st.file_uploader("Planta de personal DHL.xlsx", type=["xlsx"])
        f_cifras_mes = st.file_uploader("Cifras de cierre Meli.xlsx", type=["xlsx"])
        f_acumulado_año = st.file_uploader("Acumulado_Año.xlsx", type=["xlsx"])

    all_files_ok = all([
        f_activos_retirados,
        f_conso_nomina,
        f_prenomina,
        f_acumulado,
        f_agrupaciones,
        f_personal_nacional,
        f_personal_nacionalFunza,
        f_cifras_mes,
        f_temporales,
        f_acumulado_año,
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
        df_agrp = load_excel(f_agrupaciones, sheet="Agrupaciones", name="Agrupaciones")
        df_personalNacional = load_excel(f_personal_nacional, sheet="BD Personal DHL", name="Base Personal Nacional")
        df_personalNacionalFunza = load_excel(f_personal_nacionalFunza, sheet="RETIRADOS", name="Planta de personal DHL")
        df_cifrasMes = load_excel(f_cifras_mes, sheet="Base", name="Cifras de cierre Meli")
        df_temp = load_excel(f_temporales, name="Plantillas Facturacion y Nómina 2025 - Mercado libre")
        df_acumuladoAño = load_excel(f_acumulado_año, name="Acumulado_Año")

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
    check_columns(df_agrp, ["CONCEPTO", "DESCRIPCION", "AGRUPACION"], "Agrupaciones")
    check_columns(df_acumulado, ["NÓMINA", "PROCESO", "AÑO PROCESO", "PERIODO PROCESO", "MES PROCESO",
                                 "NUMERO DOCUMENTO", "PRIMER APELLIDO", "SEGUNDO APELLIDO", "NOMBRES",
                                 "CONCEPTO", "DESCRIPCIÓN", "CANTIDAD", "MONTO", "NETO", "SMRU"], "Acumulado_Mes")
    check_columns(df_personalNacionalFunza, ["CEDULA", "CARGO DHL", "FECHA INGRESO", "FECHA RETIRO"], "Planta de personal DHL")
    check_columns(df_cifrasMes, ["CEDULA", "NOMBRE", "CONCEPTO", "NOMBRE_CONCEPTO", "SALDO", "NETO", "SMRU", "MES"], "Cifras de cierre Meli")
    check_columns(df_temp, ["EMPRESA", "TIPO DE VINCULACIÓN", "MES"], "Plantillas Facturacion y Nómina 2025 - Mercado libre")
    check_columns(df_acumuladoAño, ["NÓMINA", "PROCESO", "AÑO PROCESO", "PERIODO PROCESO", "MES PROCESO",  "NUMERO DOCUMENTO"], "Acumulado_Año")

st.success("🚀 Files loaded and validated successfully. Ready for analysis.")
st.divider()

# Calculate Payroll Periods
periodos = calcular_periodos_nomina(df_acumulado)
st.write("📌 Periodos calculados:", periodos)

nMesActual = periodos["n_mes_actual"]
nMesAnterior = periodos["n_mes_anterior"]
nombreMesActual = periodos["nombre_mes_actual"]
nomMesAnterior = periodos["nombre_mes_anterior"]
nomMesIBC = periodos["nombre_mes_ibc"]
corteNomina1 = periodos["corte_nomina_1"]
corteNomina2 = periodos["corte_nomina_2"]

# Filter DataFrames by Periods
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

# Select Relevant Columns
df_activos = col.delete_columns(
    df_activos,
    columns=[
        col for col in df_activos.columns
        if col not in ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "SALARIO MENSUAL"]
    ]
)

df_retirados = col.delete_columns(
    df_retirados,
    columns=[
        col for col in df_retirados.columns
        if col not in ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA"]
    ]
)

df_consoNomina = col.delete_columns(
    df_conso_nomina,
    columns=[
        col for col in df_conso_nomina.columns
        if col not in ["CEDULA", "CARGO NOMINA", "SALARIO BASICO"]
    ]
)

df_preNomina = col.delete_columns(
    df_prenomina,
    columns=[
        col for col in df_prenomina.columns
        if col not in ["Cedula", "Basico"]
    ]
)

df_personalNacional = col.delete_columns(
    df_personalNacional,
    columns=[
        col for col in df_personalNacional.columns
        if col not in ["OPERACION","ID", "CARGO NÓMINA", "FECHA DE INGRESO", "FECHA DE RETIRO"]
    ]
)

# Insert New Columns
df_activos = col.new_column(df_activos, "FECHA DE BAJA", "1990-01-01 00:00:00")
df_personalNacionalFunza = col.new_column(df_personalNacionalFunza, "OPERACION", "Funza") 

# Select Relevant Columns
df_personalNacionalFunza = col.delete_columns(
    df_personalNacionalFunza,
    columns=[
        col for col in df_personalNacionalFunza.columns
        if col not in ["OPERACION", "CEDULA", "CARGO DHL", "FECHA INGRESO", "FECHA RETIRO"]
    ]
)

#--------------- CONSOLIDAR DATA DE EMPLEADOS ACTIVOS RETIRADOS ---------------
# Consolidate DataFrames
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

# Delete Column
df_retirados = col.delete_columns(df_retirados, columns=["CARGO NOMINA"])

# Delete Duplicates
df_retirados = col.delete_duplicate_rows(df_retirados, column_name="CEDULA", keep="first")

# Insert New Columns with Condition
df_retirados = col.new_column_with_condition(
    df_retirados,
    column_name="SALARIO MENSUAL",
    condition=df_retirados["SALARIO BASICO"] != "",
    value_if_true=df_retirados["SALARIO BASICO"],
    value_if_false=df_retirados["Basico"]
)

# Update Columns
df_retirados = col.update_column(
    df_retirados,
    column_name="SALARIO MENSUAL",
    condition=df_retirados["SALARIO BASICO"].isna(),
    new_value=df_retirados["Basico"]
)

# Delete Column
df_retirados = col.delete_columns(df_retirados, columns=["SALARIO BASICO", "Basico","Cedula"])

# Select Relevant Columns
df_activos = col.delete_columns(
    df_activos,
    columns=[
        col for col in df_activos.columns
        if col not in ["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE INGRESO", "FECHA DE BAJA", "SALARIO MENSUAL"]
    ]
)

# Concat DataFrames
df_activos = concat_dataframes(df_activos, df_retirados, axis=0)

# -------------- UNIR BASES NACIONAL AMERICAS Y FUNZA  ---------------
# Rename Columns
df_personalNacionalFunza = col.rename_columns(df_personalNacionalFunza, columns_mapping={
    "CEDULA": "ID",
    "CARGO DHL": "CARGO NÓMINA",
    "FECHA INGRESO": "FECHA DE INGRESO",
    "FECHA RETIRO": "FECHA DE RETIRO"
})

# Delete Duplicates
df_personalNacional = col.delete_duplicate_rows(df_personalNacional, column_name="ID", keep="last")
df_personalNacionalFunza = col.delete_duplicate_rows(df_personalNacionalFunza, column_name="ID", keep="last")

# Concat DataFrames
df_personalNacional = concat_dataframes(df_personalNacional, df_personalNacionalFunza, axis=0)

# --------------- ELIMINAR DUPLICADOS DE BASE NACIONAL Y RETIRADOS -----------
# Delete Duplicates
df_personalNacionalRetirados = col.filter_and_drop_duplicates(df_personalNacional, filter_column="FECHA DE RETIRO",
                                                filter_value="1990-01-01 00:00:00",operator="!=", duplicate_column="ID",
                                                keep="last")

# Order Columns
df_personalNacionalRetirados = col.order_columns(df_personalNacionalRetirados, column_name="FECHA DE RETIRO", ascending=True)
df_personalNacional = col.order_columns(df_personalNacional, column_name="FECHA DE RETIRO", ascending=True)

# Delete Duplicates
df_personalNacional = col.delete_duplicate_rows(df_personalNacional, column_name="ID", keep="last")
df_personalNacionalRetirados = col.delete_duplicate_rows(df_personalNacionalRetirados, column_name="ID", keep="last")

#--------------- VERIFICAR CARGO FECHAS DE INGRESO Y RETIRO DE EMPLEADOS ---------------
# Merge DataFrames
df_activos = merge_dataframes(
    df_left=df_activos,
    df_right=df_personalNacionalRetirados,
    left_key="CEDULA",
    right_key="ID",
    how="left",
    merge_name="Activos vs Personal Nacional"
)

# Delete Columns
df_activos = col.delete_columns(df_activos, columns=["CARGO NÓMINA", "OPERACION", "CARGO MELI"])

# Change Register in Column
df_activos = col.modify_register(df_activos, column_name="NOMBRE DEL PUESTO", condition=".", position=1)

# Change Register to DateTime
df_activos = col.change_to_datetime(df_activos, column_name="FECHA DE INGRESO_x")
df_activos = col.change_to_datetime(df_activos, column_name="FECHA DE INGRESO_y")

# Update Column with Condition
fecha_vacia = "1990-01-01 00:00:00"

df_activos = col.update_column(df_activos,column_name="FECHA DE BAJA",
    condition=df_activos["FECHA DE BAJA"].isna() | (df_activos["FECHA DE BAJA"] == fecha_vacia),
    new_value=df_activos["FECHA DE RETIRO"]
)

df_activos = col.update_column(df_activos,column_name="FECHA DE INGRESO_x",
    condition=df_activos["FECHA DE INGRESO_x"].isna() | (df_activos["FECHA DE INGRESO_x"] == fecha_vacia),
    new_value=df_activos["FECHA DE INGRESO_y"]
)

# Delete Columns
df_activos = col.delete_columns(df_activos, columns=["FECHA DE INGRESO_y", "ID", "FECHA DE RETIRO"])

# Rename Columns
df_activos = col.rename_columns(df_activos, columns_mapping={"FECHA DE INGRESO_x": "FECHA DE INGRESO"})

#-------------------- CHECK FILE ACUMULADO MES --------------------
# Merge DataFrames
df_acumulado = merge_dataframes(
    df_left=df_acumulado,
    df_right=df_activos,
    left_key="Numero Documento",
    right_key="CEDULA",
    how="left",
    merge_name="Acumulado vs Base Activos"
)

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado,["CEDULA", "NOMBRE DEL PUESTO", "FECHA DE BAJA", "FECHA DE INGRESO"])

# Codes Payroll
codigos_general = [
    "D144", "D169", "D196",
    "P003", "P129", "P140", "P153",
    "P211", "P216", "P243", "P275", "P331", "P115", "P210",
    "D232", "P176"
]

codigos_ft = ["P138", "P142", "P144", "P358"]

# Check Quantity with Salary
df_acumulado = check_quantity_with_salary(
    df=df_acumulado,
    salario_umbral_ft=salary_base,#Var Salary Base,
    codigos_general=codigos_general,
    codigos_ft=codigos_ft,
    dias_mes=30,
    salario_col="SALARIO MENSUAL",
    neto_col="Neto",
    cantidad_col="Cantidad",
    concepto_col="Concepto"
)

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado,["SALARIO MENSUAL", "Salario Dia", "Verificacion Dias Salario"])

# Export Excel
df_acumulado.to_excel("Acumulado_Mes_Verificado.xlsx", index=False)

#-------------------- CHECK FILE CIERRE MELI O INTERFAZ --------------------
# Update Total Dias = Cantidad, but if Concepto contains D196 or D144 then Total Dias = Cantidad * -1 
df_acumulado["Total Dias"] = df_acumulado["Cantidad"]

mask_d196 = df_acumulado["Concepto"].astype(str).str.contains("D196", na=False)
mask_d144 = df_acumulado["Concepto"].astype(str).str.contains("D144", na=False)
df_acumulado.loc[mask_d196 | mask_d144, "Total Dias"] = df_acumulado.loc[mask_d196 | mask_d144, "Cantidad"] * -1

# Change to Uppercase Columns
df_acumulado = col.uppercase_columns(df_acumulado)

# Concat Name and Last Name
df_acumulado = col.concat_full_name(
    df_acumulado,
    first_name_col="NOMBRES",
    last_name_1_col="PRIMER APELLIDO",
    last_name_2_col="SEGUNDO APELLIDO",
    target_col="NOMBRE COMPLETO"
)

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado,["PRIMER APELLIDO", "SEGUNDO APELLIDO", "NOMBRES","NÓMINA", "PROCESO",
                                            "PERIODO PROCESO", "NÚMERO EMPLEADO","AÑO PROCESO", "CANTIDAD"])

# Delete Rows
df_cifrasMes = filter_by_operator(df_cifrasMes, column="COMPROBANTE", value="NELECT  ", operator="!=")

# Rename Columns
df_cifrasMes = col.rename_columns(df_cifrasMes, {
    "CEDULA": "NUMERO DOCUMENTO",
    "NOMBRE": "NOMBRE COMPLETO",
    "NOMBRE_CONCEPTO": "DESCRIPCIÓN",
    "NETO": "MONTO",
    "MES": "MES PROCESO"
})

# Insert New Columns
df_cifrasMes["CANTIDAD"] = 0
df_cifrasMes["NETO"] = df_cifrasMes["MONTO"]
df_cifrasMes["TOTAL DIAS"] = 0

# Filter by Prefix in Column
df_cifrasMes = filter_by_prefix(df_cifrasMes, column="CUENTA", prefix="4", keep_matches=True)

# Select Relevant Columns
orden_columnas = [
    "MES PROCESO", "NUMERO DOCUMENTO", "CONCEPTO", "DESCRIPCIÓN",
    "CANTIDAD", "MONTO", "NETO", "SMRU", "TOTAL DIAS", "NOMBRE COMPLETO"
]
df_cifrasMes = col.select_columns(df_cifrasMes, orden_columnas)

# Consolidate DataFrames
df_acumulado = concat_dataframes(df_acumulado, df_cifrasMes, axis=0)

# Delete Duplicates
df_activos = col.delete_duplicate_rows(df_activos, column_name="CEDULA", keep="first")

# ------------------ MERGE ACUMULADO VS ACTIVOS ------------------
# Merge DataFrames
df_acumulado = merge_dataframes(
    df_left=df_acumulado,
    df_right=df_activos,
    left_key="NUMERO DOCUMENTO",
    right_key="CEDULA",
    how="left",
    merge_name="Acumulado vs Base Activos"
)

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado, ["CEDULA"])

# ------------------ MERGE ACUMULADO VS PERSONAL NACIONAL ------------------
df_acumulado = merge_dataframes(
    df_left=df_acumulado,
    df_right=df_personalNacional,
    left_key="NUMERO DOCUMENTO",
    right_key="ID",
    how="left",
    merge_name="Acumulado vs Base Personal Nacional"
)

# Change to DateTime
df_acumulado = col.change_to_datetime(df_acumulado, "FECHA DE BAJA")
df_acumulado = col.change_to_datetime(df_acumulado, "FECHA DE RETIRO")

# Fill Missing Values
df_acumulado["NOMBRE DEL PUESTO"] = df_acumulado["NOMBRE DEL PUESTO"].fillna(df_acumulado["CARGO NÓMINA"])
df_acumulado["FECHA DE INGRESO_x"] = df_acumulado["FECHA DE INGRESO_x"].fillna(df_acumulado["FECHA DE INGRESO_y"])
df_acumulado["FECHA DE BAJA"] = df_acumulado["FECHA DE BAJA"].fillna(df_acumulado["FECHA DE RETIRO"])

# Delete Columns
df_acumulado = col.delete_columns(
    df_acumulado,
    ["CARGO NÓMINA", "ID", "FECHA DE INGRESO_y", "FECHA DE RETIRO", "OPERACION"]
)

# Rename Columns
df_acumulado = col.rename_columns(df_acumulado, {"FECHA DE INGRESO_x": "FECHA DE INGRESO"})

# ------------------------- CREAR COLUMNAS EN NOMINA ----------------------
# Mapping SMRU -> Values
SMRU_TO_CC = {
    "COL - MERCADO LIBRE - Funza Zol - WHS.": "6563",
    "COL - MERCADO LIBRE - Btá Americas - WHS": "6571",
    "COL - MERCADO LIBRE - Cortijo 9 - WHS.": "1980",
    "COL - MERCADO LIBRE - Medellin Olaya - WHS.": "6567",
    "COL - MERCADO LIBRE - Giron In House - WHS.": "5641",
    "COL - MERCADO LIBRE - Pereira In House - WHS.": "5358",
    "COL - MERCADO LIBRE - Tunja In House - WHS.": "5359",
    "COL - MERCADO LIBRE - Ibague In House - WHS.": "5840",
    "COL - MERCADO LIBRE - Estrella  In House - WHS": "5421",
    "COL - MERCADO LIBRE -Funza Zol -WHS": "1111",
}

SMRU_TO_NOMBRE_CC = {
    "COL - MERCADO LIBRE - Funza Zol - WHS.": "FUNZA ZOL",
    "COL - MERCADO LIBRE - Btá Americas - WHS": "BTA AMERICAS",
    "COL - MERCADO LIBRE - Cortijo 9 - WHS.": "CORTIJO 9",
    "COL - MERCADO LIBRE - Medellin Olaya - WHS.": "MEDELLIN OLAYA",
    "COL - MERCADO LIBRE - Giron In House - WHS.": "GIRON IN HOUSE",
    "COL - MERCADO LIBRE - Pereira In House - WHS.": "PEREIRA IN HOUSE",
    "COL - MERCADO LIBRE - Tunja In House - WHS.": "TUNJA IN HOUSE",
    "COL - MERCADO LIBRE - Ibague In House - WHS.": "IBAGUE IN HOUSE",
    "COL - MERCADO LIBRE - Estrella  In House - WHS": "Estrella  In House",
    "COL - MERCADO LIBRE -Funza Zol -WHS": "SVC FUNZA",
}

SMRU_TO_POBLACION = {
    "COL - MERCADO LIBRE - Funza Zol - WHS.": "FUNZA",
    "COL - MERCADO LIBRE - Btá Americas - WHS": "BOGOTA",
    "COL - MERCADO LIBRE - Cortijo 9 - WHS.": "YUMBO",
    "COL - MERCADO LIBRE - Medellin Olaya - WHS.": "MEDELLIN",
    "COL - MERCADO LIBRE - Giron In House - WHS.": "GIRON",
    "COL - MERCADO LIBRE - Pereira In House - WHS.": "PEREIRA",
    "COL - MERCADO LIBRE - Tunja In House - WHS.": "TUNJA",
    "COL - MERCADO LIBRE - Ibague In House - WHS.": "IBAGUE",
    "COL - MERCADO LIBRE - Estrella  In House - WHS": "MEDELLIN",
    "COL - MERCADO LIBRE -Funza Zol -WHS": "SVC FUNZA",
}

# Create new columns based on mapping from SMRU
df_acumulado = col.map_column_values(
    df_acumulado,
    source_col="SMRU",
    target_col="CENTRO DE COSTOS",
    mapping=SMRU_TO_CC,
    default="N/A"
)

df_acumulado = col.map_column_values(
    df_acumulado,
    source_col="SMRU",
    target_col="NOMBRE CENTRO DE COSTOS",
    mapping=SMRU_TO_NOMBRE_CC,
    default="N/A"
)

df_acumulado = col.map_column_values(
    df_acumulado,
    source_col="SMRU",
    target_col="POBLACIÓN",
    mapping=SMRU_TO_POBLACION,
    default="N/A"
)

# Create "CARGO NOMINA" column based on "NOMBRE DEL PUESTO"
df_acumulado["CARGO NOMINA"] = df_acumulado["NOMBRE DEL PUESTO"]

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado, ["NOMBRE DEL PUESTO"])

# ------------------ MERGE NOMINA WITH AGRUPACIONES ------------------ 
df_acumulado = merge_dataframes(
    df_left=df_acumulado,
    df_right=df_agrp,
    left_key="CONCEPTO",
    right_key="CONCEPTO",
    how="left",
    merge_name="Acumulado vs Base Agrupaciones"
)

# Delete Rows where AGRUPACION is "NO APLICA"
df_acumulado = filter_by_operator(df_acumulado, column="AGRUPACION", value="NO APLICA", operator="!=")

# Update to Negative Values in "TOTAL" Column if "CONCEPTO" starts with "D" and keep original "MONTO" value if not
df_acumulado = col.update_column_by_prefix(
    df_acumulado,
    source_col="CONCEPTO",
    value_col="MONTO",
    target_col="TOTAL",
    prefix="D",
    multiplier_if_match=-1,
    default_from_value_col=True
)

# --------------- FUNCTION TO CREATE NEW COLUMNS WITH SUM OF "CANTIDAD" FOR SPECIFIC "DESCRIPCIÓN" VALUES ---------------
# Update "DESCRIPCIÓN" value to "AJUS SALARIO" if "CONCEPTO" is "P176"
condicion = df_acumulado["CONCEPTO"] == "P176"
df_acumulado = col.update_column(df_acumulado,column_name="DESCRIPCION",condition=condicion,new_value="AJUS SALARIO")

# Dictionary mapping from "DESCRIPCIÓN" values to new column names
dic_days_for_descripcion = {
    "SUELDO BASICO": "DIAS_SUELDO_BASICO",
    "DÍA FAMILIAR": "DIAS_FAMILIAR",
    "SANCION / SUSPENSION": "DIAS_SANCION_/_SUSPENSION",
    "LICENCIA NO REMUN": "DIAS_LICENCIA_NO_REMUN",
    "INASISTENCIA INJUST": "DIAS_INASISTENCIA_INJUST",
    "VACACIONES": "DIAS_VACACIONES",
    "VACACIONES FESTIVAS": "DIAS_VACACIONES_FESTIVAS",
    "VACACIONES EN DINERO": "DIAS_VACACIONES_DINERO",
    "GASTO INCAPACIDAD": "DIAS_GASTO_INCAPACIDAD",
    "LIC LEY MARIA 8 DIAS": "DIAS_LIC_LEY_MARIA_8_DIAS",
    "INCAPACIDAD ACC TRAB": "DIAS_INCAPACIDAD_ACC_TRAB",
    "INCAP ENFERMEDAD GEN": "DIAS_INCAP_ENFERMEDAD_GEN",
    "LICENCIA MATERNIDAD": "DIAS_LICENCIA_MATERNIDAD",
    "VAC HABILES SAL INT": "DIAS_VAC_HABILES_SAL_INT",
    "INCAPACIDAD AL 50%": "DIAS_INCAPACIDAD_AL_50%",
    "DÍA NO LAB DER A PAG": "DIAS_DÍA_NO_LAB_DER_A_PAG",
    "RTEGRO DTO INASISTEN": "DIAS_RTEGRO_DTO_INASISTEN",
    "AJS  LICENCIA MATERN": "DIAS_AJS_LICENCIA_MATERN",
    "INCAP ENF GEN PRORR": "DIAS_INCAP_ENF_GEN_PRORR",
    "DTO SALARIO": "DIAS_DTO_SALARIO",
    "INASIS X INC > 180 D": "DIAS_INASIS_X_INC_>_180_D",
    "DTO INC ENF GRAL AL": "DIAS_DTO_INC_ENF_GRAL_AL",
    "PERMISO JUSTIFICADO": "DIAS_PERMISO_JUSTIFICADO",
    "RETROACTIV SALARIO": "DIAS_RETROACTIV_SALARIO",
    "PERMISO PERSONAL": "DIAS_PERMISO_PERSONAL",
    "AJUS SALARIO": "DIAS_AJUS_SALARIO"
}

# Execute function to create new columns with sum of "CANTIDAD" for specific "DESCRIPCIÓN" values based on the dictionary
df_acumulado = calculate_for_concept(
    df=df_acumulado,
    diccionario=dic_days_for_descripcion,
    columna_filtro="DESCRIPCION",
    columna_valor="TOTAL DIAS",
    group_col="NUMERO DOCUMENTO",
    asignar_primera_fila=True
)

# --------------- FUNCTION TO CREATE NEW COLUMNS WITH SUM OF "AGRUPACIONES" VALUES ---------------
# Update "AGRUPACION" without spaces
df_acumulado = col.strip_column(df_acumulado, column_name="AGRUPACION")

# Dictionary mapping from "AGRUPACION" values to new column names
dic_values_for_agrupacion = {
    "SALARIO A PAGAR": "SALARIO_A_PAGAR",
    "SUBSIDIO DE TRANSPORTE": "SUBSIDIO_TRANSPORTE",
    "HE DIURNA - 1.25": "VR._HORA_EXTRA_DIURNA - 1,25",
    "HE NOCTURNA - 1.75": "VR._HORA_EXTRA_NOCTURNA - 1,75",
    "HRS. EXTRA HORA DOM/FEST. NOCTURNA 2.50%": "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%": "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "HRS. DOMINICAL DIURNO - 1,75": "VR._DOMINICAL_DIURNO - 1,75",
    "FESTIVO DIURNO  1.75": "VR._FESTIVO_DIURNO - 1,75",
    "RECAR DOM NOCT - 2.1": "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
    "RECARGO FESTIVO NOCTURNO - 2,1": "VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "RECARGO NOCT - 0.35": "VR._RECARGO_NOCTURNO - 0,35",
    "REAJUSTE RECARGOS": "REAJUSTE_RECARGOS",
    "REAJUSTE H.E": "REAJUSTE_H.E",
    "REAJUSTE SALARIAL": "REAJUSTE_SALARIAL",
    "REAJUSTE AUSENCIAS JUSTIFICADAS": "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
    "REAJUSTE VACACIONES": "REAJUSTE_VACACIONES",
    "DIAS AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)": "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
    "BONIFICACION NO CONSTITUTIVA DE SALARIO": "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
    "BONIFICACION SALARIAL": "BONIFICACION_SALARIAL",
    "TRANSPORTE EXTRALEGAL AUT. POR CL": "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
    "AUXILIO DE RODAMIENTO": "AUXILIO_DE_RODAMIENTO",
    "MAY. VALOR PAGADO EN SALARIO": "MAY._VALOR_PAGADO_EN_SALARIO",
    "MAY. VALOR PAGADO EN AUX. TRANS": "MAY._VALOR_PAGADO_EN_AUX._TRANS",
    "BENEFICIOS": "BENEFICIOS",
    "VACACIONES": "VACACIONES",
    "OTROS CONCEPTOS FACTURABLES PRESTACIONALES": "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
    "SALUD": "SALUD_PATRONO",
    "PENSION": "PENSION_12%",
    "ARL": "ARP",
    "CAJA": "CAJA_DE_COMP_4%",
    "SENA": "SENA",
    "ICBF": "ICBF",
    "PROV. CESANTIAS": "CESANTIAS_8.33%",
    "PROV. INT CESANT": "INT._CESANTIAS_1%",
    "PRO_PRIMA": "PRIMA_8.33%",
    "PROV. VACACIONES": "VACACIONES_4.34%",
    "PROV. BONO ANUAL": "BONIFICACION_DIRECTIVO",
    "PROV. PRIMA EXTRALEGAL": "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
}

# Execute function to create new columns with sum of "TOTAL" for specific "AGRUPACION" values based on the dictionary
df_acumulado = calculate_for_concept(
    df=df_acumulado,
    diccionario=dic_values_for_agrupacion,
    columna_filtro="AGRUPACION",
    columna_valor="TOTAL",
    group_col="NUMERO DOCUMENTO",
    asignar_primera_fila=True
)

# --------------- CREATE NEW COLUMN WITH SUM OF "TOTAL DIAS" FOR SPECIFIC "AGRUPACION" VALUES ---------------
# dictionary mapping from "AGRUPACION" values to new column names for days of payroll
dic_days_pay = {"SALARIO A PAGAR": "DIAS_PAGO_NOMINA"}

# Execute function to create new column with sum of "TOTAL DIAS" for "AGRUPACION" value "SALARIO A PAGAR"
df_acumulado = calculate_for_concept(
    df=df_acumulado,
    diccionario=dic_days_pay,
    columna_filtro="AGRUPACION",
    columna_valor="TOTAL DIAS",
    group_col="NUMERO DOCUMENTO",
    asignar_primera_fila=True
)

# --------------- CREATE NEW COLUMNS WITH SUM OF "CANTIDAD" FOR SPECIFIC "AGRUPACION" VALUES --------------
# Dictionary mapping from "AGRUPACION" values to new column names for quantity of hours
dic_quantity_hours = {
    "HE DIURNA - 1.25    ": "HRS_HORA_EXTRA_DIURNA - 1,25",
    "HE NOCTURNA - 1.75  ": "HRS._HORA_EXTRA_NOCTURNA - 1,75",
    "HRS. EXTRA HORA DOM/FEST. NOCTURNA 2.50%": "HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%": "HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "HRS. DOMINICAL DIURNO - 1,75": "HRS._DOMINICAL_DIURNO - 1,75",
    "FESTIVO DIURNO  1.75": "HRS._FESTIVO_DIURNO - 1,75",
    "RECAR DOM NOCT - 2.1": "HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
    "RECARGO FESTIVO NOCTURNO - 2,1": "HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "RECARGO NOCT - 0.35 ": "HRS_RECARGO_NOCTURNO - 0,35",
    "DIAS AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)": "DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
}

# Execute function to create new columns with sum of "CANTIDAD" for specific "AGRUPACION" values based on the dictionary
df_acumulado = calculate_for_concept(
    df=df_acumulado,
    diccionario=dic_quantity_hours,
    columna_filtro="AGRUPACION",
    columna_valor="CANTIDAD",
    group_col="NUMERO DOCUMENTO",
    asignar_primera_fila=True
)

# --------------- CREATE COLUMNS WITH SUM OF SPECIFIC COLUMNS ---------------
# Dictionary mapping from new column names to list of columns to sum
dict_totales = {
    "TOTAL # H.E.": [
        "HRS_HORA_EXTRA_DIURNA - 1,25",
        "HRS._HORA_EXTRA_NOCTURNA - 1,75",
        "HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
        "HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%"
    ],
    "TOTAL_HORAS_EXTRAS_SIN_R.N.": [
        "VR._HORA_EXTRA_DIURNA - 1,25",
        "VR._HORA_EXTRA_NOCTURNA - 1,75",
        "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
        "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%"
    ],
    "TOTAL NO. RECARGOS": [
        "HRS._DOMINICAL_DIURNO - 1,75",
        "HRS._FESTIVO_DIURNO - 1,75",
        "HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
        "HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
        "HRS_RECARGO_NOCTURNO - 0,35"
    ],
    "TOTAL_$_RECARGOS": [
        "VR._DOMINICAL_DIURNO - 1,75",
        "VR._FESTIVO_DIURNO - 1,75",
        "VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
        "VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
        "VR._RECARGO_NOCTURNO - 0,35"
    ],
    "TOTAL_S.S.": [
        "SALUD_PATRONO",
        "PENSION_12%",
        "ARP"
    ],
    "VALOR_PARAFISCALES": [
        "CAJA_DE_COMP_4%",
        "SENA",
        "ICBF"
    ],
    "VALOR_PRESTACIONES": [
        "CESANTIAS_8.33%",
        "INT._CESANTIAS_1%",
        "PRIMA_8.33%",
        "VACACIONES_4.34%"
    ],
    "TOTAL_NOMINA_S.S.PARAFI_PRESTA": [
        "SALARIO_A_PAGAR",
        "SUBSIDIO_TRANSPORTE",
        "TOTAL_HORAS_EXTRAS_SIN_R.N.",
        "TOTAL_$_RECARGOS",
        "REAJUSTE_RECARGOS",
        "REAJUSTE_H.E",
        "REAJUSTE_SALARIAL",
        "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
        "REAJUSTE_VACACIONES",
        "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
        "BONIFICACION_SALARIAL",
        "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
        "AUXILIO_DE_RODAMIENTO",
        "MAY._VALOR_PAGADO_EN_SALARIO",
        "BENEFICIOS",
        "EXAMENES_MEDICOS_SERVICIOS",
        "VACACIONES",
        "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
        "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
        "TOTAL_S.S.",
        "VALOR_PARAFISCALES",
        "VALOR_PRESTACIONES"
    ],
    "SUBTOTAL FACTURA": [
        "SALARIO_A_PAGAR",
        "SUBSIDIO_TRANSPORTE",
        "TOTAL_HORAS_EXTRAS_SIN_R.N.",
        "TOTAL_$_RECARGOS",
        "REAJUSTE_RECARGOS",
        "REAJUSTE_H.E",
        "REAJUSTE_SALARIAL",
        "REAJUSTE_AUSENCIAS_JUSTIFICADAS",
        "REAJUSTE_VACACIONES",
        "BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
        "BONIFICACION_SALARIAL",
        "TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
        "AUXILIO_DE_RODAMIENTO",
        "MAY._VALOR_PAGADO_EN_SALARIO",
        "BENEFICIOS",
        "EXAMENES_MEDICOS_SERVICIOS",
        "VACACIONES",
        "OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
        "CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
        "TOTAL_S.S.",
        "VALOR_PARAFISCALES",
        "VALOR_PRESTACIONES",
        "MAY._VALOR_PAGADO_EN_AUX._TRANS",
        "IMPREVISTOS",
        "ADMINISTRACION",
        "BONIFICACION_DIRECTIVO"
    ]
}

# Execute function to create new columns with sum of specific columns based on the dictionary
df_acumulado = col.create_column_total_from_dict(df_acumulado, dict_totales)

# --------------- CREATE COLUMNS WITH 0 ---------------
# Init columns with 0
list_columns = [
    "IMPREVISTOS",
    "EXAMENES_MEDICOS_SERVICIOS",
    "MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO",
    "ADMINISTRACION",
    "CARGO_MELI",
    "TIPO_DE_DOTACION",
    "TIPO_DE_CARGO",
    "NO.HORA_ORD_DOMINICAL_175",
    "VR.HORA_ORD_DOMINICAL_175",
    "HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%"
]

df_acumulado = col.init_columns(df_acumulado, list_columns, 0)

# Columns with constant values
df_acumulado = col.set_constant_columns(df_acumulado, {
    "EMPRESA": "SUPPLA S.A",
    "TIPO_DE_VINCULACIÓN": "DIRECTO"
})

# Rename Column
df_acumulado = col.rename_columns(df_acumulado, {"MES PROCESO": "MES"})


# --------------- COMPARATIVO DE NOMINA Y INTERFAZ ---------------
# Crear tablas resumen (equivalente a pivot_table sum)
df_summ_cifrasMes = pivot_sum(
    df=df_cifrasMes.copy(),
    index_cols=["NUMERO DOCUMENTO", "NOMBRE COMPLETO", "CONCEPTO"],
    value_col="NETO",
    output_col="NETO"
)

df_summ_acumulado = pivot_sum(
    df=df_acumulado,
    index_cols=["NUMERO DOCUMENTO", "NOMBRE COMPLETO", "CONCEPTO"],
    value_col="NETO",
    output_col="NETO"
)

# Change data type to string for merge keys
df_summ_cifrasMes["NUMERO DOCUMENTO"] = df_summ_cifrasMes["NUMERO DOCUMENTO"].astype(str)
df_summ_acumulado["NUMERO DOCUMENTO"] = df_summ_acumulado["NUMERO DOCUMENTO"].astype(str)

# Create "LLAVE" column for merging (concatenate "NUMERO DOCUMENTO" and "CONCEPTO")
df_summ_cifrasMes["LLAVE"] = df_summ_cifrasMes["NUMERO DOCUMENTO"] + df_summ_cifrasMes["CONCEPTO"].astype(str)
df_summ_acumulado["LLAVE"] = df_summ_acumulado["NUMERO DOCUMENTO"] + df_summ_acumulado["CONCEPTO"].astype(str)

# Merge Summ Acumulado vs Summ Cifras Mes
df_summ_acumulado = merge_dataframes(
    df_left=df_summ_acumulado,
    df_right=df_summ_cifrasMes,
    left_key="LLAVE",
    right_key="LLAVE",
    how="left",
    merge_name="Summ Acumulado vs Summ Cifras Mes"
)

# Delete Columns
df_summ_acumulado = col.delete_columns(
    df_summ_acumulado,
    ["NUMERO DOCUMENTO_y", "NOMBRE COMPLETO_y", "CONCEPTO_y", "LLAVE"]
)

# Rename Columns
df_summ_acumulado = col.rename_columns(df_summ_acumulado, {
    "NUMERO DOCUMENTO_x": "NUMERO DOCUMENTO",
    "NOMBRE COMPLETO_x": "NOMBRE COMPLETO",
    "CONCEPTO_x": "CONCEPTO",
    "NETO_x": "VALOR NOMINA",
    "NETO_y": "VALOR INTERFAZ",
})

# Fill missing values in "VALOR INTERFAZ" with 0
df_summ_acumulado["VALOR INTERFAZ"] = df_summ_acumulado["VALOR INTERFAZ"].fillna(0)

# Create "DIFERENCIA CONCEPTO" column with the difference between "VALOR NOMINA" and "VALOR INTERFAZ"
df_summ_acumulado["DIFERENCIA CONCEPTO"] = (df_summ_acumulado["VALOR NOMINA"] - df_summ_acumulado["VALOR INTERFAZ"])

# Sort for each "NUMERO DOCUMENTO"
df_summ_acumulado = df_summ_acumulado.sort_values(by=["NUMERO DOCUMENTO"])

# Create "TOTAL NOMINA" column with the total "VALOR NOMINA" for each "NUMERO DOCUMENTO" and assign it to the first row of each group, filling other rows with 0
df_summ_acumulado = total_by_group_first_row(
    df=df_summ_acumulado,
    group_col="NUMERO DOCUMENTO",
    value_col="VALOR NOMINA",
    target_col="TOTAL NOMINA",
    fill_other_rows=0
)

# Create "TOTAL INTERFAZ" column with the total "VALOR INTERFAZ" for each "NUMERO DOCUMENTO" and assign it to the first row of each group, filling other rows with 0
df_summ_acumulado = total_by_group_first_row(
    df=df_summ_acumulado,
    group_col="NUMERO DOCUMENTO",
    value_col="VALOR INTERFAZ",
    target_col="TOTAL INTERFAZ",
    fill_other_rows=0
)

# Create "DIFERENCIA TOTAL" column with the difference between "TOTAL NOMINA" and "TOTAL INTERFAZ"
df_summ_acumulado["DIFERENCIA TOTAL"] = (df_summ_acumulado["TOTAL NOMINA"] - df_summ_acumulado["TOTAL INTERFAZ"])

# --------------- SORT COLUMNS ---------------
# Define desired column order
list_sort = ["EMPRESA", "TIPO_DE_VINCULACIÓN", "MES","CENTRO DE COSTOS", "NOMBRE CENTRO DE COSTOS",
             "POBLACIÓN", "NUMERO DOCUMENTO","NOMBRE COMPLETO","CARGO NOMINA","TIPO_DE_DOTACION","TIPO_DE_CARGO",
             "FECHA DE INGRESO","FECHA DE BAJA","SALARIO MENSUAL","DIAS_PAGO_NOMINA","SALARIO_A_PAGAR","SUBSIDIO_TRANSPORTE",
             "HRS_HORA_EXTRA_DIURNA - 1,25","VR._HORA_EXTRA_DIURNA - 1,25","HRS._HORA_EXTRA_NOCTURNA - 1,75","VR._HORA_EXTRA_NOCTURNA - 1,75",
             "NO.HORA_ORD_DOMINICAL_175","VR.HORA_ORD_DOMINICAL_175","HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
             "VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%","HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
             "VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%","TOTAL # H.E.","TOTAL_HORAS_EXTRAS_SIN_R.N.",
             "HRS._DOMINICAL_DIURNO - 1,75","VR._DOMINICAL_DIURNO - 1,75","HRS._FESTIVO_DIURNO - 1,75","VR._FESTIVO_DIURNO - 1,75",
             "HRS. RECARGO DOMINICAL NOCTURNO - 2,1","VR._RECARGO_DOMINICAL_NOCTURNO - 2,1","HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
             "VR._RECARGO_FESTIVO_NOCTURNO - 2,1","HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
             "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%","HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
             "VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%","HRS_RECARGO_NOCTURNO - 0,35","VR._RECARGO_NOCTURNO - 0,35",
             "TOTAL NO. RECARGOS","TOTAL_$_RECARGOS","REAJUSTE_RECARGOS","REAJUSTE_H.E","REAJUSTE_SALARIAL","REAJUSTE_AUSENCIAS_JUSTIFICADAS",
             "REAJUSTE_VACACIONES","DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
             "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)","BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
             "BONIFICACION_SALARIAL","TRANSPORTE_EXTRALEGAL_AUT._POR_CL","AUXILIO_DE_RODAMIENTO","MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO",
             "MAY._VALOR_PAGADO_EN_SALARIO","MAY._VALOR_PAGADO_EN_AUX._TRANS","BENEFICIOS","EXAMENES_MEDICOS_SERVICIOS",
             "VACACIONES","OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES","CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
             "SALUD_PATRONO","PENSION_12%","ARP","TOTAL_S.S.","CAJA_DE_COMP_4%","SENA","ICBF","VALOR_PARAFISCALES","CESANTIAS_8.33%",
             "INT._CESANTIAS_1%","PRIMA_8.33%","VACACIONES_4.34%","IMPREVISTOS","VALOR_PRESTACIONES","TOTAL_NOMINA_S.S.PARAFI_PRESTA",
             "ADMINISTRACION","BONIFICACION_DIRECTIVO","SUBTOTAL FACTURA","DIAS_SUELDO_BASICO","DIAS_FAMILIAR","DIAS_PERMISO_JUSTIFICADO",
             "DIAS_SANCION_/_SUSPENSION","DIAS_LICENCIA_NO_REMUN","DIAS_LICENCIA_MATERNIDAD","DIAS_AJS_LICENCIA_MATERN","DIAS_INASISTENCIA_INJUST",
             "DIAS_VACACIONES","DIAS_VACACIONES_FESTIVAS","DIAS_VACACIONES_DINERO","DIAS_GASTO_INCAPACIDAD","DIAS_LIC_LEY_MARIA_8_DIAS",
             "DIAS_INCAPACIDAD_ACC_TRAB","DIAS_INCAP_ENFERMEDAD_GEN","DIAS_VAC_HABILES_SAL_INT","DIAS_INCAPACIDAD_AL_50%","DIAS_DÍA_NO_LAB_DER_A_PAG",
             "DIAS_RTEGRO_DTO_INASISTEN","DIAS_DTO_SALARIO","DIAS_INASIS_X_INC_>_180_D","DIAS_INCAP_ENF_GEN_PRORR","DIAS_DTO_INC_ENF_GRAL_AL",
             "DIAS_RETROACTIV_SALARIO","DIAS_PERMISO_PERSONAL","DIAS_AJUS_SALARIO",
             ]

# Sort columns in df_acumulado based on the list
df_acumulado = col.select_columns(df_acumulado, list_sort)

# --------------- JOIN FILES OF TEMPORALES AND NOMINA ---------------
# Rename Columns
df_temp = col.rename_columns(df_temp, {
    "TIPO DE VINCULACIÓN":"TIPO_DE_VINCULACIÓN",
    "COST CENTER":"CENTRO DE COSTOS", 
    "COST CENTER NAME":"NOMBRE CENTRO DE COSTOS",
    "CEDULA":"NUMERO DOCUMENTO",
    "NOMBRE DEL EMPLEADO":"NOMBRE COMPLETO",
    "FECHA INGRESO (D/M/A)":"FECHA DE INGRESO",
    "FECHA DE RETIRO (D/M/A)":"FECHA DE BAJA",
    "SALARIO BASICO":"SALARIO MENSUAL",
    "DIAS PAGO NOMINA":"DIAS_PAGO_NOMINA",
    "SALARIO A PAGAR":"SALARIO_A_PAGAR",
    "SUBSIDIO DE TRANSPORTE":"SUBSIDIO_TRANSPORTE",
    "HRS. HORA EXTRA DIURNA - 1,25":"HRS_HORA_EXTRA_DIURNA - 1,25",
    "VR. HORA EXTRA DIURNA - 1,25":"VR._HORA_EXTRA_DIURNA - 1,25",
    "HRS. HORA EXTRA NOCTURNA - 1,75":"HRS._HORA_EXTRA_NOCTURNA - 1,75",
    "VR. HORA EXTRA NOCTURNA - 1,75":"VR._HORA_EXTRA_NOCTURNA - 1,75",
    "NO.HORA ORD DOMINICAL 175":"NO.HORA_ORD_DOMINICAL_175",
    "VA.HORA ORD DOMINICAL 175":"VR.HORA_ORD_DOMINICAL_175",
    "HRS. EXTRA HORA DOM/FEST. NOCTURNA 2.50%":"HRS._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "VR. EXTRA HORA DOM/FEST. NOCTURNA 2.50%":"VR._EXTRA_HORA_DOM/FEST._NOCTURNA_2.50%",
    "HRS. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%":"HRS._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "VR. HORA EXTRA DOMINICAL Y FESTIVA DIURNA 2.00%":"VR._HORA_EXTRA_DOMINICAL_Y_FESTIVA_DIURNA_2.00%",
    "TOTAL # H.E.":"TOTAL # H.E.",
    "TOTAL HORAS EXTRAS SIN R.N.":"TOTAL_HORAS_EXTRAS_SIN_R.N.",
    "HRS. DOMINICAL DIURNO - 1,75":"HRS._DOMINICAL_DIURNO - 1,75",
    "VR. DOMINICAL DIURNO - 1,75":"VR._DOMINICAL_DIURNO - 1,75",
    "HRS. FESTIVO DIURNO - 1,75":"HRS._FESTIVO_DIURNO - 1,75",
    "VR. FESTIVO DIURNO - 1,75":"VR._FESTIVO_DIURNO - 1,75",
    "HRS. RECARGO DOMINICAL NOCTURNO - 2,10":"HRS. RECARGO DOMINICAL NOCTURNO - 2,1",
    "VR. RECARGO DOMINICAL NOCTURNO - 2,10":"VR._RECARGO_DOMINICAL_NOCTURNO - 2,1",
    "HRS. RECARGO FESTIVO NOCTURNO - 2,1":"HRS._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "VR. RECARGO FESTIVO NOCTURNO - 2,1":"VR._RECARGO_FESTIVO_NOCTURNO - 2,1",
    "HRS. HORA DOMINICAL Y FESTIVO CON COMPENSATORIO DIUR 1.00%":"HRS._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "VR. HORA DOMINICAL Y FESTIVO CON COMPENSATORIO DIUR 1.00%":"VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_DIUR_1.00%",
    "HRS HORA DOMINICAL Y FESTIVO CON COMPENSATORIO NOC 1.35%":"HRS_HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "VR. HORA DOMINICAL Y FESTIVO CON COMPENSATORIO NOC 1.35%":"VR._HORA_DOMINICAL_Y_FESTIVO_CON_COMPENSATORIO_NOC_1.35%",
    "HRS RECARGO NOCTURNO - 0,35":"HRS_RECARGO_NOCTURNO - 0,35",
    "VR. RECARGO NOCTURNO - 0,35":"VR._RECARGO_NOCTURNO - 0,35",
    "TOTAL NO. RECARGO NOCTURNO":"TOTAL NO. RECARGOS",
    "TOTAL $ RECARGO NOCTURNO":"TOTAL_$_RECARGOS",
    "REAJUSTE RECARGOS":"REAJUSTE_RECARGOS",
    "REAJUSTE H.E":"REAJUSTE_H.E",
    "REAJUSTE SALARIAL":"REAJUSTE_SALARIAL",  
    "REAJUSTE AUSENCIAS JUSTIFICADAS":"REAJUSTE_AUSENCIAS_JUSTIFICADAS",
    "REAJUSTE VACACIONES":"REAJUSTE_VACACIONES",
    "DIAS AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)":"DIAS_AUSENCIAS_JUSTIFICADAS_SIN_COBRO (Vac. Habiles, inc 66,67%)",
    "VALOR AUSENCIAS JUSTIFICADAS SIN COBRO (Vac. Habiles, inc 66,67%)": "VALOR_AUSENCIAS_JUSTIFICADAS_SIN_COBRO_(Vac. Habiles, inc 66,67%)",
    "BONIFICACION NO CONSTITUTIVA DE SALARIO":"BONIFICACION_NO_CONSTITUTIVA_DE_SALARIO",
    "BONIFICACION SALARIAL":"BONIFICACION_SALARIAL",
    "TRANSPORTE EXTRALEGAL AUT. POR CL":"TRANSPORTE_EXTRALEGAL_AUT._POR_CL",
    "AUXILIO DE RODAMIENTO":"AUXILIO_DE_RODAMIENTO",
    "MAYOR VALOR PAGADO AUX. DE RODAMIENTO":"MAYOR_VALOR_PAGADO_AUX._DE_RODAMIENTO",
    "MAY. VALOR PAGADO EN SALARIO":"MAY._VALOR_PAGADO_EN_SALARIO",
    "MAY. VALOR PAGADO EN AUX. TRANS":"MAY._VALOR_PAGADO_EN_AUX._TRANS",
    "EXAMENES MEDICOS SERVICIOS":"EXAMENES_MEDICOS_SERVICIOS",
    "OTROS CONCEPTOS FACTURABLES PRESTACIONALES ":"OTROS_CONCEPTOS_FACTURABLES_PRESTACIONALES",
    "CONCEPTOS NO CONTEMPLADOS SUPPLA- NO PRESTACIONALES CON SERVICIOS":"CONCEPTOS_NO_CONTEMPLADOS_SUPPLA_NO_PRESTACIONALES_CON_SERVICIOS",
    "SALUD PATRONO":"SALUD_PATRONO",
    "PENSION 12%":"PENSION_12%",
    "TOTAL S.S.":"TOTAL_S.S.",
    "CAJA DE COMP 4%":"CAJA_DE_COMP_4%",
    "VALOR PARAFISCALES":"VALOR_PARAFISCALES",
    "CESANTIAS 8.33%":"CESANTIAS_8.33%",
    "INT. CESANTIAS 1%":"INT._CESANTIAS_1%",
    "PRIMA 8.33%":"PRIMA_8.33%",
    "VACACIONES 4.34%":"VACACIONES_4.34%",
    "VALOR PRESTACIONES":"VALOR_PRESTACIONES",
    "TOTAL NOMINA S.S.PARAFI PRESTA":"TOTAL_NOMINA_S.S.PARAFI_PRESTA",
    "BONIFICACION DIRECTIVO":"BONIFICACION_DIRECTIVO",
})

# Delete Duplicated Rows
df_acumulado = col.delete_duplicate_rows(df_acumulado, column_name="NUMERO DOCUMENTO",keep="first")

# Create New Column
df_acumulado = col.new_column(df_acumulado,column_name="MES",default_value=nombreMesActual)

# Concatenate DataFrames
df_acumulado = concat_dataframes(df_up=df_acumulado,df_down=df_temp,axis=0)

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado,["a"])

# --------------- EXECUTE FUNCTION TO CREATE OBSERVATION ---------------
# Variable for current year
anio_actual = datetime.now().year  # o pásalo fijo si lo necesitas

# Execute function to create commentary column based on conditions of days of payroll and salary
df_acumulado = execute_analysis_days_payroll(
    df=df_acumulado,
    nombre_mes_actual=nombreMesActual,
    nombre_mes_anterior=nomMesAnterior,
    anio=anio_actual,
    salario_ft_umbral=salary_target, # Rule for full-time salary threshold
    dias_mes_base=30
)

# Exrcute Funciotn to Validate Offboarding Friday/Saturday + dto/no lab
df_acumulado = validate_offboarding_weekdays(df_acumulado, empresa_value="SUPPLA S.A")

# Get number of days in current month based on rules and assign it to a variable
days_current_month = config_days_month_rules(get_days_month(nombreMesActual, anio_actual),base=30)

# Execute Function to Validate Change of Vinculation
df_acumulado = validate_vinculation_change(df_acumulado, dias_mes_actual=days_current_month)

# Execute Function charge/salary validation vs previous month (merge + column)
df_acumulado = validate_salary_role_previous_month(df_acumulado, df_consoNomina)

# Delete Columns
df_acumulado = col.delete_columns(df_acumulado, ["CARGO NOMINA_y", "CEDULA", "SALARIO BASICO"])

# Execute Function to Validate Days of Payroll based on "NOVEDADES" and rules for days of month
df_acumulado = validate_days_by_novedades(df_acumulado,dias_mes_actual=days_current_month,empresa_value="SUPPLA S.A")














# ------------------- Display Preview -------------------
st.divider()
st.subheader("📋 Preview – File Analysis of Payroll (df_acumulado)")


st.dataframe(
    df_acumulado,
    use_container_width=True
)

