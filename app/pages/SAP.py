import sys
from pathlib import Path

# Esto permite que la página encuentre la carpeta 'integrations' en la raíz
root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import streamlit as st
import time
import pythoncom
from integrations.sap.sap_gui import SapGUI
from integrations.sap.facade import SapFacade
from integrations.sap.create_order import CreateOrder
import os
import pandas as pd

# Configuración de página
st.set_page_config(page_title="SAP RPA Dashboard", layout="wide")

# --- INICIALIZACIÓN DEL ESTADO (SINGLETON PATTERN) ---
# Esto asegura que solo exista UNA instancia de SAP conectada
if 'sap_facade' not in st.session_state:
    try:
        # Inicializamos el hilo COM para evitar errores de hilos en servidores web
        pythoncom.CoInitialize() 
        gui = SapGUI()
        st.session_state.sap_facade = SapFacade(gui)
        st.session_state.logged_in = False
    except Exception as e:
        st.error(f"Error al inicializar SAP GUI: {e}")

# --- INTERFAZ DE USUARIO ---
st.title("🤖 Centro de Control SAP RPA")
st.markdown("---")

# Layout de dos columnas: Login y Acciones
col_login, col_actions = st.columns([1, 2])

with col_login:
    st.subheader("🔐 Autenticación")
    with st.container(border=True):
        username = st.text_input("Usuario SAP", help="Ej: MROSSI")
        password = st.text_input("Contraseña", type="password")
        system = st.text_input("Nombre del Sistema", value="EPA [ANDINA_COPA]", help="Nombre en SAP Logon")
        
        if st.button("Iniciar Sesión en SAP", use_container_width=True):
            pythoncom.CoInitialize()
            with st.status("Conectando con SAP...", expanded=True) as status:
                try:
                    # Usamos tu método existente de la Facade
                    st.write("Abriendo SAP GUI...")
                    success = st.session_state.sap_facade.login(
                        username=username, 
                        password=password, 
                        system_name=system
                    )
                    if success:
                        st.session_state.logged_in = True
                        status.update(label="✅ Conexión Exitosa", state="complete", expanded=False)
                        st.success("Sesión activa en SAP")
                        st.rerun()
                except Exception as e:
                    status.update(label="❌ Error de Conexión", state="error")
                    st.error(f"Detalle: {e}")

with col_actions:
    st.subheader("⚙️ Automatizaciones Disponibles")
    
    if not st.session_state.logged_in:
        st.info("Estatus: Esperando conexión para habilitar comandos.")
    else:
        # Aquí puedes agregar botones para tus otras clases (CreateOrder, etc.)
        tab1, tab2 = st.tabs(["Pedidos (ME21N)", "Pedidos (MB21)"])
        
        with tab1:
            st.write("### Ejecutar creación de pedidos masiva (ME21N)")
            
            # 1. El cargador de archivos debe estar fuera del bloque del botón
            uploaded_file = st.file_uploader("Subir Archivo de Creación", type=["xlsx"])

            if uploaded_file:
                # 2. Leer y mostrar los datos inmediatamente al cargar
                try:
                    df_preview = pd.read_excel(uploaded_file, sheet_name='Creation')
                    
                    st.write("#### 📊 Vista previa de los datos cargados:")
                    st.dataframe(df_preview, use_container_width=True)
                    
                    total_items = len(df_preview[df_preview['INDICE'] == 'X'])
                    st.info(f"Se procesarán **{total_items}** posiciones marcadas con 'X' en la columna INDICE.")

                except Exception as e:
                    st.error(f"Error al leer el archivo: {e}")

                # 3. El botón de ejecución aparece solo si hay un archivo cargado
                if st.button("🚀 Lanzar Proceso ME21N", use_container_width=True):
                    try:
                        temp_path = os.path.join(os.getcwd(), "temp_upload.xlsx")
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        with st.status("Trabajando en SAP...", expanded=True) as status:
                            pythoncom.CoInitialize()
                            bot = CreateOrder()
                            
                            # Llamar a tu función original
                            bot.create_documents(temp_path, os.getcwd())
                            
                            status.update(label="✅ Proceso finalizado", state="complete")
                            st.success("El bot ha terminado de procesar el archivo.")
                            
                        # Limpiar archivo temporal
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                    except Exception as e:
                        st.error(f"Error durante la ejecución: {e}")

        with tab2:
            st.write("Generación de documentos MB21.")
            if st.button("📋 Iniciar MB21"):
                st.info("Procesando datos...")

# --- FOOTER / STATUS ---
st.sidebar.markdown("### Estado del Sistema")
if st.session_state.logged_in:
    st.sidebar.success("Conectado a SAP")
    if st.sidebar.button("Forzar Cierre de Sesión"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.sidebar.warning("Desconectado")