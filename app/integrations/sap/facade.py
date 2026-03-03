from integrations.sap.create_order_MB21 import CreateOrderMB21
from integrations.sap.sap_gui import SapGUI
from integrations.sap.create_order import CreateOrder
from integrations.sap.save_docs import SaveDocs

class SapFacade:

    def __init__(self, sap_gui: SapGUI):
        self.sap = sap_gui
        self._create_order: CreateOrder | None = None
        self._save_docs_service: SaveDocs | None = None
        self._create_order_mb21: CreateOrderMB21 | None = None

    #------------ Connection and Login -------------
    def _ensure_session(self, system_name: str = None,index: int = None):
        if self.sap.session:
            return
        self.sap.open_sap()
        self.sap.connect_sap(system_name=system_name, index=index)

        if not self.sap.session:
            raise RuntimeError("unable to establish SAP session.")

    def login(self,username: str, password: str,system_name: str = None) -> bool:
        self.sap.open_sap()
        self.sap.connect_sap(system_name=system_name)
        session = self.sap.session
        if not session:
            raise RuntimeError("SAP session not available. Cannot perform login.")  
        
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = username
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        session.findById("wnd[0]").sendVKey(0)

        return True

    #------------ Create Order ME21N -------------
    def create_orders(self, excel_path: str, file_folder: str):
        self._ensure_session()
        if not self._create_order:
            self._create_order = CreateOrder(self.sap.session)

        self._create_order.create_documents(excel_path, file_folder)

    #------------ Create Order MB21 -------------
    def create_orders_MB21(self, excel_path: str, file_folder: str):
        self._ensure_session()
        if not self._create_order_mb21:
            self._create_order_mb21 = CreateOrderMB21(self.sap.session)

        self._create_order_mb21.create_documentsMB21(excel_path, file_folder)

    #------------ Save PDF MB02 SP01------------- 
    def print_documents(self, excel_path: str, output_folder: str):
        self._ensure_session()

        if not self._save_docs_service:
            self._save_docs_service = SaveDocs(self.sap.session)
            #raise RuntimeError("SaveDocs service not initialized.")

        self._save_docs_service.print_documents(excel_path, output_folder)

    #------------ Create Identity Document -------------
    def save_docs(self, df_print, output_folder, pdf_base_path):
        self._ensure_session()
        
        if not self._save_docs_service:
            self._save_docs_service = SaveDocs(self.sap.session)
        
        self._save_docs_service.save_docs(df_print, output_folder, pdf_base_path)






