from ..database import SessionLocal
from ..models import Company
import pandas as pd
from psycopg2.errors import UniqueViolation

def init_companies():
    db = SessionLocal()
    try:
        df = pd.read_csv("app/artifacts/bist_data.csv")

        for _, row in df.iterrows():
            try:
                # Check if a company with the same name already exists
                existing_company = db.query(Company).filter(Company.name == row['Name']).first()

                if not existing_company:
                    # Company does not exist, so insert it
                    new_company = Company(
                        ticker=row['Symbol'],
                        name=row['Name'],
                        market_id=None,  # or some default if you want
                    )
                    db.add(new_company)
                else:
                    # If company already exists, skip it
                    print(f"Company {row['Name']} already exists. Skipping insertion.")

            except UniqueViolation:
                # If a unique constraint violation occurs, skip the insertion
                print(f"Duplicate entry for company {row['Name']}. Skipping insertion.")

        # Commit changes to the database
        db.commit()

    except Exception as e:
        db.rollback()  # Rollback if there is an error
        print(f"An error occurred: {e}")
    finally:
        db.close()
