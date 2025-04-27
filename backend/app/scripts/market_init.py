from ..database import SessionLocal
from ..models import Market
import pandas as pd
from psycopg2.errors import UniqueViolation


def init_markets():
    db = SessionLocal()
    try:
        df = pd.read_csv("app/artifacts/market_data.csv")

        for _, row in df.iterrows():
            try:
                # Check if a market with the same name already exists
                existing_market = db.query(Market).filter(
                    Market.name == row['Name']).first()

                if not existing_market:
                    # Market does not exist, so insert it
                    new_market = Market(
                        name=row['Name'],
                        country=row['Country'],
                        currency=row['Currency'],
                        timezone=row["Timezone"],
                        mic_code=row["Mic_code"],
                        yahoo_suffix=row["Yahoo_suffix"] if pd.notna(row["Yahoo_suffix"]) else None,
                        index_30=None,
                        index_50=None,
                        index_100=None
                    )
                    db.add(new_market)
                else:
                    # If market already exists, skip it
                    print(
                        f"Market {row['Name']} already exists. Skipping insertion.")

            except UniqueViolation:
                # If a unique constraint violation occurs, skip the insertion
                print(
                    f"Duplicate entry for market {row['Name']}. Skipping insertion.")

        # Commit changes to the database
        db.commit()

    except Exception as e:
        db.rollback()  # Rollback if there is an error
        print(f"An error occurred: {e}")
    finally:
        db.close()
