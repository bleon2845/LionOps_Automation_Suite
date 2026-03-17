from pathlib import Path
import pandas as pd
import time

def generate_orders_txt():
    ruta_base = Path(r"C:/temp/SAP")
    archivo_excel = ruta_base / "Archivo_Transitos.xlsx"
    archivo_txt = ruta_base / "Orders.txt"

    timeout = 60 # seconds
    start_time = time.time()

    while not archivo_excel.exists():
        if time.time() - start_time > timeout:
            raise FileNotFoundError(f"{archivo_excel} was not created after MB5T export.")
        time.sleep(1)

    df = pd.read_excel(archivo_excel)

    columna_objetivo = "Documento compras"
    if columna_objetivo not in df.columns:
        raise ValueError(f"Column '{columna_objetivo}' not found in the file.")

    ordenes = (
        df[columna_objetivo]
        .dropna()
        .astype(float)
        .astype(int)
        .astype(str)
        .str.strip()
    )

    ordenes = ordenes[ordenes != ""].drop_duplicates()

    with open(archivo_txt, "w", encoding="utf-8") as f:
        for orden in ordenes:
            f.write(f"{orden}\n")

    return str(archivo_txt), len(ordenes)

if __name__ == "__main__":
    ruta, total = generate_orders_txt()
    print(f"File generated: {ruta}")
    print(f"Unique orders: {total}")