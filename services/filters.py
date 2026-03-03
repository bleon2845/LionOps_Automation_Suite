import pandas as pd
from typing import Union, List

def filter_dataframe(
    df: pd.DataFrame,
    column: str,
    values: Union[str, int, List[str], List[int]],
    case_insensitive: bool = True
) -> pd.DataFrame:
    """
    Generic DataFrame filter utility.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to filter
    column : str
        Column name to apply filter on
    values : str | int | list
        Value or list of values to filter by
    case_insensitive : bool
        Apply upper() comparison for strings

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame
    """

    if df.empty:
        raise ValueError("DataFrame is empty")

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")

    df_filtered = df.copy()

    # Convert single value to list for uniform handling
    if not isinstance(values, list):
        values = [values]

    # Handle string comparison
    if case_insensitive and isinstance(values[0], str):
        df_filtered[column] = df_filtered[column].astype(str).str.upper()
        values = [str(v).upper() for v in values]

    return df_filtered[df_filtered[column].isin(values)]

import pandas as pd

def filter_by_operator(df: pd.DataFrame, column: str, value, operator: str) -> pd.DataFrame:
    """Filter rows based on a comparison operator."""
    if df.empty:
        return df
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")

    if operator == "!=":
        return df[df[column] != value]
    if operator == "==":
        return df[df[column] == value]
    if operator == ">":
        return df[df[column] > value]
    if operator == "<":
        return df[df[column] < value]
    if operator == ">=":
        return df[df[column] >= value]
    if operator == "<=":
        return df[df[column] <= value]

    raise ValueError(f"Unsupported operator: {operator}")

def filter_by_prefix(df: pd.DataFrame, column: str, prefix: str, keep_matches: bool = True) -> pd.DataFrame:
    """
    Filter rows where df[column] starts with prefix.
    keep_matches=True -> deja los que empiezan con prefix
    keep_matches=False -> elimina los que empiezan con prefix
    """
    if df.empty:
        return df
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")

    s = df[column].astype(str)
    mask = s.str.startswith(str(prefix), na=False)
    return df[mask] if keep_matches else df[~mask]
