import pandas as pd


def dedupe(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    return df.drop_duplicates(subset=columns).reset_index(drop=True)


def sort_data(df: pd.DataFrame, columns: list[str], ascending: list[bool]) -> pd.DataFrame:
    return df.sort_values(by=columns, ascending=ascending).reset_index(drop=True)


def aggregate(df: pd.DataFrame, group_by: str, value_col: str, method: str) -> pd.DataFrame:
    grouped = df.groupby(group_by)[value_col]
    if method == 'sum':
        result = grouped.sum()
    elif method == 'mean':
        result = grouped.mean()
    elif method == 'count':
        result = grouped.count()
    else:
        raise ValueError(f'対応していない集計方法です: {method}')
    return result.reset_index()


def merge_files(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(dfs, ignore_index=True)
