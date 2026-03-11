import time
import pandas as pd
from integrations.sap.sap_gui import SapGUI
from integrations.sap import session
import pythoncom
import win32gui
import win32com.client


class Mb5t():
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

    #----------- Download Report MB5T -----------
    def download_mb5t(self):
        # Enter in MB5T transaction
        self.session.findById("wnd[0]/tbar[0]/okcd").Text = "/NMB5T" #Transaction code to create material document
        self.session.findById("wnd[0]").sendVKey(0)

        position = 1

        # Register general data
        self.session.findById("wnd[0]/usr/btn%_WERKS_%_APP_%-VALU_PUSH").press()
        self.session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,0]").text = "C901"
        self.session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,1]").text = "C906"
        self.session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").text = "C022"
        self.session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").setFocus()
        self.session.findById("wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/ctxtRSCSEL_255-SLOW_I[1,2]").caretPosition = 4
        self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
        
        # Register procedence centers
        self.session.findById("wnd[0]/usr/btn%_RESWK_%_APP_%-VALU_PUSH").press()
        self.session.findById("wnd[1]/tbar[0]/btn[23]").press()
        self.session.findById("wnd[2]/usr/ctxtDY_PATH").text = r"C:\Users\bleonpar\OneDrive - DPDHL\Documents\SAP\SAP GUI\Centers.txt"
        self.session.findById("wnd[2]/usr/ctxtDY_PATH").setFocus()
        self.session.findById("wnd[2]/usr/ctxtDY_PATH").caretPosition = 68
        self.session.findById("wnd[2]/tbar[0]/btn[0]").press()
        self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # It's necessary to wait until the system process the data and show the report
        self.session.findById("wnd[0]/tbar[1]/btn[43]").press()

        # Select variant with all the data and download the report
        self.session.findById("wnd[0]/mbar/menu[3]/menu[2]/menu[1]").select()
        self.session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").currentCellRow = 41
        self.session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").firstVisibleRow = 31
        self.session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").selectedRows = "41"
        self.session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()

        # Download the report in the specified path
        #self.session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[1]").select()
        #self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "Archivo_Transitos.xlsx"
        #self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 22
        #self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        #self.session.findById("wnd[0]/tbar[0]/btn[15]").press()
        #self.session.findById("wnd[0]/tbar[0]/btn[15]").press()
        #self.session.findById("wnd[0]/tbar[0]/btn[15]").press()
