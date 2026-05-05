import os
import tempfile
import pandas as pd
import pytest
from file_io import read_table, write_table


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        '名前': ['田中', '鈴木', '佐藤'],
        '売上': [1000, 2000, 1500],
    })


def test_read_csv(sample_df, tmp_path):
    path = tmp_path / 'test.csv'
    sample_df.to_csv(path, index=False, encoding='utf-8-sig')
    result = read_table(str(path))
    assert list(result.columns) == ['名前', '売上']
    assert len(result) == 3


def test_read_excel(sample_df, tmp_path):
    path = tmp_path / 'test.xlsx'
    sample_df.to_excel(path, index=False)
    result = read_table(str(path))
    assert list(result.columns) == ['名前', '売上']
    assert len(result) == 3


def test_write_csv(sample_df, tmp_path):
    path = tmp_path / 'output.csv'
    write_table(sample_df, str(path))
    assert path.exists()
    result = pd.read_csv(path, encoding='utf-8-sig')
    assert len(result) == 3


def test_write_excel(sample_df, tmp_path):
    path = tmp_path / 'output.xlsx'
    write_table(sample_df, str(path))
    assert path.exists()
    result = pd.read_excel(path)
    assert len(result) == 3


def test_unsupported_extension(sample_df, tmp_path):
    path = tmp_path / 'test.txt'
    with pytest.raises(ValueError):
        read_table(str(path))
