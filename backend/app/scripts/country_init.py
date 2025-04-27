from ..database import SessionLocal
from ..models import Country
import pandas as pd
from psycopg2.errors import UniqueViolation

def init_countries():
    db = SessionLocal()
    try:
        df = pd.read_csv("app/artifacts/country_data.csv")

        for _, row in df.iterrows():
            try:
                # Check if a country with the same country code already exists
                existing_country = db.query(Country).filter(Country.country_code == row['CountryCode']).first()

                if not existing_country:
                    # Country does not exist, so insert it
                    new_country = Country(
                        country_code=row['CountryCode'],
                        name=row['Name'],
                        region=str(row["Region"]), 
                        income_level= int(row["IncomeLevel"]) if not pd.isnull(row["IncomeLevel"]) else None
                    )
                    db.add(new_country)
                else:
                    # If country already exists, skip it
                    print(f"Company {row['Name']} already exists. Skipping insertion.")

            except UniqueViolation:
                # If a unique constraint violation occurs, skip the insertion
                print(f"Duplicate entry for company {row['CountryCode']}. Skipping insertion.")

        # Commit changes to the database
        db.commit()

    except Exception as e:
        db.rollback()  # Rollback if there is an error
        print(f"An error occurred: {e}")
    finally:
        db.close()
