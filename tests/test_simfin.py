# tests/test_simfin.py
import pytest
import pandas as pd
from src.data_fetcher import DataFetcher
from src.data_analysis import FinancialAnalyzer

def test_data_fetcher_income():
    fetcher = DataFetcher()
    df = fetcher.get_income_statement("AMZN")
    assert isinstance(df, pd.DataFrame)
    assert 'Ticker' in df.index.names
    assert not df.empty

def test_financial_analyzer_ratios():
    analyzer = FinancialAnalyzer("AMZN")
    df = analyzer.get_financial_ratios()
    assert 'Gross_Margin' in df.columns
    assert 'EPS' in df.columns
    assert 'Volatility (%)' in df.columns