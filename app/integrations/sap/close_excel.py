import win32com.client

def close_excel_file(file_name: str):
    try:
        excel = win32com.client.GetObject(None, "Excel.Application")
    except Exception:
        # Excel is not running
        return False

    try:
        for wb in excel.Workbooks:
            if wb.Name.lower() == file_name.lower():
                wb.Close(SaveChanges=False)
                print(f"Excel file closed: {file_name}")
                break

        # If no workbooks remain open → close Excel application
        if excel.Workbooks.Count == 0:
            excel.Quit()
            print("Excel application closed.")

        return True

    except Exception as e:
        print(f"Error closing Excel file: {e}")
        return False