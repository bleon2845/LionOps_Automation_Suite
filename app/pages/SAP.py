import sys
from pathlib import Path

root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import os
import pandas as pd
import pythoncom
import streamlit as st

from integrations.sap.sap_gui import SapGUI
from integrations.sap.facade import SapFacade
from integrations.sap.create_order import CreateOrder
from integrations.sap.save_docs import SaveDocs
from integrations.sap.mb5t import Mb5t

# ------------------- Page Configuration -------------------
st.set_page_config(
    page_title="SAP RPA Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- CSS visual enterprise -------------------
st.markdown("""
<style>
.sap-card {
    background-color: #111827;
    border: 1px solid #1F2937;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
}

.sap-card h3 {
    margin-top: 0;
    margin-bottom: 8px;
    color: #F9FAFB;
}

.sap-card p {
    color: #D1D5DB;
    margin-bottom: 0;
}

.sap-section-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
    color: #F9FAFB;
}

.sap-kpi {
    background-color: #1F2937;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    border: 1px solid #374151;
}

.sap-kpi-title {
    color: #9CA3AF;
    font-size: 0.9rem;
}

.sap-kpi-value {
    color: #F9FAFB;
    font-size: 1.3rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ------------------- Initialization -------------------
if "sap_facade" not in st.session_state:
    try:
        pythoncom.CoInitialize()
        gui = SapGUI()
        st.session_state.sap_facade = SapFacade(gui)
        st.session_state.logged_in = False
    except Exception as e:
        st.error(f"Error al inicializar SAP GUI: {e}")

if "sap_menu" not in st.session_state:
    st.session_state.sap_menu = "Login"

# ------------------- Auxiliary Functions -------------------
def render_login_card():
    st.markdown('<div class="sap-section-title">🔐 Autenticación SAP</div>', unsafe_allow_html=True)

    with st.container(border=True):
        username = st.text_input("Usuario SAP", help="Ej: MROSSI o usuario corporativo")
        password = st.text_input("Contraseña", type="password")
        system = st.text_input(
            "Nombre del Sistema",
            value="EPA [ANDINA_COPA]",
            help="Nombre exacto configurado en SAP Logon"
        )

        if st.button("Iniciar Sesión en SAP", use_container_width=True):
            pythoncom.CoInitialize()
            with st.status("Conectando con SAP...", expanded=True) as status:
                try:
                    st.write("Abriendo SAP GUI...")
                    success = st.session_state.sap_facade.login(
                        username=username,
                        password=password,
                        system_name=system
                    )

                    if success:
                        st.session_state.logged_in = True
                        st.session_state.sap_menu = "Automatizaciones"
                        status.update(label="✅ Conexión exitosa", state="complete", expanded=False)
                        st.success("Sesión iniciada correctamente en SAP.")
                        st.rerun()
                    else:
                        status.update(label="❌ No fue posible iniciar sesión", state="error")
                        st.error("No se pudo establecer sesión en SAP.")

                except Exception as e:
                    status.update(label="❌ Error de conexión", state="error")
                    st.error(f"Detalle: {e}")


def render_automation_cards():
    st.markdown('<div class="sap-section-title">⚙️ Automatizaciones disponibles</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="sap-card">
            <h3>📝 Orders (ME21N)</h3>
            <p>Creación masiva de pedidos desde archivo Excel.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir ME21N", use_container_width=True):
            st.session_state.sap_menu = "ME21N"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="sap-card">
            <h3>📝 Orders (MB21)</h3>
            <p>Generación de documentos logísticos y movimientos.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir MB21", use_container_width=True):
            st.session_state.sap_menu = "MB21"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="sap-card">
            <h3>🖨️ Print Documents</h3>
            <p>Impresión y guardado de documentos PDF desde SAP.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Print Documents", use_container_width=True):
            st.session_state.sap_menu = "Print Documents"
            st.rerun()

    with col4:
        st.markdown("""
        <div class="sap-card">
            <h3>📥 Download MB5T</h3>
            <p>Descarga de documentos desde SAP.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Abrir Download MB5T", use_container_width=True):
            st.session_state.sap_menu = "Download MB5T"
            st.rerun()


def render_me21n():
    st.subheader("📝 Ejecutar creación de pedidos masiva (ME21N)")

    uploaded_file = st.file_uploader(
        "Subir Archivo de Creación",
        type=["xlsx"],
        key="upload_me21n"
    )

    if uploaded_file:
        try:
            df_preview = pd.read_excel(uploaded_file, sheet_name="Creation")
            st.write("#### 📊 Vista previa de los datos cargados")
            st.dataframe(df_preview, use_container_width=True)

            total_items = len(df_preview[df_preview["INDICE"] == "X"])
            st.info(f"Se procesarán **{total_items}** posiciones marcadas con 'X' en la columna INDICE.")

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return

        if st.button("🚀 Lanzar Proceso ME21N", use_container_width=True):
            try:
                temp_path = os.path.join(os.getcwd(), "temp_upload.xlsx")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.status("Trabajando en SAP...", expanded=True) as status:
                    pythoncom.CoInitialize()
                    bot = CreateOrder()
                    bot.create_documents(temp_path, os.getcwd())
                    status.update(label="✅ Proceso finalizado", state="complete")
                    st.success("El bot ha terminado de procesar el archivo.")

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            except Exception as e:
                st.error(f"Error durante la ejecución: {e}")


def render_mb21():
    st.subheader("📋 Generación de documentos MB21")

    st.markdown("""
    <div class="sap-card">
        <h3>MB21</h3>
        <p>Este módulo permitirá ejecutar procesos asociados a la transacción MB21.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📋 Iniciar MB21", use_container_width=True):
        st.info("Procesando datos...")


def render_print_documents():
    st.subheader("🖨️ Generación de documentos PDF")

    uploaded_print = st.file_uploader(
        "Subir Archivo de Impresión",
        type=["xlsx"],
        key="upload_docs"
    )

    if uploaded_print:
        try:
            df_print = pd.read_excel(uploaded_print, sheet_name="Print")
            st.write("#### 📊 Vista previa de documentos a imprimir")
            st.dataframe(df_print, use_container_width=True)

            output_path = os.path.join(os.getcwd(), "PDF_Outputs")
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            if st.button("🚀 Iniciar Proceso de Impresión", use_container_width=True):
                try:
                    temp_print_path = os.path.join(os.getcwd(), "temp_print.xlsx")
                    with open(temp_print_path, "wb") as f:
                        f.write(uploaded_print.getbuffer())

                    with st.status("Ejecutando impresión en SAP...", expanded=True) as status:
                        pythoncom.CoInitialize()
                        bot_print = SaveDocs()
                        bot_print.print_documents(temp_print_path, output_path)
                        status.update(label="✅ Impresión completada", state="complete")
                        st.success(f"Documentos guardados en: {output_path}")

                    if os.path.exists(temp_print_path):
                        os.remove(temp_print_path)

                except Exception as e:
                    st.error(f"Error durante la ejecución: {e}")

        except Exception as e:
            st.error(f"No se encontró la hoja 'Print' o el archivo es inválido: {e}")

def render_mb5t():
    st.subheader("📥 Download Report")

    if st.button("🚀 Iniciar Proceso de Descarga", use_container_width=True):
        try:
            with st.status("Ejecutando descarga en SAP...", expanded=True) as status:
                pythoncom.CoInitialize()
                bot_mb5t = Mb5t()
                bot_mb5t.download_mb5t()

                status.update(label="✅ Download Completed", state="complete")
                st.success(f"Process Finished With Success")

        except Exception as e:
            st.error(f"Error during download: {e}")

# ------------------- Sidebar -------------------
st.sidebar.title("SAP")
if st.session_state.logged_in:
    menu_options = ["Automatizaciones", "ME21N", "MB21", "Print Documents", "Download MB5T", "Login"]
else:
    menu_options = ["Login"]

sap_menu = st.sidebar.radio("Submenú SAP", menu_options, index=menu_options.index(st.session_state.sap_menu) if st.session_state.sap_menu in menu_options else 0)
st.session_state.sap_menu = sap_menu

st.sidebar.markdown("---")
st.sidebar.markdown("### Estado del Sistema")

if st.session_state.logged_in:
    st.sidebar.success("Conectado a SAP")
    if st.sidebar.button("Forzar Cierre de Sesión"):
        st.session_state.logged_in = False
        st.session_state.sap_menu = "Login"
        st.rerun()
else:
    st.sidebar.warning("Desconectado")

# ------------------- Header principal -------------------
st.title("🤖 Centro de Control SAP RPA")
st.markdown("---")

# ------------------- Resumen visual -------------------
if st.session_state.logged_in:
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.markdown("""
        <div class="sap-kpi">
            <div class="sap-kpi-title">Estado SAP</div>
            <div class="sap-kpi-value">Conectado</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown("""
        <div class="sap-kpi">
            <div class="sap-kpi-title">Módulos Activos</div>
            <div class="sap-kpi-value">3</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown("""
        <div class="sap-kpi">
            <div class="sap-kpi-title">Sesión</div>
            <div class="sap-kpi-value">Operativa</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ------------------- Render según submenú -------------------
if sap_menu == "Login":
    render_login_card()

elif sap_menu == "Automatizaciones":
    render_automation_cards()

elif sap_menu == "ME21N":
    render_me21n()

elif sap_menu == "MB21":
    render_mb21()

elif sap_menu == "Print Documents":
    render_print_documents()

elif sap_menu == "Download MB5T":
    render_mb5t()