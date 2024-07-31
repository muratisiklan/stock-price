from ..utils.utils import get_historical_data
import os.path as path
import pandas as pd
import numpy as np
from ..utils.exception import CustomException
from ..utils.logger import logging
import sys


class CompanyMetrics():

    def __init__(self, mongo_uri) -> None:
        self.uri = mongo_uri
        self.symbols_list = list(pd.read_csv(path.abspath(
            path.join(__file__, "../../../artifacts/base_data/bist_data.csv")))["Symbol"])

    # TODO: Metric calculations should be updated correctly some of them can be eliminated

    def calculate_company_metrics(self, symbol: str, start_date: str, return_data: bool = False) -> dict:
        """
        Calculate various metrics for each company's stock based on historical data.

        Args:
            last_n_days (int): Number of days of historical data to consider.

        Returns:
            dict: Dictionary containing calculated metrics for each company.
        """
        metrics_dict = {}

        try:
            # Fetch historical data for the last 'last_n_days' days
            df = get_historical_data(self.uri, symbol, start_date)

            closing_prices = df['Close']

            # Calculate metric

            max_value = closing_prices.max()
            min_value = closing_prices.min()
            std_dev = closing_prices.std()
            price_interval = max_value - min_value
            percentage_change = (
                (closing_prices.iloc[-1] - closing_prices.iloc[0]) / closing_prices.iloc[0]) * 100

            daily_returns = closing_prices.pct_change(
                fill_method="ffill").dropna()
            volatility = daily_returns.std() * np.sqrt(len(closing_prices))

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
            metrics_dict = {
                'Symbol': symbol,
                "Start From": start_date,
                'Max Value': round(max_value, 3),
                'Min Value': round(min_value, 3),
                'Standard Deviation': round(std_dev, 3),
                'Price Interval': round(price_interval, 3),
                'Percentage Change': round(percentage_change, 3),
                'Volatility': round(volatility, 3),
                'RSI': round(rsi, 3),
                'Bollinger Upper Band': round(latest_upper_band, 3),
                'Bollinger Lower Band': round(latest_lower_band, 3),
                'Sharpe Ratio': round(sharpe_ratio, 3)
            }

        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")
            raise CustomException(f"Error processing {symbol}: {e}", sys)
        if return_data == True:
            return df
        else:
            return metrics_dict
