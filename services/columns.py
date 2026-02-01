import pandas as pd

def delete_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Delete specified columns from the DataFrame."""
    return df.drop(columns=columns, errors='ignore')

def new_column(df: pd.DataFrame, column_name: str, default_value) -> pd.DataFrame:
    """Add a new column with a default value to the DataFrame."""
    df[column_name] = default_value
    return df

def delete_duplicate(df: pd.DataFrame, column_name: str, default_value) -> pd.DataFrame:
    """Delete duplicate columns from the DataFrame."""
    return df.drop_duplicates(subset=[column_name], keep=default_value)

def new_column_with_condition(df: pd.DataFrame, column_name: str, condition, value_if_true, value_if_false) -> pd.DataFrame:
    """Add a new column with a default value to the DataFrame."""
    df[column_name] = value_if_true.where(condition, value_if_false)
    return df

def update_column(df: pd.DataFrame, column_name: str, condition, new_value) -> pd.DataFrame:
    """Update an existing column with new values."""
    df.loc[condition, column_name] = new_value
    return df