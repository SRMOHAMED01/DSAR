import pandas as pd
from sqlalchemy import create_engine, text
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://Mohamed:12345@localhost:5432/dsar_db"
)

engine = create_engine(DATABASE_URL)


def create_schemas():
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
    log.info("Schema 'raw' prêt")


def load_transactions():
    path = "./data/archive/bank_transactions_data_2.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["transactiondate"] = pd.to_datetime(df["transactiondate"], errors="coerce")
    df["previoustransactiondate"] = pd.to_datetime(df["previoustransactiondate"], errors="coerce")
    df.to_sql("raw_kaggle_transactions", engine, schema="raw",
              if_exists="replace", index=False)
    log.info(f"Transactions Kaggle chargées : {len(df)} lignes")


def load_customers():
    path = "./data/Banking-Dataset/Comprehensive_Banking_Database.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    date_cols = ["date_of_account_opening", "last_transaction_date",
                 "transaction_date", "payment_due_date", "feedback_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df.to_sql("raw_github_profiles", engine, schema="raw",
              if_exists="replace", index=False)
    log.info(f"Profils GitHub chargés : {len(df)} lignes")


if __name__ == "__main__":
    create_schemas()
    load_transactions()
    load_customers()
    log.info("Ingest terminé ✅")