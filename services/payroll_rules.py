import pandas as pd
import re
import calendar
from datetime import datetime
import calendar
import numpy as np
from typing import Dict, List, Optional


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

def check_quantity_with_salary(
    df: pd.DataFrame,
    salario_umbral_ft: float,
    codigos_general: list[str],
    codigos_ft: list[str],
    dias_mes: int = 30,
    salario_col: str = "SALARIO MENSUAL",
    neto_col: str = "Neto",
    cantidad_col: str = "Cantidad",
    concepto_col: str = "Concepto",
) -> pd.DataFrame:
    """
    Crea:
      - Salario Dia = SALARIO MENSUAL / dias_mes
      - Verificacion Dias Salario = Neto / Salario Dia
    y actualiza 'Cantidad' cuando aplica:
      - Para codigos_general: si verificacion>0, salario>0 y cantidad != verificacion.
      - Para codigos_ft: si verificacion>0, salario > salario_umbral_ft y cantidad != verificacion.
    """

    if df.empty:
        return df

    required = [salario_col, neto_col, cantidad_col, concepto_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()

    # Evitar divisiones raras / strings
    out[salario_col] = pd.to_numeric(out[salario_col], errors="coerce")
    out[neto_col] = pd.to_numeric(out[neto_col], errors="coerce")
    out[cantidad_col] = pd.to_numeric(out[cantidad_col], errors="coerce")

    out["Salario Dia"] = out[salario_col] / float(dias_mes)
    out["Verificacion Dias Salario"] = out[neto_col] / out["Salario Dia"]

    # --- Reglas general ---
    mask_cod_gen = out[concepto_col].astype(str).isin(codigos_general)
    mask_update_gen = (
        mask_cod_gen
        & (out["Verificacion Dias Salario"] > 0)
        & (out[salario_col] > 0)
        & (out[cantidad_col] != out["Verificacion Dias Salario"])
    )
    out.loc[mask_update_gen, cantidad_col] = out.loc[mask_update_gen, "Verificacion Dias Salario"]

    # --- Reglas FT ---
    mask_cod_ft = out[concepto_col].astype(str).isin(codigos_ft)
    mask_update_ft = (
        mask_cod_ft
        & (out["Verificacion Dias Salario"] > 0)
        & (out[salario_col] > float(salario_umbral_ft))
        & (out[cantidad_col] != out["Verificacion Dias Salario"])
    )
    out.loc[mask_update_ft, cantidad_col] = out.loc[mask_update_ft, "Verificacion Dias Salario"]

    return out

def calculate_for_concept(
    df: pd.DataFrame,
    diccionario: dict,
    columna_filtro: str,
    columna_valor: str,
    group_col: str,
    asignar_primera_fila: bool = True
) -> pd.DataFrame:
    """
    Calcula días por concepto de nómina agrupados por NUMERO DOCUMENTO.

    diccionario: {
        "SUELDO BASICO": "DIAS_SUELDO_BASICO",
        ...
    }

    Si asignar_primera_fila=True:
        Los valores solo quedan en la primera fila del documento.
    """

    if df.empty:
        return df

    required = [group_col, columna_filtro, columna_valor]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()

    # Asegurar numérico
    out[columna_valor] = pd.to_numeric(out[columna_valor], errors="coerce").fillna(0)

    # Filtrar solo conceptos del diccionario
    base = out[out[columna_filtro].isin(diccionario.keys())]

    # Agrupar y sumar
    sums = (
        base
        .groupby([group_col, columna_filtro], dropna=False)[columna_valor]
        .sum()
        .reset_index()
    )

    # Mapear a nombres finales
    sums["__col__"] = sums[columna_filtro].map(diccionario)

    # Pivotear
    pivot = (
        sums.pivot_table(
            index=group_col,
            columns="__col__",
            values=columna_valor,
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # Redondear y convertir a int
    for col in diccionario.values():
        if col not in pivot.columns:
            pivot[col] = 0
        pivot[col] = pivot[col].round().astype(int)

    # Merge al DF original
    out = out.merge(pivot, on=group_col, how="left")

    # Asignar solo a la primera fila por documento
    if asignar_primera_fila:
        first_row = out.groupby(group_col).cumcount().eq(0)
        for col in diccionario.values():
            out.loc[~first_row, col] = None

    return out

def pivot_sum(
    df: pd.DataFrame,
    index_cols: list[str],
    value_col: str,
    output_col: str | None = None
) -> pd.DataFrame:
    """
    Agrupa y suma value_col por index_cols (equivalente a tu pivot_table con sum).
    """
    if df.empty:
        return df

    missing = [c for c in index_cols + [value_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    out = df.copy()
    out[value_col] = pd.to_numeric(out[value_col], errors="coerce").fillna(0)

    grouped = (
        out.groupby(index_cols, dropna=False)[value_col]
        .sum()
        .reset_index()
    )

    if output_col and output_col != value_col:
        grouped = grouped.rename(columns={value_col: output_col})

    return grouped

def total_by_group_first_row(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    target_col: str,
    fill_other_rows=0
) -> pd.DataFrame:
    """
    Crea un total por grupo y lo asigna SOLO en la primera fila del grupo.
    El resto queda en 0 (o el valor que definas).
    """
    if df.empty:
        return df

    for c in [group_col, value_col]:
        if c not in df.columns:
            raise ValueError(f"Column '{c}' not found in DataFrame")

    out = df.copy()
    total = out.groupby(group_col)[value_col].transform("sum")
    first = ~out.duplicated(subset=group_col)
    out[target_col] = total.where(first, fill_other_rows)
    return out


MONTHS_NAME_TO_NUM = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

def _parse_mes_to_int(mes_value) -> int | None:
    """Convierte MES a número 1-12. Acepta nombre o número."""
    if pd.isna(mes_value):
        return None

    # Si ya es número (int/float)
    if isinstance(mes_value, (int, float)):
        m = int(mes_value)
        return m if 1 <= m <= 12 else None

    s = str(mes_value).strip().upper()

    # Si es string numérico
    if s.isdigit():
        m = int(s)
        return m if 1 <= m <= 12 else None

    # Si contiene el nombre del mes dentro del texto
    for nombre, num in MONTHS_NAME_TO_NUM.items():
        if nombre in s:
            return num

    return None

def _date_start_month(mes_value, anio: int) -> pd.Timestamp:
    m = _parse_mes_to_int(mes_value)
    if not m:
        return pd.NaT
    return pd.Timestamp(year=int(anio), month=int(m), day=1)

def _date_end_month(mes_value, anio: int) -> pd.Timestamp:
    m = _parse_mes_to_int(mes_value)
    if not m:
        return pd.NaT
    ultimo = calendar.monthrange(int(anio), int(m))[1]
    return pd.Timestamp(year=int(anio), month=int(m), day=int(ultimo))

def get_days_month(nombre_mes: str, anio: int) -> int:
    """Retorna número de días del mes dado (nombre en español)."""
    if not isinstance(nombre_mes, str):
        raise ValueError("nombre_mes must be a string")

    mes_num = MONTHS_NAME_TO_NUM.get(nombre_mes.strip().upper())
    if not mes_num:
        raise ValueError(f"Nombre de mes no válido: {nombre_mes}")

    return calendar.monthrange(int(anio), int(mes_num))[1]

def config_days_month_rules(dias_mes: int, *, base: int = 30) -> int:
    """
    Reglas que aplicabas:
    - Si febrero < 30 => 30
    - Si mes = 31 => 30
    """
    if dias_mes < base:
        return base
    if dias_mes == 31:
        return base
    return dias_mes

def execute_analysis_days_payroll(
    df: pd.DataFrame,
    nombre_mes_actual: str,
    nombre_mes_anterior: str,
    anio: int,
    salario_ft_umbral: float,
    dias_mes_base: int,
    *,
    col_mes: str = "MES",
    col_salario_mensual: str = "SALARIO MENSUAL",
    col_salario_pagar: str = "SALARIO_A_PAGAR",
    col_dias_pago: str = "DIAS_PAGO_NOMINA",
    col_fecha_ingreso: str = "FECHA DE INGRESO",
    col_fecha_baja: str = "FECHA DE BAJA",
    col_estatus: str = "ESTATUS_DIAS",
    col_obs: str = "OBSERVACION",
) -> pd.DataFrame:
    """
    Aplica todas las reglas del bloque:
    - Calcula días mes actual/anterior (con reglas 30)
    - Ajusta DIAS_PAGO_NOMINA cuando salario mensual = salario a pagar
    - Normaliza fechas (fillna, conversion)
    - Calcula DIAS_TRABAJADOS
    - Setea ESTATUS_DIAS/OBSERVACION con varias reglas
    - Calcula FECHA_INICIO_MES, FECHA_FIN_MES, DIFERENCIA_DIAS y valida ingresos/retiros en el mes
    """

    if df.empty:
        return df

    out = df.copy()

    # --------- Días mes actual/anterior ----------
    dias_mes_actual = config_days_month_rules(get_days_month(nombre_mes_actual, anio), base=dias_mes_base)
    dias_mes_anterior = config_days_month_rules(get_days_month(nombre_mes_anterior, anio), base=dias_mes_base)

    # (dias_mes_anterior lo calculas por si lo usas después; aquí queda disponible)
    _ = dias_mes_anterior

    # --------- Asegurar columnas base ----------
    for c in [col_salario_mensual, col_salario_pagar, col_dias_pago]:
        if c not in out.columns:
            raise ValueError(f"Missing required column: {c}")

    # Asegurar numéricos
    out[col_salario_mensual] = pd.to_numeric(out[col_salario_mensual], errors="coerce")
    out[col_salario_pagar] = pd.to_numeric(out[col_salario_pagar], errors="coerce")
    out[col_dias_pago] = pd.to_numeric(out[col_dias_pago], errors="coerce")

    # --------- Regla: si salario mensual = salario a pagar -> dias mes actual ----------
    mask_salario_igual = out[col_salario_mensual] == out[col_salario_pagar]
    out.loc[mask_salario_igual, col_dias_pago] = dias_mes_actual

    # --------- Normalizar fechas ----------
    if col_fecha_ingreso not in out.columns or col_fecha_baja not in out.columns:
        raise ValueError(f"Missing date columns: '{col_fecha_ingreso}' or '{col_fecha_baja}'")

    ts_base = pd.Timestamp("1900-01-01 00:00:00")

    out[col_fecha_ingreso] = out[col_fecha_ingreso].fillna(ts_base)
    out[col_fecha_baja] = out[col_fecha_baja].fillna(ts_base)

    # tu caso raro: FECHA DE BAJA == 1
    out.loc[out[col_fecha_baja] == 1, col_fecha_baja] = ts_base

    out[col_fecha_ingreso] = pd.to_datetime(out[col_fecha_ingreso], errors="coerce")
    out[col_fecha_baja] = pd.to_datetime(out[col_fecha_baja], errors="coerce")

    # --------- DIAS_TRABAJADOS ----------
    out["DIAS_TRABAJADOS"] = (out[col_fecha_baja] - out[col_fecha_ingreso]).dt.days

    # --------- ESTATUS/OBSERVACION init ----------
    if col_estatus not in out.columns:
        out[col_estatus] = "VALIDAR"
    else:
        out[col_estatus] = out[col_estatus].fillna("VALIDAR")

    if col_obs not in out.columns:
        out[col_obs] = None

    # --------- Regla: diferencia de $1 ----------
    mask_diff_1 = (
        (out[col_estatus] == "VALIDAR")
        & (out[col_salario_mensual].notna())
        & (out[col_salario_pagar].notna())
        & ((out[col_salario_mensual] - out[col_salario_pagar]).abs() == 1)
    )
    out.loc[mask_diff_1, col_estatus] = "OK"
    out.loc[mask_diff_1, col_obs] = "Dias Laborados = Dias a Pagar (con diferencia de $1)"

    # --------- Regla: dias trabajados == dias pago ----------
    mask_dias_igual = out["DIAS_TRABAJADOS"] == out[col_dias_pago]
    out.loc[mask_dias_igual, col_estatus] = "OK"
    out.loc[mask_dias_igual, col_obs] = "Dias Laborados = Dias a Pagar"

    # --------- Regla: salario mensual = salario a pagar ----------
    out.loc[mask_salario_igual, col_estatus] = "OK"
    out.loc[mask_salario_igual, col_obs] = "Salario Mensual = Salario a Pagar"

    # --------- Regla: dias pago = dias mes actual (30) ----------
    mask_30 = out[col_dias_pago] == dias_mes_actual
    out.loc[mask_30, col_estatus] = "OK"
    out.loc[mask_30, col_obs] = "30 Dias Trabajados"

    # --------- Redondeo dias pago para FT ----------
    mask_ft = out[col_salario_mensual] > float(salario_ft_umbral)
    out.loc[mask_ft, col_dias_pago] = out.loc[mask_ft, col_dias_pago].round()

    # Reaplicar regla 30 (tu script lo repite)
    mask_30 = out[col_dias_pago] == dias_mes_actual
    out.loc[mask_30, col_estatus] = "OK"
    out.loc[mask_30, col_obs] = "30 Dias Trabajados"

    # --------- ANALISIS POR FECHA INICIO/FIN MES ----------
    # FECHA_INICIO_MES según MES (col_mes)
    if col_mes not in out.columns:
        raise ValueError(f"Missing column: {col_mes}")

    out["FECHA_INICIO_MES"] = out[col_mes].apply(lambda x: _date_start_month(x, anio))
    out["FECHA_FIN_MES"] = out[col_mes].apply(lambda x: _date_end_month(x, anio))

    # DIFERENCIA_DIAS = baja - inicio_mes + 1
    out["DIFERENCIA_DIAS"] = (out[col_fecha_baja] - out["FECHA_INICIO_MES"]).dt.days + 1

    # Retiro en mismo mes (validar)
    mask_retiro_mismo_mes = (
        (out[col_estatus] == "VALIDAR")
        & (out["DIFERENCIA_DIAS"] == out[col_dias_pago])
    )
    out.loc[mask_retiro_mismo_mes, col_estatus] = "OK"
    out.loc[mask_retiro_mismo_mes, col_obs] = "Empleado con Retiro en Mismo Mes"

    # Ingreso en el mismo mes: recalcular DIFERENCIA_DIAS usando FECHA_FIN_MES ya calculada
    mask_ingreso_mismo_mes = out["FECHA_INICIO_MES"] < out[col_fecha_ingreso]

    out.loc[mask_ingreso_mismo_mes, "DIFERENCIA_DIAS"] = (
        (out.loc[mask_ingreso_mismo_mes, "FECHA_FIN_MES"] - out.loc[mask_ingreso_mismo_mes, col_fecha_ingreso]).dt.days
    )

    mask_ok_ingreso = (
        (out[col_estatus] == "VALIDAR")
        & (out["DIFERENCIA_DIAS"] == out[col_dias_pago])
    )
    out.loc[mask_ok_ingreso, col_estatus] = "OK"
    out.loc[mask_ok_ingreso, col_obs] = "Empleado con Ingreso en Mismo Mes"

    # ahora con +1
    out.loc[mask_ingreso_mismo_mes, "DIFERENCIA_DIAS"] = (
        (out.loc[mask_ingreso_mismo_mes, "FECHA_FIN_MES"] - out.loc[mask_ingreso_mismo_mes, col_fecha_ingreso]).dt.days + 1
    )

    mask_ok_ingreso = (
        (out[col_estatus] == "VALIDAR")
        & (out["DIFERENCIA_DIAS"] == out[col_dias_pago])
    )
    out.loc[mask_ok_ingreso, col_estatus] = "OK"
    out.loc[mask_ok_ingreso, col_obs] = "Empleado con Ingreso en Mismo Mes"

    # Ingreso y retiro en mismo mes
    mask_ingreso_retiro = (
        (out["FECHA_INICIO_MES"] < out[col_fecha_ingreso])
        & (out["FECHA_FIN_MES"] > out[col_fecha_baja])
    )
    out.loc[mask_ingreso_retiro, "DIFERENCIA_DIAS"] = (
        (out.loc[mask_ingreso_retiro, col_fecha_baja] - out.loc[mask_ingreso_retiro, col_fecha_ingreso]).dt.days + 1
    )

    mask_ok_ingreso_retiro = (
        (out[col_estatus] == "VALIDAR")
        & (out["DIFERENCIA_DIAS"] == out[col_dias_pago])
    )
    out.loc[mask_ok_ingreso_retiro, col_estatus] = "OK"
    out.loc[mask_ok_ingreso_retiro, col_obs] = "Empleado con Ingreso y Retiro en Mismo Mes"

    # Cambiar FECHA BAJA base 1900 -> 1990 (tu script)
    out.loc[out[col_fecha_baja] == pd.Timestamp("1900-01-01"), col_fecha_baja] = pd.Timestamp("1990-01-01")

    # Rellenar FECHA_FIN_MES con primer valor no nulo (tu script)
    non_na_fin = out["FECHA_FIN_MES"].dropna()
    if not non_na_fin.empty:
        primer_valor = non_na_fin.iloc[0]
        out["FECHA_FIN_MES"] = out["FECHA_FIN_MES"].fillna(primer_valor)

    # Validar retiro cuando no concuerda
    # Nota: tu script compara fecha con string "1990-01-01 00:00:00".
    # Aquí lo hacemos como Timestamp para evitar errores.
    mask_validar_retiro = (
        (out[col_estatus] == "VALIDAR")
        & (out["DIFERENCIA_DIAS"] != out[col_dias_pago])
        & (out[col_fecha_baja] != pd.Timestamp("1990-01-01"))
        & (out["FECHA_FIN_MES"] > out[col_fecha_baja])
    )
    out.loc[mask_validar_retiro, col_estatus] = "VALIDAR"
    out.loc[mask_validar_retiro, col_obs] = "Validar Retiro"

    return out


_WEEKDAY_ES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}

def weekday_name_es_from_datetime(series: pd.Series) -> pd.Series:
    """
    Retorna nombre del día en español SIN depender del locale del sistema.
    (evita errores con dt.day_name(locale="es_ES") en Windows/servidores)
    """
    s = pd.to_datetime(series, errors="coerce")
    return s.dt.dayofweek.map(_WEEKDAY_ES)

def validate_offboarding_weekdays(
    df: pd.DataFrame,
    *,
    empresa_value: str = "SUPPLA S.A",
    col_empresa: str = "EMPRESA",
    col_fecha_baja: str = "FECHA DE BAJA",
    col_estatus: str = "ESTATUS_DIAS",
    col_obs: str = "OBSERVACION",
    col_dif: str = "DIFERENCIA_DIAS",
    col_dias_pago: str = "DIAS_PAGO_NOMINA",
    col_no_lab: str = "DIAS_DÍA_NO_LAB_DER_A_PAG",
    col_dto: str = "DIAS_DTO_SALARIO",
    col_dayname: str = "DIA SEMANA RETIRO",
) -> pd.DataFrame:
    """
    Reglas:
    - Si retiro es Viernes y está en Validar Retiro -> suma 2 días a DIFERENCIA_DIAS
    - Si retiro es Sábado  y está en Validar Retiro -> suma 1 día a DIFERENCIA_DIAS
    - Luego valida si cuadra con DIAS_PAGO_NOMINA
    - Luego valida casos con DIAS NO LABORALES y/o DIAS DTO SALARIO
    """
    if df.empty:
        return df

    out = df.copy()

    # Asegurar columnas
    required = [col_fecha_baja, col_estatus, col_obs, col_empresa, col_dif, col_dias_pago]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns for validate_retiros_weekdays: {missing}")

    # Asegurar numéricos donde aplica
    out[col_dif] = pd.to_numeric(out[col_dif], errors="coerce")
    out[col_dias_pago] = pd.to_numeric(out[col_dias_pago], errors="coerce")

    if col_no_lab not in out.columns:
        out[col_no_lab] = 0
    if col_dto not in out.columns:
        out[col_dto] = 0

    out[col_no_lab] = pd.to_numeric(out[col_no_lab], errors="coerce").fillna(0)
    out[col_dto] = pd.to_numeric(out[col_dto], errors="coerce").fillna(0)

    # Día semana retiro (sin locale)
    out[col_dayname] = weekday_name_es_from_datetime(out[col_fecha_baja])

    base_mask = (
        (out[col_estatus] == "VALIDAR")
        & (out[col_obs] == "Validar Retiro")
        & (out[col_empresa] == empresa_value)
    )

    # ---- Friday: +2
    mask_viernes = base_mask & (out[col_dayname] == "Viernes")
    out.loc[mask_viernes, col_dif] = out.loc[mask_viernes, col_dif] + 2

    # Si con el ajuste ya cuadra
    mask_ok_viernes = mask_viernes & (out[col_dif] == out[col_dias_pago])
    out.loc[mask_ok_viernes, col_estatus] = "OK"
    out.loc[mask_ok_viernes, col_obs] = "Empleado con Retiro en Mismo Mes"

    # ---- Saturday: +1
    mask_sabado = base_mask & (out[col_dayname] == "Sábado")
    out.loc[mask_sabado, col_dif] = out.loc[mask_sabado, col_dif] + 1

    mask_ok_sabado = mask_sabado & (out[col_dif] == out[col_dias_pago])
    out.loc[mask_ok_sabado, col_estatus] = "OK"
    out.loc[mask_ok_sabado, col_obs] = "Empleado con Retiro en Mismo Mes"

    # ---- Validaciones con NO LABORALES / DTO (aplican para los que siguen VALIDAR + Validar Retiro)
    still_mask = base_mask & (out[col_estatus] == "VALIDAR")  # base + aún validar

    # Caso 1: tiene no laborales >0 y (dias_pago - dto) == diferencia
    mask_no_lab = (
        still_mask
        & (out[col_no_lab] > 0)
        & ((out[col_dias_pago] - out[col_dto]) == out[col_dif])
    )
    out.loc[mask_no_lab, col_estatus] = "OK"
    out.loc[mask_no_lab, col_obs] = (
        out.loc[mask_no_lab, col_no_lab].round().astype(int).astype(str)
        + " Dias No Laborales "
        + out.loc[mask_no_lab, col_dto].round().astype(int).astype(str)
        + " Dias Dcto"
    )

    # Caso 2: (dias_pago - dto) == diferencia (sin exigir no_lab > 0)
    mask_dto = (
        still_mask
        & ((out[col_dias_pago] - out[col_dto]) == out[col_dif])
    )
    out.loc[mask_dto, col_estatus] = "OK"
    out.loc[mask_dto, col_obs] = (
        out.loc[mask_dto, col_dias_pago].round().astype(int).astype(str)
        + " Dias Trabajados "
        + out.loc[mask_dto, col_dto].round().astype(int).astype(str)
        + " Dias Dcto"
    )

    return out

def validate_vinculation_change(
    df: pd.DataFrame,
    dias_mes_actual: int,
    *,
    group_col: str = "NUMERO DOCUMENTO",
    col_tipo: str = "TIPO_DE_VINCULACIÓN",
    col_dias_pago: str = "DIAS_PAGO_NOMINA",
    col_estatus: str = "ESTATUS_DIAS",
    col_obs: str = "OBSERVACION",
) -> pd.DataFrame:
    """
    Si un documento tiene exactamente 2 filas y el tipo de vinculación es {DIRECTO, TEMPORAL}
    y la suma DIAS_PAGO_NOMINA == dias_mes_actual, marca ambos OK con observación.
    """
    if df.empty:
        return df

    out = df.copy()

    required = [group_col, col_tipo, col_dias_pago]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns for validate_vinculation_change: {missing}")

    # asegurar columnas destino
    if col_estatus not in out.columns:
        out[col_estatus] = "VALIDAR"
    if col_obs not in out.columns:
        out[col_obs] = None

    out[col_dias_pago] = pd.to_numeric(out[col_dias_pago], errors="coerce").fillna(0)

    def _apply_group(grupo: pd.DataFrame) -> pd.DataFrame:
        if len(grupo) != 2:
            return grupo

        tipos = set(grupo[col_tipo].astype(str))
        if tipos != {"DIRECTO", "TEMPORAL"}:
            return grupo

        if float(grupo[col_dias_pago].sum()) != float(dias_mes_actual):
            return grupo

        grupo_ordenado = grupo.sort_values(col_tipo)
        fila1 = grupo_ordenado.iloc[0]
        fila2 = grupo_ordenado.iloc[1]

        observacion = (
            f'{int(round(fila1[col_dias_pago]))} Dias Trabajados en {fila1[col_tipo]} '
            f'{int(round(fila2[col_dias_pago]))} Dias Trabajados en {fila2[col_tipo]}'
        )
        grupo.loc[:, col_estatus] = "OK"
        grupo.loc[:, col_obs] = observacion
        return grupo

    # group_keys=False para evitar multiindex
    out = out.groupby(group_col, group_keys=False).apply(_apply_group)
    out = out.reset_index(drop=True)
    return out

def validate_salary_role_previous_month(
    df_acumulado: pd.DataFrame,
    df_consoNomina: pd.DataFrame,
    *,
    col_doc_acu: str = "NUMERO DOCUMENTO",
    col_doc_prev: str = "CEDULA",
    col_cargo_acu: str = "CARGO NOMINA",
    col_cargo_prev: str = "CARGO NOMINA",
    col_salario_acu: str = "SALARIO MENSUAL",
    col_salario_prev: str = "SALARIO BASICO",
    output_col: str = "VALIDACION SALARIO Y CARGO",
) -> pd.DataFrame:
    """
    Hace merge con nómina mes anterior y crea la columna:
    - "Salario y Cargo del Mes Anterior es Igual" si cargo y salario coinciden
    - "Salario o Cargo del Mes Anterior Diferentes" si no
    """
    if df_acumulado.empty:
        return df_acumulado

    out = df_acumulado.copy()
    prev = df_consoNomina.copy()

    # drop duplicates en prev (usualmente por CEDULA)
    if col_doc_prev in prev.columns:
        prev = prev.drop_duplicates(subset=[col_doc_prev], keep="first")

    # evitar problema si col_doc_acu está en índice
    if col_doc_acu not in out.columns and col_doc_acu in getattr(out.index, "names", []):
        out = out.reset_index()

    # merge (left)
    out = pd.merge(
        out,
        prev,
        how="left",
        left_on=col_doc_acu,
        right_on=col_doc_prev,
        suffixes=("_x", "_y"),
    )

    # nombres reales después del merge (por suffixes)
    cargo_x = f"{col_cargo_acu}_x" if f"{col_cargo_acu}_x" in out.columns else col_cargo_acu
    cargo_y = f"{col_cargo_prev}_y" if f"{col_cargo_prev}_y" in out.columns else col_cargo_prev
    sal_prev = col_salario_prev if col_salario_prev in out.columns else f"{col_salario_prev}_y"

    # numéricos
    out[col_salario_acu] = pd.to_numeric(out[col_salario_acu], errors="coerce")
    if sal_prev in out.columns:
        out[sal_prev] = pd.to_numeric(out[sal_prev], errors="coerce")

    cond_ok = (out[cargo_x] == out[cargo_y]) & (out[col_salario_acu] == out[sal_prev])

    out[output_col] = np.where(
        cond_ok,
        "Salario y Cargo del Mes Anterior es Igual",
        "Salario o Cargo del Mes Anterior Diferentes",
    )

    return out

def _ensure_int_abs_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Asegura:
    - columnas existen (si no, se crean en 0)
    - fillna(0)
    - abs()
    - int
    """
    out = df.copy()
    for c in cols:
        if c not in out.columns:
            out[c] = 0
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).abs().round().astype(int)
    return out

def _build_observations(df_mask: pd.DataFrame, mapping: Dict[str, str], col_dias_pago: str) -> pd.Series:
    """
    Construye observaciones para las filas en df_mask:
    - Siempre incluye "{DIAS_PAGO_NOMINA} Días trabajados"
    - Agrega "{col} texto" para cada col>0 del mapping
    """
    # Base: dias trabajados
    dias = pd.to_numeric(df_mask.get(col_dias_pago), errors="coerce").fillna(0).round().astype(int)
    obs = dias.astype(str) + " Días trabajados"

    # Agregar partes por cada columna >0
    for col, texto in mapping.items():
        if col not in df_mask.columns:
            continue
        vals = pd.to_numeric(df_mask[col], errors="coerce").fillna(0).round().astype(int)
        add = np.where(vals > 0, "; " + vals.astype(str) + " " + str(texto), "")
        obs = obs + add

    return obs

def validate_days_by_novedades(
    df: pd.DataFrame,
    *,
    dias_mes_actual: int,
    empresa_value: str = "SUPPLA S.A",
    cols_sum: Optional[List[str]] = None,
    obs_mapping: Optional[Dict[str, str]] = None,
    # columnas clave
    col_empresa: str = "EMPRESA",
    col_estatus: str = "ESTATUS_DIAS",
    col_obs: str = "OBSERVACION",
    col_total: str = "TOTAL_SUMA_DIAS",
    col_dias_pago: str = "DIAS_PAGO_NOMINA",
    col_fecha_inicio_mes: str = "FECHA_INICIO_MES",
    col_fecha_baja: str = "FECHA DE BAJA",
    # columnas usadas en reglas (si no existen se crean en 0)
    col_rtegro: str = "DIAS_RTEGRO_DTO_INASISTEN",
    col_vac: str = "DIAS_VACACIONES",
    col_gasto_incap: str = "DIAS_GASTO_INCAPACIDAD",
    col_sueldo_basico: str = "DIAS_SUELDO_BASICO",
    col_inasistencia: str = "DIAS_INASISTENCIA_INJUST",
    col_incap_gen: str = "DIAS_INCAP_ENFERMEDAD_GEN",
    col_sancion: str = "DIAS_SANCION_/_SUSPENSION",
    col_dto_salario: str = "DIAS_DTO_SALARIO",
    col_no_lab: str = "DIAS_DÍA_NO_LAB_DER_A_PAG",
    col_may_valor_sal: str = "MAY._VALOR_PAGADO_EN_SALARIO",
    col_salario_pagar: str = "SALARIO_A_PAGAR",
) -> pd.DataFrame:
    """
    - Normaliza columnas de días (abs, fillna, int)
    - Calcula TOTAL_SUMA_DIAS = suma(cols_sum)
    - Aplica reglas para marcar ESTATUS_DIAS=OK y construir OBSERVACION

    NOTA: Esta función reemplaza:
    - tu bloque de TOTAL_SUMA_DIAS
    - construir_observacion
    - aplicar_reglas
    """
    if df.empty:
        return df

    out = df.copy()

    # Defaults (lista de columnas para sumar)
    if cols_sum is None:
        cols_sum = [
            "DIAS_SUELDO_BASICO",
            "DIAS_FAMILIAR",
            "DIAS_PERMISO_JUSTIFICADO",
            "DIAS_SANCION_/_SUSPENSION",
            "DIAS_LICENCIA_NO_REMUN",
            "DIAS_INASISTENCIA_INJUST",
            "DIAS_VACACIONES",
            "DIAS_GASTO_INCAPACIDAD",
            "DIAS_LIC_LEY_MARIA_8_DIAS",
            "DIAS_INCAPACIDAD_ACC_TRAB",
            "DIAS_INCAP_ENFERMEDAD_GEN",
            "DIAS_LICENCIA_MATERNIDAD",
            "DIAS_VAC_HABILES_SAL_INT",
            "DIAS_INCAPACIDAD_AL_50%",
            "DIAS_DÍA_NO_LAB_DER_A_PAG",
            "DIAS_RTEGRO_DTO_INASISTEN",
            "DIAS_AJS_LICENCIA_MATERN",
            "DIAS_INCAP_ENF_GEN_PRORR",
            "DIAS_VACACIONES_FESTIVAS",
            "DIAS_DTO_SALARIO",
            "DIAS_INASIS_X_INC_>_180_D",
            "DIAS_DTO_INC_ENF_GRAL_AL",
            "DIAS_RETROACTIV_SALARIO",
            "DIAS_PERMISO_PERSONAL",
            "DIAS_AJUS_SALARIO",
        ]

    # Defaults (diccionario para observación)
    if obs_mapping is None:
        obs_mapping = {
            "DIAS_SANCION_/_SUSPENSION": "Dias Sancion",
            "DIAS_PERMISO_PERSONAL": "Dias Permiso Personal",
            "DIAS_PERMISO_JUSTIFICADO": "Dias Permiso Justificado",
            "DIAS_FAMILIAR": "Dia Familiar",
            "DIAS_LICENCIA_NO_REMUN": "Dias Licencia No Remunerada",
            "DIAS_INASISTENCIA_INJUST": "Dias Inasistencia",
            "DIAS_VACACIONES": "Dias Vacaciones",
            # OJO: si esta columna no existe en tu flujo la dejamos, no rompe:
            "DIAS_VACACIONES_DINERO": "Dias Vacaciones en Dinero",
            "DIAS_GASTO_INCAPACIDAD": "Dias Gasto Incapacidad",
            "DIAS_LIC_LEY_MARIA_8_DIAS": "Dias Lic Ley Maria",
            "DIAS_INCAPACIDAD_ACC_TRAB": "Dias Incapacidad Acc Trab",
            "DIAS_INCAP_ENFERMEDAD_GEN": "Dias Incap Enfermedad General",
            "DIAS_LICENCIA_MATERNIDAD": "Dias Licencia Maternidad",
            "DIAS_VAC_HABILES_SAL_INT": "Dias Vac Habiles Sal Int",
            "DIAS_INCAPACIDAD_AL_50%": "Dias Incapacidad",
            "DIAS_DÍA_NO_LAB_DER_A_PAG": "Dias Día No Lab Der A Pag",
            "DIAS_RTEGRO_DTO_INASISTEN": "Dias Rtegro Dto Inasistencia",
            "DIAS_AJS_LICENCIA_MATERN": "Dias Ajs Licencia Matern",
            "DIAS_INCAP_ENF_GEN_PRORR": "Dias Incap Enf Gen Prorr",
            "DIAS_VACACIONES_FESTIVAS": "Dias Vacaciones Festivas",
            "DIAS_DTO_SALARIO": "Dias Dto Salario",
            "DIAS_INASIS_X_INC_>_180_D": "Dias Inasis X Inc >180 D",
            "DIAS_DTO_INC_ENF_GRAL_AL": "Dias Dto Inc Enf Gral",
            "DIAS_RETROACTIV_SALARIO": "Dias Retroactivo Salario",
            "DIAS_AJUS_SALARIO": "Dias Ajuste Salario",
        }

    # Asegurar columnas clave
    for c in [col_estatus, col_obs, col_empresa]:
        if c not in out.columns:
            out[c] = None

    # Normalizar estatus/obs
    out[col_estatus] = out[col_estatus].fillna("VALIDAR")
    out[col_obs] = out[col_obs].fillna("")

    # Normalizar columnas numéricas que se usan en reglas
    cols_needed_for_rules = list(set(cols_sum + [
        col_dias_pago, col_rtegro, col_vac, col_gasto_incap, col_sueldo_basico,
        col_inasistencia, col_incap_gen, col_sancion, col_dto_salario, col_no_lab,
    ]))
    out = _ensure_int_abs_cols(out, cols_needed_for_rules)

    # Columna MAY._VALOR_PAGADO_EN_SALARIO puede ser decimal -> numeric abs (no necesariamente int)
    if col_may_valor_sal not in out.columns:
        out[col_may_valor_sal] = 0
    out[col_may_valor_sal] = pd.to_numeric(out[col_may_valor_sal], errors="coerce").fillna(0)

    # SALARIO_A_PAGAR puede ser decimal -> numeric
    if col_salario_pagar not in out.columns:
        out[col_salario_pagar] = 0
    out[col_salario_pagar] = pd.to_numeric(out[col_salario_pagar], errors="coerce").fillna(0)

    # Asegurar fechas necesarias en algunas reglas
    if col_fecha_inicio_mes in out.columns:
        out[col_fecha_inicio_mes] = pd.to_datetime(out[col_fecha_inicio_mes], errors="coerce")
    if col_fecha_baja in out.columns:
        out[col_fecha_baja] = pd.to_datetime(out[col_fecha_baja], errors="coerce")

    # TOTAL_SUMA_DIAS
    out[col_total] = out[cols_sum].sum(axis=1)

    # Base para aplicar reglas solo a SUPPLA y estatus VALIDAR
    base = (out[col_estatus] == "VALIDAR") & (out[col_empresa] == empresa_value)

    # Solo permitimos “clasificar” si OBSERVACION está vacía o es Validar Retiro
    sin_clasificar = (out[col_obs].isin(["", "Validar Retiro"])) | (out[col_obs].isna())

    def _apply_rule(mask: pd.Series, *, custom_text: Optional[str] = None) -> None:
        """Aplica OBS y ESTATUS a las filas mask."""
        final_mask = mask & sin_clasificar
        if final_mask.any():
            if custom_text is not None:
                out.loc[final_mask, col_obs] = custom_text
            else:
                out.loc[final_mask, col_obs] = _build_observations(out.loc[final_mask], obs_mapping, col_dias_pago)
            out.loc[final_mask, col_estatus] = "OK"

    # ------------------- REGLAS (equivalentes a tus reglas) -------------------

    # 1) TOTAL_SUMA_DIAS == dias_mes_actual
    _apply_rule(base & (out[col_total] == int(dias_mes_actual)))

    # 2) Retiro del mes anterior: FECHA_INICIO_MES > FECHA DE BAJA con obs=Validar Retiro
    if col_fecha_inicio_mes in out.columns and col_fecha_baja in out.columns:
        _apply_rule(
            base
            & (out[col_obs] == "Validar Retiro")
            & (out[col_fecha_inicio_mes].notna())
            & (out[col_fecha_baja].notna())
            & (out[col_fecha_inicio_mes] > out[col_fecha_baja])
        )

    # 3) Aplica por reintegro: (TOTAL - RTEGRO) == dias_mes_actual
    _apply_rule(base & ((out[col_total] - out[col_rtegro]) == int(dias_mes_actual)))

    # 4) Aplica por vacaciones: TOTAL>30 y DIAS_VACACIONES>0
    _apply_rule(base & (out[col_total] > 30) & (out[col_vac] > 0))

    # 5) Sueldo básico + gasto incapacidad == dias pago nómina
    _apply_rule(base & (out[col_gasto_incap] > 0) & ((out[col_sueldo_basico] + out[col_gasto_incap]) == out[col_dias_pago]))

    # 6) Dias pago + inasistencia + incap_gen == dias_mes_actual
    _apply_rule(
        base
        & ((out[col_inasistencia] > 0) | (out[col_incap_gen] > 0))
        & ((out[col_dias_pago] + out[col_inasistencia] + out[col_incap_gen]) == int(dias_mes_actual))
    )

    # 7) Dias pago - sancion == dias_mes_actual  OR  (sueldo_basico - sancion) == dias_pago
    _apply_rule(
        base
        & (out[col_sancion] > 0)
        & (
            ((out[col_dias_pago] - out[col_sancion]) == int(dias_mes_actual))
            | ((out[col_sueldo_basico] - out[col_sancion]) == out[col_dias_pago])
        )
    )

    # 8) Dias pago - incap_gen == dias_mes_actual
    _apply_rule(base & (out[col_incap_gen] > 0) & ((out[col_dias_pago] - out[col_incap_gen]) == int(dias_mes_actual)))

    # 9) Dias pago + inasistencia + sancion == dias_mes_actual
    _apply_rule(
        base
        & (out[col_inasistencia] > 0)
        & (out[col_sancion] > 0)
        & ((out[col_dias_pago] + out[col_inasistencia] + out[col_sancion]).round().astype(int) == int(dias_mes_actual))
    )

    # 10) DCTO SALARIO o MAYOR VALOR: (dias_pago - dto) == DIFERENCIA_DIAS
    if "DIFERENCIA_DIAS" in out.columns:
        out["DIFERENCIA_DIAS"] = pd.to_numeric(out["DIFERENCIA_DIAS"], errors="coerce")
        _apply_rule(
            base
            & (out[col_may_valor_sal].abs() > 0)
            & ((out[col_dias_pago] - out[col_dto_salario].round()).round().astype(int) == out["DIFERENCIA_DIAS"].round().astype(int))
        )

    # 11) DCTO + inasistencias con retiro: regla larga (solo si existe DIFERENCIA_DIAS y obs=Validar Retiro)
    if "DIFERENCIA_DIAS" in out.columns:
        _apply_rule(
            base
            & (out[col_obs] == "Validar Retiro")
            & (out[col_may_valor_sal].abs() > 0)
            & (
                (
                    (out[col_dias_pago] + out[col_no_lab])
                    - (out[col_dto_salario] + out[col_inasistencia])
                ).round().astype(int)
                == (out["DIFERENCIA_DIAS"] - out[col_inasistencia]).round().astype(int)
            )
        )

    # 12) Salida antes de iniciar mes y con dcto de pago: texto personalizado
    if col_fecha_inicio_mes in out.columns and col_fecha_baja in out.columns:
        _apply_rule(
            (out[col_estatus] == "VALIDAR")
            & (out[col_obs] == "Validar Retiro")
            & (out[col_fecha_baja].notna())
            & (out[col_fecha_inicio_mes].notna())
            & ((out[col_fecha_baja] - out[col_fecha_inicio_mes]).dt.days < 0)
            & ((out[col_salario_pagar] + out[col_may_valor_sal]).abs() == 0),
            custom_text="No se realiza pago por descuento mayor valor pagado"
        )

    return out


