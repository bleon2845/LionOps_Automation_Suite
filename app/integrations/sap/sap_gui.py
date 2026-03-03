import os
import time
import subprocess
import win32com.client


class SapGUI:
    def __init__(self):
        self.application = None
        self.connection = None
        self.session = None
        self.path = None

    #----------- SAP Connection and Login -----------
    def open_sap(self) -> None:

        try:
            sapgui = win32com.client.GetObject("SAPGUI")
            self.application = sapgui.GetScriptingEngine
            return # SAP is already open

        except Exception:
            paths = [
                r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
                r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe"
            ]

            for path in paths:
                if os.path.exists(path):
                    self.path = path
                    subprocess.Popen(path)
                    time.sleep(3)
                    break
            else:
                raise FileNotFoundError("Path SAP logon not found")

            sapgui = win32com.client.GetObject("SAPGUI")
            self.application = sapgui.GetScriptingEngine

    def connect_sap(self, system_name: str = None, index: int = None) -> None:

        try:
            sapgui = win32com.client.GetObject("SAPGUI")
        except Exception:
            raise RuntimeError("SAP GUI Scripting not available.")

        if sapgui is None:
            raise RuntimeError("SAP GUI Scripting not available.")

        app = sapgui.GetScriptingEngine
        self.application = app

        #------- Select Connection -------
        if index is not None:
            if app.Children.Count <= index:
                raise RuntimeError(
                    f"Not existing SAP connection with index {index}"
                )
            self.connection = app.Children(index)

        else:
            if app.Children.Count > 0:
                self.connection = app.Children(0)
            else:
                if not system_name:
                    raise RuntimeError(
                        "system_name is required when no connections are available."
                    )
                self.connection = app.OpenConnection(system_name, True)

        time.sleep(2)

        #------- Select Session -------
        if self.connection.Children.Count == 0:
            raise RuntimeError(
                "Not session available in the selected connection."
            )

        self.session = self.connection.Children(0)
        self.session.findById("wnd[0]").maximize()