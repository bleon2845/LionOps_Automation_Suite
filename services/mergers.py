import pandas as pd

def merge_dataframes(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    left_key,
    right_key,
    how: str,
    merge_name: str
) -> pd.DataFrame:

    try:
        return pd.merge(
            left=df_left,
            right=df_right,
            how=how,
            left_on=left_key,
            right_on=right_key
        )
    except Exception as e:
        raise RuntimeError(f"Error merging dataframes ({merge_name}): {e}")
