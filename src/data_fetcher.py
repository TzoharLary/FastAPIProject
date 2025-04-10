# src/data_fetcher.py
import simfin as sf
from dotenv import load_dotenv
import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
SIMFIN_API_KEY = os.getenv("SIMFIN_API_KEY")
DATA_DIR = os.getenv("DATA_DIR", "data/simfin_data/")

class DataFetcher:

    """
        Class for managing data retrieval from financial sources.
    """

    def __init__(self):
        sf.set_api_key(SIMFIN_API_KEY)
        sf.set_data_dir(DATA_DIR)
        logger.info("DataFetcher initialized")

    def get_income_statement(self, ticker: str, market: str = 'us', variant: str = 'annual') -> pd.DataFrame:
        """
        Retrieves the income statement.

        Args:
            ticker (str): Stock symbol.
            market (str): Market.
            variant (str): Reporting period.

        Returns:
            pd.DataFrame: Data table.
        """
        df_income = sf.load_income(variant=variant, market=market)
        company_data = df_income.loc[df_income.index.get_level_values('Ticker') == ticker]
        if company_data.empty:
            raise ValueError(f"No income data for {ticker}")
        return company_data

    def get_balance_sheet(self, ticker: str, market: str = 'us', variant: str = 'annual') -> pd.DataFrame:
        """
        Retrieves the financial balance sheet.

        Args:
            ticker (str): Stock symbol.
            market (str): Market.
            variant (str): Reporting period.

        Returns:
            pd.DataFrame: Data table.
        """
        df_balance = sf.load_balance(variant=variant, market=market)
        company_data = df_balance.loc[df_balance['Ticker'] == ticker]
        if company_data.empty:
            raise ValueError(f"No balance sheet data for {ticker}")
        return company_data

    def get_share_prices(self, ticker: str, variant: str = 'daily', market: str = 'us') -> pd.DataFrame:
        """
        Retrieves stock price data.

        Args:
            ticker (str): Stock symbol.
            variant (str): Reporting frequency.
            market (str): Market.

        Returns:
            pd.DataFrame: Data table.
        """
        df = sf.load_shareprices(variant=variant, market=market).reset_index()
        df = df[df['Ticker'] == ticker].copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        if df.empty:
            raise ValueError(f"No share price data for {ticker}")
        return df
