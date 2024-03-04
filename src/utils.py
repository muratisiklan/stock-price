import yfinance as yf
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import plotly.express as px


def get_data_from_yfinance(symbol:str, start_date:str, end_date:str):
    # Includes start, excludes end date
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    try:
        # Fetch historical stock data for the specified symbol and date range from Yahoo Finance
        stock_data = yf.download(symbol, start=start_date, end=end_date)

        # Reset the index and format the '_id' field as a string
        stock_data.reset_index(inplace=True)

        return stock_data
    except Exception as e:
        print(
            f"Error fetching data for {symbol} from {start_date} to {end_date}: {e}")


def create_update_collections(connection_string:str, database:str,symbols_list:list)->None:

    """cretes data frame for given symbol list starting from 2015-01-01 to now+1 (now is included)
    """
    client = MongoClient(connection_string)
    db = client[database]
        

    for symbol in symbols_list:

        collection = db[symbol]
        most_recent_document = collection.find_one({}, sort=[('_id', -1)])
        if most_recent_document:
            most_recent_id = most_recent_document["_id"]
            most_recent_date = datetime.strptime(most_recent_id, "%Y-%m-%d")
            one_day_later = most_recent_date + timedelta(days=1)
            start_date = one_day_later.strftime("%Y-%m-%d")

            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            end_date = tomorrow.strftime("%Y-%m-%d")
        else:
            start_date = "2015-01-01"
            tomorrow = datetime.now() + timedelta(days=1)
            end_date = tomorrow.strftime("%Y-%m-%d")


        
        data = get_data_from_yfinance(symbol, start_date,end_date)

        if data.empty:
            print(f"No data retrieved for {symbol}")
            continue

        data['_id'] = pd.to_datetime(data['Date']).dt.strftime("%Y-%m-%d")

        # Drop the original 'Date' column
        data = data.drop(columns=['Date'])

        # Convert the DataFrame to a list of dictionaries
        data_list = data.to_dict(orient='records')

        # Insert the data into the MongoDB collection
        collection.insert_many(data_list)

    client.close()

def get_historical_data(connection_string: str, symbol: str, last_n: int) -> pd.DataFrame:
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client["stockdata"]
        collection = db[symbol]

        # Retrieve the last N documents for the given symbol
        cursor = collection.find().sort("_id", -1).limit(last_n)
        data_list = list(cursor)

        # Convert the selected documents into a DataFrame
        df = pd.DataFrame(data_list)

        return df

    finally:
        # Close the MongoDB connection
        client.close()


def plot_stock(symbol, last_n) -> None:
    try:
        client = MongoClient("mongodb://127.0.0.1:27017/")
        db = client["stockdata"]
        collection = db[symbol]

        cursor = collection.find().sort("_id", -1).limit(last_n)
        data_list = list(cursor)

        df = pd.DataFrame(data_list)

        df["_id"] = pd.to_datetime(df["_id"])

        fig = px.line(df, x="_id", y=["Open", "High", "Low", "Close"], 
                      labels={"_id": "Date", "value": "Price"},
                      title=f"Stock Price Over Time {symbol}")

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price",
            legend_title="Type",
            hovermode="x",
            template="plotly_dark",
            width = 1500,
            height = 750
        )

        fig.show()

    finally:
        client.close()