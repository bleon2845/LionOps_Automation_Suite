import pandas as pd

def delete_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Delete specified columns from the DataFrame."""
    return df.drop(columns=columns, errors='ignore')

def new_column(df: pd.DataFrame, column_name: str, default_value) -> pd.DataFrame:
    """Add a new column with a default value to the DataFrame."""
    df[column_name] = default_value
    return df

def delete_duplicate_rows(df: pd.DataFrame, column_name: str, keep: str) -> pd.DataFrame:
    """Delete duplicate rows from the DataFrame based on a specific column."""
    return df.drop_duplicates(subset=[column_name], keep=keep)

def new_column_with_condition(df: pd.DataFrame, column_name: str, condition, value_if_true, value_if_false) -> pd.DataFrame:
    """Add a new column with a default value to the DataFrame."""
    df[column_name] = value_if_true.where(condition, value_if_false)
    return df

def update_column(df: pd.DataFrame, column_name: str, condition, new_value) -> pd.DataFrame:
    """Update an existing column with new values."""
    df.loc[condition, column_name] = new_value
    return df

def rename_columns(df: pd.DataFrame, columns_mapping: dict) -> pd.DataFrame:
    """Rename columns in the DataFrame based on a mapping dictionary."""
    return df.rename(columns=columns_mapping)

def filter_and_drop_duplicates(df: pd.DataFrame,*,filter_column: str,filter_value,operator: str = "!=",duplicate_column: str,keep: str = "first") -> pd.DataFrame:
    if operator == "!=":
        df_filtered = df[df[filter_column] != filter_value]
    elif operator == "==":
        df_filtered = df[df[filter_column] == filter_value]
    elif operator == ">":
        df_filtered = df[df[filter_column] > filter_value]
    elif operator == "<":
        df_filtered = df[df[filter_column] < filter_value]
    elif operator == ">=":
        df_filtered = df[df[filter_column] >= filter_value]
    elif operator == "<=":
        df_filtered = df[df[filter_column] <= filter_value]
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    return df_filtered.drop_duplicates(
        subset=[duplicate_column],
        keep=keep
    )

def order_columns(df: pd.DataFrame, column_name: str, ascending: bool) -> pd.DataFrame:
    """order the DataFrame by a specific column."""
    return df.sort_values(by=column_name, ascending=ascending)

def modify_register(df: pd.DataFrame, column_name: str, condition, position:int) -> pd.DataFrame:
    """Modify specific register in column"""
    df[column_name] = df[column_name].str.split(condition).str[position]
    return df

def change_to_datetime(df: pd.DataFrame, column_name: str, error: str = 'coerce') -> pd.DataFrame:
    """Convert a column to datetime format."""
    df[column_name] = pd.to_datetime(df[column_name], errors=error)
    return df

def uppercase_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Uppercase all DataFrame column names."""
    out = df.copy()
    out.columns = out.columns.astype(str).str.upper()
    return out

def concat_full_name(
    df: pd.DataFrame,
    first_name_col: str,
    last_name_1_col: str,
    last_name_2_col: str,
    target_col: str = "NOMBRE COMPLETO"
) -> pd.DataFrame:
    """Create a full name column concatenating first name + last names."""
    out = df.copy()
    for c in [first_name_col, last_name_1_col, last_name_2_col]:
        if c not in out.columns:
            raise ValueError(f"Column '{c}' not found in DataFrame")

    out[target_col] = (
        out[first_name_col].astype(str).fillna("").str.strip() + " " +
        out[last_name_1_col].astype(str).fillna("").str.strip() + " " +
        out[last_name_2_col].astype(str).fillna("").str.strip()
    ).str.replace(r"\s+", " ", regex=True).str.strip()

    return out

def select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Select and order columns, validating which exist."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for selection: {missing}")
    return df[columns].copy()

def map_column_values(df: pd.DataFrame,source_col: str,target_col: str,mapping: dict,default="N/A") -> pd.DataFrame:
    """
    Crea/actualiza target_col según mapping aplicado a source_col.
    Los valores no encontrados quedan en 'default'.
    """
    if df.empty:
        return df
    if source_col not in df.columns:
        raise ValueError(f"Column '{source_col}' not found in DataFrame")

    out = df.copy()
    out[target_col] = out[source_col].map(mapping).fillna(default)
    return out

def update_column_by_prefix(
    df: pd.DataFrame,
    source_col: str,
    value_col: str,
    target_col: str,
    prefix: str,
    multiplier_if_match: float = -1,
    default_from_value_col: bool = True
) -> pd.DataFrame:
    """
    Crea/actualiza target_col tomando value_col.
    Si source_col empieza con prefix => value_col * multiplier_if_match
    Si no:
      - si default_from_value_col=True => value_col
      - else => deja NaN
    """
    if df.empty:
        return df

    for c in [source_col, value_col]:
        if c not in df.columns:
            raise ValueError(f"Column '{c}' not found in DataFrame")

    out = df.copy()
    s = out[source_col].astype(str)
    mask = s.str.startswith(str(prefix), na=False)

    if default_from_value_col:
        out[target_col] = out[value_col]
    else:
        out[target_col] = pd.NA

    out.loc[mask, target_col] = out.loc[mask, value_col] * multiplier_if_match
    return out

def strip_column(
    df: pd.DataFrame,
    column_name: str
) -> pd.DataFrame:
    """
    Convierte la columna a string y elimina espacios a izquierda y derecha.
    """
    if df.empty:
        return df

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")

    out = df.copy()
    out[column_name] = out[column_name].astype(str).str.strip()
    return out

def create_column_total_from_dict(df, dict_totales):
    for nombre_columna, columnas_a_sumar in dict_totales.items():
        columnas_existentes = [col for col in columnas_a_sumar if col in df.columns]
        if not columnas_existentes:
            print(f'Warning: None of the columns for "{nombre_columna}" exist in the DataFrame.')
            df[nombre_columna] = 0
            continue
        
        df[nombre_columna] = df[columnas_existentes].sum(axis=1)
    return df

def init_columns(df: pd.DataFrame, columns: list[str], value) -> pd.DataFrame:
    """Crea columnas si no existen y les asigna un valor (a todas las filas)."""
    out = df.copy()
    for c in columns:
        out[c] = value
    return out

def set_constant_columns(df: pd.DataFrame, constants: dict) -> pd.DataFrame:
    """Asigna valores constantes a múltiples columnas."""
    out = df.copy()
    for col, val in constants.items():
        out[col] = val
    return out


