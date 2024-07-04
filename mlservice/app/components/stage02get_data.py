from ..utils import get_historical_data
import os.path as path
import pandas as pd
import numpy as np
from ..database import client
from ..exception import CustomException
from ..logger import logging
import sys

# Path to the CSV file containing the list of stock symbols
path_to_file: str = path.abspath(
    path.join(__file__, "../../../artifacts/base_data/bist_data.csv"))

# Read the symbols from the CSV file
symbols_list = list(pd.read_csv(path_to_file)["Symbol"])


async def calculate_company_metrics(last_n_days: int) -> dict:
    """
    Calculate various metrics for each company's stock based on historical data.

    Args:
        last_n_days (int): Number of days of historical data to consider.

    Returns:
        dict: Dictionary containing calculated metrics for each company.
    """
    metrics_dict = {}

    try:
        for symbol in symbols_list:
            # Fetch historical data for the last 'last_n_days' days
            df = await get_historical_data(client, symbol, last_n_days)

            if df.empty:
                logging.warning(f"No data found for {symbol}. Skipping...")
                continue

            closing_prices = df['Close']

            # Calculate metrics
            max_value = closing_prices.max()
            min_value = closing_prices.min()
            std_dev = closing_prices.std()
            price_interval = max_value - min_value
            percentage_change = (
                (closing_prices.iloc[-1] - closing_prices.iloc[0]) / closing_prices.iloc[0]) * 100

            daily_returns = closing_prices.pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(last_n_days)

            cumulative_return = (
                closing_prices.iloc[-1] / closing_prices.iloc[0] - 1) * 100

            sma_20 = closing_prices.rolling(window=20).mean(
            ).iloc[-1] if len(closing_prices) >= 20 else np.nan
            sma_50 = closing_prices.rolling(window=50).mean(
            ).iloc[-1] if len(closing_prices) >= 50 else np.nan

            ema_20 = closing_prices.ewm(span=20, adjust=False).mean(
            ).iloc[-1] if len(closing_prices) >= 20 else np.nan
            ema_50 = closing_prices.ewm(span=50, adjust=False).mean(
            ).iloc[-1] if len(closing_prices) >= 50 else np.nan

            delta = closing_prices.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14, min_periods=1).mean()
            avg_loss = loss.rolling(window=14, min_periods=1).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]

            sma_20_bb = closing_prices.rolling(window=20).mean() if len(
                closing_prices) >= 20 else np.nan
            rolling_std_20 = closing_prices.rolling(
                window=20).std() if len(closing_prices) >= 20 else np.nan
            upper_band = sma_20_bb + \
                (rolling_std_20 * 2) if sma_20_bb is not np.nan else np.nan
            lower_band = sma_20_bb - \
                (rolling_std_20 * 2) if sma_20_bb is not np.nan else np.nan
            latest_upper_band = upper_band.iloc[-1] if upper_band is not np.nan else np.nan
            latest_lower_band = lower_band.iloc[-1] if lower_band is not np.nan else np.nan

            sharpe_ratio = (daily_returns.mean() /
                            daily_returns.std()) * np.sqrt(252) if daily_returns.std() != 0 else np.nan

            # Store the metrics in the dictionary
            metrics_dict[symbol] = {
                'Max Value': max_value,
                'Min Value': min_value,
                'Standard Deviation': std_dev,
                'Price Interval': price_interval,
                'Percentage Change': percentage_change,
                'Volatility': volatility,
                'Cumulative Return': cumulative_return,
                'SMA 20': sma_20,
                'SMA 50': sma_50,
                'EMA 20': ema_20,
                'EMA 50': ema_50,
                'RSI': rsi,
                'Bollinger Upper Band': latest_upper_band,
                'Bollinger Lower Band': latest_lower_band,
                'Sharpe Ratio': sharpe_ratio
            }

    except Exception as e:
        logging.error(f"Error processing {symbol}: {e}")
        raise CustomException(f"Error processing {symbol}: {e}",sys)

    return metrics_dict
