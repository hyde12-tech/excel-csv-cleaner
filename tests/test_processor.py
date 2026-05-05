import pandas as pd
import pytest
from processor import dedupe, sort_data, aggregate, merge_files


@pytest.fixture
def sales_df():
    return pd.DataFrame({
        '部署': ['営業', '営業', '開発', '開発', '営業'],
        '担当者': ['田中', '田中', '鈴木', '佐藤', '田中'],
        '売上': [1000, 1000, 2000, 1500, 800],
    })


# ─── 重複削除 ───

def test_dedupe_removes_duplicates(sales_df):
    result = dedupe(sales_df)
    # (営業, 田中, 1000) が3回 → 1回に
    assert len(result) == 4


def test_dedupe_with_column_subset(sales_df):
    result = dedupe(sales_df, columns=['部署', '担当者'])
    # 部署+担当者でユニーク: 営業/田中, 開発/鈴木, 開発/佐藤 → 3行
    assert len(result) == 3


def test_dedupe_no_duplicates():
    df = pd.DataFrame({'A': [1, 2, 3]})
    result = dedupe(df)
    assert len(result) == 3


# ─── 並び替え ───

def test_sort_ascending(sales_df):
    result = sort_data(sales_df, columns=['売上'], ascending=[True])
    assert result['売上'].iloc[0] == 800
    assert result['売上'].iloc[-1] == 2000


def test_sort_descending(sales_df):
    result = sort_data(sales_df, columns=['売上'], ascending=[False])
    assert result['売上'].iloc[0] == 2000
    assert result['売上'].iloc[-1] == 800


def test_sort_multiple_columns(sales_df):
    result = sort_data(sales_df, columns=['部署', '売上'], ascending=[True, False])
    assert result['部署'].iloc[0] == '営業'
    assert result['部署'].iloc[-1] == '開発'


# ─── 集計 ───

def test_aggregate_sum(sales_df):
    result = aggregate(sales_df, group_by='部署', value_col='売上', method='sum')
    営業合計 = result.loc[result['部署'] == '営業', '売上'].values[0]
    assert 営業合計 == 2800


def test_aggregate_mean(sales_df):
    result = aggregate(sales_df, group_by='部署', value_col='売上', method='mean')
    開発平均 = result.loc[result['部署'] == '開発', '売上'].values[0]
    assert 開発平均 == 1750.0


def test_aggregate_count(sales_df):
    result = aggregate(sales_df, group_by='部署', value_col='売上', method='count')
    営業件数 = result.loc[result['部署'] == '営業', '売上'].values[0]
    assert 営業件数 == 3


# ─── 複数ファイル統合 ───

def test_merge_files():
    df1 = pd.DataFrame({'名前': ['田中'], '売上': [1000]})
    df2 = pd.DataFrame({'名前': ['鈴木'], '売上': [2000]})
    result = merge_files([df1, df2])
    assert len(result) == 2
    assert list(result['名前']) == ['田中', '鈴木']


def test_merge_files_single():
    df = pd.DataFrame({'A': [1, 2]})
    result = merge_files([df])
    assert len(result) == 2


def test_merge_files_resets_index():
    df1 = pd.DataFrame({'A': [1, 2]})
    df2 = pd.DataFrame({'A': [3, 4]})
    result = merge_files([df1, df2])
    assert list(result.index) == [0, 1, 2, 3]
