"""Хранение данных в CSV."""

import csv
import os
from datetime import datetime

from config import TRANSACTION_CSV_HEADERS, TRANSACTIONS_CSV
from models import Transaction


def _ensure_data_dir(path: str) -> None:
    """Создаёт директорию для файла, если её нет."""
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _ensure_csv_headers(path: str, headers: list[str]) -> None:
    """Создаёт файл с заголовками, если файл не существует или пуст."""
    _ensure_data_dir(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


def append_transaction_to_csv(tx: Transaction, path: str | None = None) -> None:
    """Добавляет транзакцию в CSV-файл."""
    path = path or TRANSACTIONS_CSV
    _ensure_csv_headers(path, TRANSACTION_CSV_HEADERS)

    row = [
        tx.datetime.strftime("%Y-%m-%d %H:%M:%S"),
        str(tx.amount),
        tx.type,
        tx.category,
        tx.subcategory or "",
        tx.account,
        tx.description or "",
    ]

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def load_transactions_from_csv(path: str | None = None) -> list[Transaction]:
    """Загружает все транзакции из CSV."""
    path = path or TRANSACTIONS_CSV
    if not os.path.exists(path):
        return []

    transactions: list[Transaction] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                dt = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S")
            except (ValueError, KeyError):
                try:
                    dt = datetime.strptime(row["datetime"], "%Y-%m-%d")
                except (ValueError, KeyError):
                    continue

            amount = float(row.get("amount", 0))
            subcategory = row.get("subcategory") or None
            if subcategory == "":
                subcategory = None
            description = row.get("description") or None
            if description == "":
                description = None

            transactions.append(
                Transaction(
                    datetime=dt,
                    amount=amount,
                    type=row.get("type", "Расход"),
                    category=row.get("category", ""),
                    subcategory=subcategory,
                    account=row.get("account", ""),
                    description=description,
                )
            )

    return transactions
