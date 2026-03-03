import time
from integrations.sap.sap_gui import SapGUI

class SapSession():
    def __init__(self, sap_gui: SapGUI):
        self.sap = sap_gui

    #----------- SAP Login -----------
    def login_sap(self, username, password, system_name=None, index=None):
        self.sap.open_sap()
        time.sleep(2)
        self.sap.connect_sap(system_name = system_name, index = index)

        try:
            session = self.sap.session

            session.findById("wnd[0]/usr/txtRSYST-MANDT").text = "300" #"100" #Claro # "500" #Telefonica
            session.findById("wnd[0]/usr/txtRSYST-BNAME").text = username #Add username when the code is ready
            time.sleep(2)
            session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password #Add password when the code is ready
            session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "ES" #Idioma
                
            session.findById("wnd[0]").sendVKey(0) # Send enter

            # 2) Fallback press button logon
            try:
                session.findById("wnd[0]/usr/btnLOGON", False) and \
                    session.findById("wnd[0]/usr/btnLOGON").press()
            except Exception:
                pass

            # 3) Fallback press button logon
            try:
                session.findById("wnd[0]/tbar[0]/btn[0]", False) and \
                    session.findById("wnd[0]/tbar[0]/btn[0]").press()   # "Enter" (✔)
            except Exception:
                pass

        except Exception as e:
            raise RuntimeError(f"Error durante el login: {e}") from e
        
        return True