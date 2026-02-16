"""Вкладка Дашборд."""

import customtkinter as ctk

from storage import load_transactions_from_csv
from reports import get_balances, get_period_transactions


class DashboardTab:
    """Вкладка с балансами и последними транзакциями."""

    def __init__(self, parent: ctk.CTkFrame, app: "ctk.CTk") -> None:
        self.parent = parent
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        self.balances_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.balances_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            self.balances_frame,
            text="Балансы по счетам",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        self.balances_container = ctk.CTkFrame(
            self.balances_frame, fg_color="transparent"
        )
        self.balances_container.pack(fill="x", pady=5)

        ctk.CTkLabel(
            self.parent,
            text="Последние транзакции",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(20, 5))

        self.transactions_scroll = ctk.CTkScrollableFrame(
            self.parent, height=300, fg_color="transparent"
        )
        self.transactions_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh()

    def refresh(self) -> None:
        """Обновляет данные на дашборде."""
        transactions = load_transactions_from_csv()
        balances = get_balances(transactions)

        for widget in self.balances_container.winfo_children():
            widget.destroy()

        if not balances:
            ctk.CTkLabel(
                self.balances_container,
                text="Нет данных. Добавьте транзакции.",
                text_color="gray",
            ).pack(anchor="w")
        else:
            total = sum(balances.values())
            for account, balance in balances.items():
                card = ctk.CTkFrame(
                    self.balances_container,
                    width=180,
                    height=60,
                    corner_radius=8,
                    fg_color=("gray85", "gray25"),
                )
                card.pack(side="left", padx=(0, 10), pady=5)
                card.pack_propagate(False)
                ctk.CTkLabel(card, text=account, font=ctk.CTkFont(size=12)).pack(
                    anchor="w", padx=10, pady=(8, 0)
                )
                ctk.CTkLabel(
                    card,
                    text=f"{balance:,.2f} ₽",
                    font=ctk.CTkFont(size=14, weight="bold"),
                ).pack(anchor="w", padx=10, pady=(0, 8))

            total_card = ctk.CTkFrame(
                self.balances_container,
                width=180,
                height=60,
                corner_radius=8,
                fg_color=("gray75", "gray30"),
            )
            total_card.pack(side="left", padx=(0, 10), pady=5)
            total_card.pack_propagate(False)
            ctk.CTkLabel(
                total_card, text="Итого", font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=10, pady=(8, 0))
            ctk.CTkLabel(
                total_card,
                text=f"{total:,.2f} ₽",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(anchor="w", padx=10, pady=(0, 8))

        for widget in self.transactions_scroll.winfo_children():
            widget.destroy()

        recent = sorted(
            get_period_transactions(transactions, "all"),
            key=lambda t: t.datetime,
            reverse=True,
        )[:10]

        if not recent:
            ctk.CTkLabel(
                self.transactions_scroll,
                text="Нет транзакций.",
                text_color="gray",
            ).pack(anchor="w")
        else:
            for tx in recent:
                row = ctk.CTkFrame(
                    self.transactions_scroll,
                    fg_color="transparent",
                    height=28,
                )
                row.pack(fill="x", pady=2)
                row.pack_propagate(False)
                date_str = tx.datetime.strftime("%d.%m.%Y")
                amount_str = f"+{tx.amount:,.2f}" if tx.type == "Доход" else f"-{tx.amount:,.2f}"
                color = "green" if tx.type == "Доход" else "red"
                ctk.CTkLabel(row, text=date_str, width=80).pack(side="left")
                ctk.CTkLabel(row, text=tx.category, width=120).pack(side="left")
                ctk.CTkLabel(row, text=tx.account, width=100).pack(side="left")
                ctk.CTkLabel(
                    row,
                    text=amount_str,
                    width=100,
                    text_color=color,
                ).pack(side="left")
                desc = (tx.description or "")[:40]
                ctk.CTkLabel(row, text=desc, anchor="w").pack(side="left", fill="x", expand=True)
