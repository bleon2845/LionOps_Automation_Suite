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