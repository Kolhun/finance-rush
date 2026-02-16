"""Отчёты и аналитика."""

from datetime import datetime
from collections import defaultdict

from models import Account, Transaction


def get_balances(
    transactions: list[Transaction],
    accounts: list[Account] | None = None,
) -> dict[str, float]:
    """
    Вычисляет баланс по каждому счёту.

    Учитывает initial_balance из accounts и все транзакции.
    Доход увеличивает баланс, расход — уменьшает.
    """
    balances: dict[str, float] = {}

    if accounts:
        for acc in accounts:
            balances[acc.name] = acc.initial_balance

    for tx in transactions:
        if tx.account not in balances:
            balances[tx.account] = 0.0

        if tx.type == "Доход":
            balances[tx.account] += tx.amount
        else:
            balances[tx.account] -= tx.amount

    return balances


def get_period_transactions(
    transactions: list[Transaction],
    period: str,
    reference_date: datetime | None = None,
) -> list[Transaction]:
    """
    Фильтрует транзакции по периоду.

    period: "month" | "quarter" | "year" | "all"
    reference_date: дата, от которой считается период (по умолчанию — сегодня).
    """
    ref = reference_date or datetime.now()
    result: list[Transaction] = []

    for tx in transactions:
        if period == "all":
            result.append(tx)
        elif period == "month":
            if tx.datetime.year == ref.year and tx.datetime.month == ref.month:
                result.append(tx)
        elif period == "quarter":
            q = (ref.month - 1) // 3 + 1
            tx_q = (tx.datetime.month - 1) // 3 + 1
            if tx.datetime.year == ref.year and tx_q == q:
                result.append(tx)
        elif period == "year":
            if tx.datetime.year == ref.year:
                result.append(tx)

    return result


def get_income_expense_total(
    transactions: list[Transaction],
) -> tuple[float, float, float]:
    """
    Возвращает (доходы, расходы, итого).
    Итого = доходы - расходы.
    """
    income = sum(tx.amount for tx in transactions if tx.type == "Доход")
    expense = sum(tx.amount for tx in transactions if tx.type == "Расход")
    return income, expense, income - expense


def get_expenses_by_category(
    transactions: list[Transaction],
) -> dict[str, float]:
    """Суммы расходов по категориям."""
    by_cat: dict[str, float] = defaultdict(float)
    for tx in transactions:
        if tx.type == "Расход" and tx.amount > 0:
            by_cat[tx.category or "Без категории"] += tx.amount
    return dict(by_cat)
