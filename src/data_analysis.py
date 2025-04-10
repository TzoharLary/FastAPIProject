# Import necessary libraries
import simfin as sf
import pandas as pd
import logging
from config import SIMFIN_API_KEY, DATA_DIR
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_fresh_shareprices(variant='daily', market='us'):
    filename = f'{market}-shareprices-{variant}.csv'
    file_path = os.path.join(DATA_DIR, market, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"✔️ Deleted cached file: {file_path}")
    else:
        print(f"⚠️ File not found (nothing to delete): {file_path}")

    df = sf.load_shareprices(variant=variant, market=market)
    print("✅ Share prices loaded fresh from SimFin.")
    return df

# define the function to get the data from SimFin
def init_simfin():
    """
        function to initialize SimFin API
    """
    sf.set_api_key(SIMFIN_API_KEY)
    # Possible to set a local directory to avoid re-downloading files
    sf.set_data_dir(DATA_DIR)

    # share_prices = load_fresh_shareprices(variant='annual', market='us')

def get_income_statement(ticker: str, market: str = 'us', variant: str = 'annual'):
    """
        Returns the income statement of a company.
        ticker - Stock symbol
        market - Market (usually 'us')
        variant - 'annual' or 'quarterly'
    """

    # Load data based on SimFin
    df_income = sf.load_income(variant=variant, market=market)

    # logger.info("Available columns: %s", df_income.columns)
    logger.info("Index names: %s", df_income.index.names)

    # Filter the requested company
    company_data = df_income.loc[df_income.index.get_level_values('Ticker') == ticker]

    return company_data

def get_balance_sheet(ticker: str, market: str = 'us', variant: str = 'annual'):
    """
        Returns the balance sheet of a company.
    """
    df_balance = sf.load_balance(variant=variant, market=market)
    return df_balance.loc[df_balance['Ticker'] == ticker]

def get_share_prices(ticker: str, variant='daily'):
    df = sf.load_shareprices(variant=variant, market='us').reset_index()
    df = df[df['Ticker'] == ticker].copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    return df


def calculate_financial_ratios(ticker: str):
    """
    Retrieves and calculates financial ratios for a company, including:
      - Earnings Per Share (EPS)
      - Price-to-Earnings Ratio (P/E)
      - Profit margins (Gross, Operating, Net)
      - Price before and after the earnings report (based on Publish Date)
    """
    init_simfin()

    # --- Income Statement ---
    income_annual = get_income_statement(ticker, variant='annual')
    df_income = income_annual[['Fiscal Year', 'Revenue', 'Cost of Revenue', 'Gross Profit',
                               'Operating Expenses', 'Operating Income (Loss)', 'Net Income',
                               'Shares (Basic)', 'Publish Date']]
    df_income = df_income.dropna(subset=['Revenue', 'Gross Profit', 'Operating Income (Loss)', 'Net Income'])

    # --- Profit Margins in Percentage ---
    df_income['Gross_Margin'] = (df_income['Gross Profit'] / df_income['Revenue']) * 100
    df_income['Operating_Margin'] = (df_income['Operating Income (Loss)'] / df_income['Revenue']) * 100
    df_income['Net_Margin'] = (df_income['Net Income'] / df_income['Revenue']) * 100

    # --- Daily Share Price Data ---
    share_prices_daily = load_fresh_shareprices(variant='daily', market='us').reset_index()
    sp_ticker = share_prices_daily[share_prices_daily['Ticker'] == ticker].copy()
    if sp_ticker.empty:
        logger.error("Ticker %s not found in share prices data.", ticker)
        return df_income

    sp_ticker['Date'] = pd.to_datetime(sp_ticker['Date'])
    sp_ticker['Year'] = sp_ticker['Date'].dt.year

    # --- Average Price per Year ---
    avg_price_by_year = sp_ticker.groupby('Year')['Close'].mean().reset_index()
    avg_price_by_year.rename(columns={'Year': 'Fiscal Year', 'Close': 'Average_Share_Price'}, inplace=True)

    # --- Merge with Income Statement ---
    df_merged = pd.merge(df_income, avg_price_by_year, on='Fiscal Year', how='left')

    # --- Calculate EPS and P/E Ratio ---
    df_merged['EPS'] = df_merged['Net Income'] / df_merged['Shares (Basic)']
    df_merged['PE Ratio'] = df_merged.apply(
        lambda row: row['Average_Share_Price'] / row['EPS'] if row['EPS'] else None, axis=1
    )

    # --- Calculate Share Price Before and After Report Publication ---
    prices = sp_ticker.set_index('Date')

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

    df_sorted = df_merged.sort_values('Fiscal Year')
    base_year = df_sorted['Fiscal Year'].min()
    base_price = df_sorted.loc[df_sorted['Fiscal Year'] == base_year, 'Average_Share_Price'].values[0]

    def compute_cagr(current_price, current_year):
        # אם זו השנה הבסיסית, CAGR הוא 0
        if current_year == base_year or not current_price:
            return 0
        # CAGR = (Current Price / Base Price)^(1/(Year difference)) - 1
        return (current_price / base_price) ** (1 / (current_year - base_year)) - 1

    df_merged['CAGR'] = df_merged.apply(lambda row: compute_cagr(row['Average_Share_Price'], row['Fiscal Year']),
                                        axis=1)
    df_merged['CAGR (%)'] = df_merged['CAGR'] * 100

    return df_merged.round(2)
