"""Модели данных приложения."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Транзакция (доход или расход)."""

    datetime: datetime
    amount: float
    type: str  # "Доход" | "Расход"
    category: str
    subcategory: str | None
    account: str
    description: str | None = None


@dataclass
class Account:
    """Счёт или кошелёк."""

    name: str
    type: str  # cash, card, crypto, etc.
    currency: str = "RUB"
    initial_balance: float = 0.0
