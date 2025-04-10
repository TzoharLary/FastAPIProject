# src/data_analysis.py
import simfin as sf
import pandas as pd
from scipy import stats
from dotenv import load_dotenv
import os
import logging
from src.data_fetcher import DataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load API key and data path from .env
load_dotenv()
SIMFIN_API_KEY = os.getenv("SIMFIN_API_KEY")
DATA_DIR = os.getenv("DATA_DIR", "data/simfin_data/")

class FinancialAnalyzer:
    """Class for managing data and calculating financial ratios."""

    def __init__(self, ticker: str, market: str = 'us', variant: str = 'annual'):
        self.ticker = ticker
        self.market = market
        self.variant = variant
        self.fetcher = DataFetcher()
        logger.info(f"Initialized FinancialAnalyzer for {ticker}")

    def load_fresh_shareprices(self) -> pd.DataFrame:
        filename = f'{self.market}-shareprices-daily.csv'
        file_path = os.path.join(DATA_DIR, self.market, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted cached file: {file_path}")
        return self.fetcher.get_share_prices(self.ticker, variant='daily', market=self.market)

    def get_income_statement(self) -> pd.DataFrame:
        """
        Retrieve the income statement for the specified ticker.
        Args:
            ticker (str): Stock symbol.
            market (str): Market.
            variant (str): Reporting period.
        Returns:
            pd.DataFrame: Income statement data.
        Raises:
            ValueError: If no data is found for the ticker.
        """
        return self.fetcher.get_income_statement(self.ticker, self.market, self.variant)

    def calculate_margins(self, df_income: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profit margins (Gross, Operating, Net).

        Args:
            df_income (pd.DataFrame): Income statement data.

        Returns:
            pd.DataFrame: Table with calculated margins.
        """
        df = df_income.copy()
        df['Gross_Margin'] = (df['Gross Profit'] / df['Revenue']) * 100
        df['Operating_Margin'] = (df['Operating Income (Loss)'] / df['Revenue']) * 100
        df['Net_Margin'] = (df['Net Income'] / df['Revenue']) * 100
        return df

    def calculate_eps_and_pe(self, df_income: pd.DataFrame, share_prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate EPS and P/E Ratio.

        Args:
            df_income (pd.DataFrame): Income statement data.
            share_prices (pd.DataFrame): Share price data.

        Returns:
            pd.DataFrame: Table with EPS and P/E values.
        """
        sp_ticker = share_prices[share_prices['Ticker'] == self.ticker].copy()
        if sp_ticker.empty:
            logger.error(f"Ticker {self.ticker} not found in share prices data.")
            return df_income

        sp_ticker['Date'] = pd.to_datetime(sp_ticker['Date'])
        sp_ticker['Year'] = sp_ticker['Date'].dt.year
        avg_price_by_year = sp_ticker.groupby('Year')['Close'].mean().reset_index()
        avg_price_by_year.rename(columns={'Year': 'Fiscal Year', 'Close': 'Average_Share_Price'}, inplace=True)

        df_merged = pd.merge(df_income, avg_price_by_year, on='Fiscal Year', how='left')
        df_merged['EPS'] = df_merged['Net Income'] / df_merged['Shares (Basic)']
        df_merged['PE Ratio'] = df_merged.apply(
            lambda row: row['Average_Share_Price'] / row['EPS'] if row['EPS'] else None, axis=1
        )
        return df_merged

    def calculate_price_changes(self, df_merged: pd.DataFrame, share_prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate stock prices before and after report publication.

        Args:
            df_merged (pd.DataFrame): Merged table.
            share_prices (pd.DataFrame): Share price data.

        Returns:
            pd.DataFrame: Table with before and after prices.
        """
        prices = share_prices[share_prices['Ticker'] == self.ticker].set_index('Date')

        def get_before_after_price(date_str):
            try:
                date = pd.to_datetime(date_str)
                before = prices.loc[:date].iloc[-1]['Close']
                after = prices.loc[date:].iloc[0]['Close']
                return before, after
            except:
                return None, None

        df_merged['Publish Date'] = pd.to_datetime(df_merged['Publish Date'])
        results = df_merged['Publish Date'].apply(get_before_after_price)
        df_merged['Price_Before_Report'] = results.apply(lambda x: x[0])
        df_merged['Price_After_Report'] = results.apply(lambda x: x[1])
        return df_merged

    def calculate_cagr(self, df_merged: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate CAGR for stock prices.

        Args:
            df_merged (pd.DataFrame): Merged table.

        Returns:
            pd.DataFrame: Table with CAGR values.
        """
        df_sorted = df_merged.sort_values('Fiscal Year')
        base_year = df_sorted['Fiscal Year'].min()
        base_price = df_sorted.loc[df_sorted['Fiscal Year'] == base_year, 'Average_Share_Price'].values[0]

        def compute_cagr(current_price, current_year):
            if current_year == base_year or not current_price:
                return 0
            return (current_price / base_price) ** (1 / (current_year - base_year)) - 1

        df_merged['CAGR'] = df_merged.apply(lambda row: compute_cagr(row['Average_Share_Price'], row['Fiscal Year']),
                                            axis=1)
        df_merged['CAGR (%)'] = df_merged['CAGR'] * 100
        return df_merged

    def calculate_volatility(self, share_prices: pd.DataFrame) -> float:
        """
        Calculate annual volatility of stock prices using SciPy.

        Args:
            share_prices (pd.DataFrame): Share price data.

        Returns:
            float: Annualized volatility.
        """
        sp_ticker = share_prices[share_prices['Ticker'] == self.ticker].copy()
        sp_ticker['Date'] = pd.to_datetime(sp_ticker['Date'])
        sp_ticker['Year'] = sp_ticker['Date'].dt.year
        returns = sp_ticker.groupby('Year').apply(lambda x: x['Close'].pct_change().dropna())
        volatility_by_year = returns.groupby('Year').apply(stats.tstd) * (252 ** 0.5)
        return volatility_by_year

    def get_financial_ratios(self) -> pd.DataFrame:
        """
        Return a table with all financial ratios.

        Returns:
            pd.DataFrame: Table of calculated financial data.
        """
        income_annual = self.get_income_statement()
        df_income = income_annual[['Fiscal Year', 'Revenue', 'Cost of Revenue', 'Gross Profit',
                                   'Operating Expenses', 'Operating Income (Loss)', 'Net Income',
                                   'Shares (Basic)', 'Publish Date']].dropna(
            subset=['Revenue', 'Gross Profit', 'Operating Income (Loss)', 'Net Income'])

        df_income = self.calculate_margins(df_income)
        share_prices = self.load_fresh_shareprices()
        df_merged = self.calculate_eps_and_pe(df_income, share_prices)
        df_merged = self.calculate_price_changes(df_merged, share_prices)
        df_merged = self.calculate_cagr(df_merged)
        volatility = self.calculate_volatility(share_prices)

        logger.info(f"Volatility calculated for {self.ticker}")
        df_merged = df_merged.merge(
            volatility.rename('Volatility').to_frame().reset_index(),
            left_on='Fiscal Year',
            right_on='Year',
            how='left'
        )

        df_merged['Volatility (%)'] = df_merged['Volatility'] * 100
        df_merged = df_merged.drop(columns=['Year', 'Volatility'])  # clean up temp columns
        return df_merged.round(2)

def calculate_financial_ratios(ticker: str, variant: str = 'annual') -> pd.DataFrame:
    """
    External interface to calculate financial ratios.

    Args:
        ticker (str): Stock symbol.
        variant (str, optional): Reporting period.

    Returns:
        pd.DataFrame: Table of calculated financial data.
    """
    analyzer = FinancialAnalyzer(ticker, variant=variant)
    return analyzer.get_financial_ratios()
