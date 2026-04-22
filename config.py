"""Константы и пути приложения."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
ACCOUNTS_CSV = os.path.join(DATA_DIR, "accounts.csv")

TRANSACTION_CSV_HEADERS = [
    "datetime",
    "amount",
    "type",
    "category",
    "subcategory",
    "account",
    "description",
]
