import pandas as pd

MESES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL",
    "MAYO", "JUNIO", "JULIO", "AGOSTO",
    "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

def calcular_periodos_nomina(df_acumulado: pd.DataFrame) -> dict:
    """
    Calcula los períodos de nómina basados en el mes del acumulado.

    Retorna un diccionario con:
    - mes actual
    - mes anterior
    - mes IBC
    - cortes de nómina
    """

    if df_acumulado.empty:
        raise ValueError("df_acumulado is empty")

    # Normalizar nombre de columna
    col_mes = "MES PROCESO" if "MES PROCESO" in df_acumulado.columns else "Mes proceso"

    n_mes_actual = int(df_acumulado[col_mes].iloc[0])

    if not 1 <= n_mes_actual <= 12:
        raise ValueError(f"Invalid month number: {n_mes_actual}")

    n_mes_anterior = n_mes_actual - 1 if n_mes_actual > 1 else 12
    n_mes_ibc = n_mes_anterior - 1 if n_mes_anterior > 1 else 12

    nombre_mes_actual = MESES[n_mes_actual - 1]
    nombre_mes_anterior = MESES[n_mes_anterior - 1]
    nombre_mes_ibc = MESES[n_mes_ibc - 1]

    return {
        "n_mes_actual": n_mes_actual,
        "n_mes_anterior": n_mes_anterior,
        "nombre_mes_actual": nombre_mes_actual,
        "nombre_mes_anterior": nombre_mes_anterior,
        "nombre_mes_ibc": nombre_mes_ibc,
        "corte_nomina_1": f"1Q {nombre_mes_anterior}",
        "corte_nomina_2": f"2Q {nombre_mes_anterior}",
    }
