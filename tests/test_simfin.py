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

def test_load_fresh_shareprices(data_fetcher, mocker):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.remove")
    df = data_fetcher.load_fresh_shareprices()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns

def test_data_fetcher_income_api_failure(data_fetcher, mocker):
    mocker.patch("simfin.load_income", side_effect=Exception("API unavailable"))
    with pytest.raises(Exception, match="API unavailable"):
        data_fetcher.get_income_statement("AMZN")

def test_calculate_volatility(financial_analyzer, mocker):
    mock_prices = pd.DataFrame({"Close": [100, 110, 120, 130]})
    mocker.patch.object(financial_analyzer.fetcher, "get_share_prices", return_value=mock_prices)
    df = financial_analyzer.calculate_volatility()
    assert "Volatility" in df.columns
    assert df["Volatility"].iloc[0] > 0

