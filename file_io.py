import pandas as pd


def read_table(path: str) -> pd.DataFrame:
    if path.endswith('.csv'):
        return pd.read_csv(path, encoding='utf-8-sig')
    elif path.endswith('.xlsx'):
        return pd.read_excel(path)
    else:
        raise ValueError(f'対応していないファイル形式です: {path}')


def write_table(df: pd.DataFrame, path: str) -> None:
    if path.endswith('.csv'):
        df.to_csv(path, index=False, encoding='utf-8-sig')
    elif path.endswith('.xlsx'):
        df.to_excel(path, index=False)
    else:
        raise ValueError(f'対応していないファイル形式です: {path}')
