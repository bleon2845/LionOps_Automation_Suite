import time
import pandas as pd
from integrations.sap.sap_gui import SapGUI

class CreateOrderMB21():
    def __init__(self, sap_session):
        self.session = sap_session

    #----------- Create documents from excel file -----------
    def create_documentsMB21(self, file_path, file_folder): # Use folder to save temporary files if needed
        data = pd.read_excel(file_path, sheet_name='Creation').astype(str)# File must have a sheet named 'Creation'
        data.columns = (data.columns.str.strip().str.upper().str.replace(r"\s+", "_", regex=True))# Check columns format and replace spaces with underscores

        # Register general data
        self.session.findById("wnd[0]/tbar[0]/okcd").Text = "/NMB21" #Transaction code to create material document
        self.session.findById("wnd[0]").sendVKey(0)

        procesando = False  #Control variable to avoid multiple processing
        header_set = False #Control variable to set header data only once
        row_number = 0 #Row counter for items in SAP

        for i, row in data.iterrows():

            if row["INDICE"] == "X":
                procesando = True
                header_set = False
                row_number = 0

            if not procesando:
                continue

            if not header_set:
                #claseMov = str(row.get("CLASE_DE_MOV", "")).strip().replace(" ","").split(".")[0] # Get movement type, remove spaces and take only the first part if it contains dots

                self.session.findById("wnd[0]/usr/ctxtRM07M-BWART").text = row["CLASE_DE_MOV"]
                self.session.findById("wnd[0]/usr/ctxtRM07M-WERKS").text = row["CENTRO"]
                self.session.findById("wnd[0]/usr/ctxtRM07M-WERKS").setFocus()
                self.session.findById("wnd[0]/usr/ctxtRM07M-WERKS").caretPosition = 4
                self.session.findById("wnd[0]").sendVKey(0)
                time.sleep(1)

                header_set = True

            self.session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1006/ctxtCOBL-PS_POSID").text = row["PEP"]
            self.session.findById(f"wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-MATNR[{row_number},7]").text = row["MATERIAL"]
            self.session.findById(f"wnd[0]/usr/sub:SAPMM07R:0521/txtRESB-ERFMG[{row_number},26]").text = row["CANTIDAD"]
            self.session.findById(f"wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-LGORT[{row_number},53]").text = row["CENTRO"]
            self.session.findById(f"wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-CHARG[{row_number},58]").text = row["BODEGA"]
            self.session.findById(f"wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-CHARG[{row_number},58]").setFocus()
            self.session.findById(f"wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-CHARG[{row_number},58]").caretPosition = 4

            row_number += 1

            if str(row.get("GUARDAR", "")).strip().upper() == "X":
                # logic to save the document, for example by clicking the save button or sending the appropriate key

                header_set = False   # change header_set to False to set new header data in next iteration
                row_number = 0       # restart row number for next document

