import time
import pandas as pd
import pyautogui
import os
import win32gui
import win32com.client
import threading
from datetime import datetime
import shutil

from integrations.sap import session
import pythoncom


class SaveDocs():
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

    def save_pdf(self, full_path: str, timeout: float = 40.0):
        
        TARGET_CLASSES = {"#32770", "Xaml_WindowedPopupClass"}# Class names to look for

        def _find_file_dialog():
            found = None

            def cb(hwnd, _):
                nonlocal found
                if found is not None:
                    return

                if not win32gui.IsWindowVisible(hwnd):
                    return

                cls = win32gui.GetClassName(hwnd)
                if cls not in TARGET_CLASSES:
                    return

                title = win32gui.GetWindowText(hwnd) or ""

                if "SAP Logon" in title: # Avoid the main SAP window
                    return

                found = hwnd

            win32gui.EnumWindows(cb, None)
            return found

        print("[save_pdf] Search (Save As / PopupHost)...")

        end = time.time() + timeout
        hwnd_dialog = None
        while time.time() < end and hwnd_dialog is None:
            hwnd_dialog = _find_file_dialog()
            if hwnd_dialog is None:
                time.sleep(0.3)

        if hwnd_dialog is None:
            raise RuntimeError("Window Save As not found.")

        title = win32gui.GetWindowText(hwnd_dialog)
        cls = win32gui.GetClassName(hwnd_dialog)
        print(f"[save_pdf] Window in use hwnd={hwnd_dialog}, clase='{cls}', título='{title}'")

        try: # Bring it to the front
            win32gui.SetForegroundWindow(hwnd_dialog)
        except Exception as e:
            print("window of saved no activated:", e)

        time.sleep(0.7)

        pyautogui.hotkey("alt", "n")   # Go to File name field
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(full_path)
        pyautogui.press("enter")

        print(f"[save_pdf] Path written: {full_path}")

    def print_documents(self, file_path, output_folder):
        dataprint = pd.read_excel(file_path, sheet_name='Print').astype(str) #file must have a sheet named 'Print'
        dataprint.columns = (dataprint.columns.str.strip().str.upper().str.replace(r"\s+", "_", regex=True))# Check columns format
        current_year = str(datetime.now().year)

        for _, row in dataprint.iterrows():

            #--------------- MB02 PRINT MATERIAL DOCUMENT ---------------#
            self.session.findById("wnd[0]/tbar[0]/okcd").text = "/NMB02" #Transaction code to print material document
            self.session.findById("wnd[0]").sendVKey(0)
            self.session.findById("wnd[0]/usr/ctxtRM07M-MBLNR").text = row["DOCUMENTO"]
            self.session.findById("wnd[0]/usr/txtRM07M-MJAHR").text = current_year #row["AÑO"] # Year of the document
            self.session.findById("wnd[0]/usr/txtRM07M-MJAHR").setFocus()
            self.session.findById("wnd[0]/usr/txtRM07M-MJAHR").caretPosition = 4
            self.session.findById("wnd[0]").sendVKey (0)

            #--------------- TRY INBOUND, ELSE OUTBOUND ---------------#
            try:
                # INBOUND
                field_in = self.session.findById("wnd[0]/usr/sub:SAPMM07M:0221/txtMSEG-ERFMG[0,7]")
                field_in.setFocus()
                field_in.caretPosition = 5
                self.session.findById("wnd[0]").sendVKey(2)
                typeOperation = "CF06"

            except Exception:
                # OUTBOUND
                field_out = self.session.findById("wnd[0]/usr/sub:SAPMM07M:0420/txtMSEG-ERFMG[0,5]")
                field_out.setFocus()
                field_out.caretPosition = 3
                self.session.findById("wnd[0]").sendVKey(2)
                typeOperation = "CF07"

            self.session.findById("wnd[0]/tbar[1]/btn[14]").press()
            self.session.findById("wnd[0]/usr/tblSAPDV70ATC_NAST3/ctxtDNAST-KSCHL[1,7]").text = typeOperation
            self.session.findById("wnd[0]/usr/tblSAPDV70ATC_NAST3/ctxtNAST-SPRAS[2,7]").text = "ES"
            self.session.findById("wnd[0]/usr/tblSAPDV70ATC_NAST3/ctxtNAST-SPRAS[2,7]").setFocus()
            self.session.findById("wnd[0]/usr/tblSAPDV70ATC_NAST3/ctxtNAST-SPRAS[2,7]").caretPosition = 2
            self.session.findById("wnd[0]").sendVKey (0)
            self.session.findById("wnd[0]/tbar[1]/btn[5]").press()
            self.session.findById("wnd[0]/usr/cmbNAST-VSZTP").key = "4"
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
            self.session.findById("wnd[0]/tbar[1]/btn[2]").press()
            ##self.session.findById("wnd[0]/usr/chkNAST-DIMME").selected = True #Flag to print immediately
            self.session.findById("wnd[0]/usr/ctxtNAST-LDEST").text = "LP01"
            self.session.findById("wnd[0]/usr/txtNAST-ANZAL").text = "1"
            self.session.findById("wnd[0]/usr/cmbNAST-TDOCOVER").key = "D"
            self.session.findById("wnd[0]/usr/cmbNAST-TDOCOVER").setFocus()
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
            self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()
            #-------------------------------------------------------#

            #--------------- CHECK PRINT STATUS SP02 ---------------#
            self.session.findById("wnd[0]/tbar[0]/okcd").text = "SP02" #Transaction to check print status
            self.session.findById("wnd[0]").sendVKey(0)
            self.session.findById("wnd[0]").maximize()
            
            try:
                # Try with checkbox
                self.session.findById("wnd[0]/usr/chk[1,3]").selected = True
                self.session.findById("wnd[0]/usr/chk[1,3]").setFocus()
                
            except:
                # Try without checkbox
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = ""
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "0"

            #-------------------------------------------------------#

            entrega = row["ENTREGA"] # Name of column in excel
            nombre_pdf = f"SAP_{entrega}.pdf"
            carpeta = output_folder
            full_path = os.path.join(carpeta, nombre_pdf)

            t = threading.Thread(
            target=self.save_pdf,
            args=(full_path,),
            daemon=True
            )
            t.start()
            
            time.sleep(0.5) #Wait for thread to start

            #---------------- Select the print job ----------------#
            self.session.findById("wnd[0]/mbar/menu[0]/menu[2]/menu[2]").select()
            #---------------- Come back to main window ----------------#
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press()

    #---------- Print documents of identity ----------------
    def save_docs(self, df_print, output_folder, pdf_base):
    
        if not pdf_base or not os.path.isfile(pdf_base):
            raise FileNotFoundError("select a PDF correct")

        # Iterar sobre el DataFrame recibido
        for _, row in df_print.iterrows():
            order = row["ENTREGA"]
            new_pdf_name = f"DOC_{order}.pdf"
            new_pdf_path = os.path.join(output_folder, new_pdf_name)

            shutil.copy(pdf_base, new_pdf_path)

        return True