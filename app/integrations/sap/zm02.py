import time
import pandas as pd
from integrations.sap.sap_gui import SapGUI
from integrations.sap import session
import pythoncom
import win32gui
import win32com.client
from pathlib import Path
from integrations.sap.close_excel import close_excel_file

class Z02RTPTR():
    def __init__(self):
        pythoncom.CoInitialize()
        try:
            # We connect to the already open instance of SAP in Windows
            SapGuiAuto = win32com.client.GetObject("SAPGUI")
            application = SapGuiAuto.GetScriptingEngine
            connection = application.Children(0)
            self.session = connection.Children(0) # This takes the active session
        except Exception as e:
            raise Exception(f"No se pudo enganchar a la sesión de SAP activa: {e}")

    #----------- Download Report Z02RTPTR -----------
    def download_Z02RTPTR(self):
        # Delete file if it already exists
        #ruta_base = Path(r"C:/temp/SAP")
        #archivo_excel = ruta_base / "Archivo_Transitos.xlsx"
        
        #if archivo_excel.exists():
        #    try:
        #        archivo_excel.unlink()
        #        print(f"Deleted previous file: {archivo_excel}")
        #    except Exception as e:
        #        print(f"Could not delete file: {e}")

        # Enter in Z02RTPTR_0375A_ME2N transaction
        self.session.findById("wnd[0]/tbar[0]/okcd").text = "Z02RTPTR_0375A_ME2N"
        self.session.findById("wnd[0]").sendVKey(0)
        self.session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = ""
        self.session.findById("wnd[0]/usr/btn%_EN_EBELN_%_APP_%-VALU_PUSH").press()
        self.session.findById("wnd[1]/tbar[0]/btn[23]").press()
        self.session.findById("wnd[2]/usr/ctxtDY_PATH").text = "C:/temp/SAP/" #Path to the file with the orders
        self.session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "Orders.txt"
        self.session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 10
        self.session.findById("wnd[2]/tbar[0]/btn[0]").press()
        self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
