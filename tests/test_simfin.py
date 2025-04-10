import simfin as sf
from config import SIMFIN_API_KEY
import warnings
from src.data_analysis import calculate_financial_ratios

warnings.simplefilter(action='ignore', category=FutureWarning)

sf.set_api_key(SIMFIN_API_KEY)
sf.set_data_dir('../data/simfin_data/')

# We load the income statement for the US market
df = sf.load_income(variant='annual', market='us')


df = calculate_financial_ratios("AAPL")  # למשל AAPL
print(df)
