import time
import pandas as pd
from integrations.sap.sap_gui import SapGUI
import win32com.client
import pythoncom

class CreateOrder():
    def __init__(self):
        pythoncom.CoInitialize()
        try:
            # Nos conectamos a la instancia de SAP que ya está abierta en Windows
            SapGuiAuto = win32com.client.GetObject("SAPGUI")
            application = SapGuiAuto.GetScriptingEngine
            connection = application.Children(0)
            self.session = connection.Children(0) # Esto toma la sesión activa
        except Exception as e:
            raise Exception(f"No se pudo enganchar a la sesión de SAP activa: {e}")

    #----------- Create documents from excel file -----------
    def element_exists(self, element_id):
        try:
            self.session.findById(element_id)
            return True
        except:
            return False

    def ensure_header(self):
        header_tabs = ("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL")

        if not self.element_exists(header_tabs):
            try:
                self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
            except:
                pass
        self.session.findById(header_tabs + "/tabpTABHDT3").select()

    def create_documents(self, file_path, file_folder): # Use folder to save temporary files if needed
        data = pd.read_excel(file_path, sheet_name='Creation').astype(str)# File must have a sheet named 'Creation'
        data.columns = (data.columns.str.strip().str.upper().str.replace(r"\s+", "_", regex=True))# Check columns format

        # Register general data
        self.session.findById("wnd[0]/tbar[0]/okcd").Text = "/NME21N"
        self.session.findById("wnd[0]").sendVKey(0)

        self.ensure_header() # Ensure header is visible

        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/cmbMEPO_TOPLINE-BSART").setFocus()
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/cmbMEPO_TOPLINE-BSART").key = "AUB"
        time.sleep(1)

        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/ctxtMEPO_TOPLINE-SUPERFIELD").text = "C906"
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1221/ctxtMEPO1222-EKORG").text = "CO02"
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1221/ctxtMEPO1222-EKGRP").text = "T34"
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1221/ctxtMEPO1222-BUKRS").text = "CO15"
        self.session.findById("wnd[0]").sendVKey(0)

        # Register header text NA
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3").select()
        # Change the text "NA" according to file
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT3/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1230/subTEXTS:SAPLMMTE:0100/subEDITOR:SAPLMMTE:0101/cntlTEXT_EDITOR_0101/shellcont/shell").text = "NA"
        
        # Click to zoom in items
        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000/btnDYN_4000-BUTTON").press()
        
        procesando = False  #Control variable to avoid multiple processing

        row_number = 0 #Row counter for items in SAP
        scroll_number = 0 #Scroll counter to manage scrolling in SAP table

        for i, row in data.iterrows():

            if row["INDICE"] == "X":
                procesando = True

            #Execute only when the row is marked to be processed
            if procesando:

                # Register Item Data
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/txtMEPO1211-AFNAM[2,{row_number}]").text = row["PROYECTO"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-EMATN[3,{row_number}]").text = row["MATERIAL"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/txtMEPO1211-MENGE[4,{row_number}]").text = row["CANTIDAD"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-EEIND[5,{row_number}]").text = row["FECHA"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-NAME1[6,{row_number}]").text = row["CENTRO"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-LGOBE[7,{row_number}]").text = row["ALM.DEST"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-CHARG[8,{row_number}]").text = row["LOTE"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/txtMEPO1211-BEDNR[9,{row_number}]").text = row["OT"]
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-RESLO_BEZ[10,{row_number}]").text = row["BODEGA"]
                # Focus in each row to avoid errors
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-LGOBE[7,{row_number}]").setFocus()
                self.session.findById(f"wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211/ctxtMEPO1211-LGOBE[7,{row_number}]").caretPosition = 4

                # Confirm destination warehouse this action open a popup
                self.session.findById("wnd[0]").sendVKey(0)

                # Try to find popup window
                try:
                    popup = self.session.findById("wnd[1]")
                    # If found, press OK button
                    popup.findById("tbar[0]/btn[0]").press()
                except:
                    # If not found, continue without failing
                    pass
                
                #time.sleep(5)

                try:
                    self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0019/subSUB3:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4002/btnDYN_4000-BUTTON").press()
                except:
                    try:
                        self.session.findById("wnd[0]/usr/subSUB0:SAPLMEGUI:0015/subSUB3:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4002/btnDYN_4000-BUTTON").press()
                    except:
                        pass

                row_number += 1
                scroll_number += 1

                if scroll_number == 14:
                    for pos in range(1, 14):
                        self.session.findById(
                            "wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB2:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1:SAPLMEGUI:1211/tblSAPLMEGUITC_1211"
                        ).verticalScrollbar.position = pos
                        row_number = 1  # Reset row number after scrolling
                
            if row["GUARDAR"] == "X":
                break