"""Константы и пути приложения."""

import os

# Базовая директория проекта (где лежит main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к файлам данных
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
ACCOUNTS_CSV = os.path.join(DATA_DIR, "accounts.csv")

# Заголовки CSV для транзакций
TRANSACTION_CSV_HEADERS = [
    "datetime",
    "amount",
    "type",
    "category",
    "subcategory",
    "account",
    "description",
]
