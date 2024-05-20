from dataclasses import dataclass
import pandas as pd



@dataclass
class StockIngestionConfig:
    connection_string: str = "mongodb://root:password@mongo:27017/"
    database_name: str = "stockdata"
    symbols_list = list(pd.read_csv("./bist_data.csv")["Symbol"])