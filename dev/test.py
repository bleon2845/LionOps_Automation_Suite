
#%%
import sys
from pathlib import Path

# Detecta la raíz del proyecto buscando la carpeta "services"
root = Path.cwd()
while not (root / "services").exists() and root != root.parent:
    root = root.parent

if not (root / "services").exists():
    raise RuntimeError("No se encontró la carpeta 'services' desde el directorio actual.")

sys.path.insert(0, str(root))
print("✅ Project root added:", root)

# %%

import pandas as pd
from pandas import DataFrame
from pandas import DataFrame
from services.loader import load_excel
from services.filters import filter_dataframe
from services.payroll_rules import calcular_periodos_nomina

# Cargar archivos locales
df_acumulado = load_excel("Acumulado_Mes.xlsx")
df_conso_nomina = load_excel("Conso_Nomina.xlsx")
df_prenomina = load_excel("Conso_PreNomina.xlsx")

# Calcular periodos
periodos = calcular_periodos_nomina(df_acumulado)

# Aplicar filtros
df_conso_filtrado: DataFrame = filter_dataframe(
    df_conso_nomina,
    column="MES",
    values=periodos["nombre_mes_anterior"]
)

df_prenomina_filtrado: DataFrame = filter_dataframe(
    df_prenomina,
    column="Periodo",
    values=[
        periodos["corte_nomina_1"],
        periodos["corte_nomina_2"]
    ]
)

df_prenomina_filtrado
# %%
