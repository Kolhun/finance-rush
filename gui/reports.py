"""Вкладка Отчёты — период, суммы, графики."""

from datetime import datetime

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from storage import load_transactions_from_csv
from reports import (
    get_period_transactions,
    get_income_expense_total,
    get_expenses_by_category,
)


class ReportsTab:
    """Вкладка с отчётами и графиками."""

    def __init__(self, parent: ctk.CTkFrame, app: "ctk.CTk") -> None:
        self.parent = parent
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        top_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Период:").pack(side="left", padx=(0, 5))
        self.period_combo = ctk.CTkComboBox(
            top_frame,
            values=["Текущий месяц", "Квартал", "Год", "Всё время"],
            width=150,
            command=self._on_period_change,
        )
        self.period_combo.pack(side="left", padx=(0, 20))

        self.summary_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            self.parent,
            text="Расходы по категориям",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(20, 5))

        self.chart_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh()

    def _period_to_key(self) -> str:
        mapping = {
            "Текущий месяц": "month",
            "Квартал": "quarter",
            "Год": "year",
            "Всё время": "all",
        }
        return mapping.get(self.period_combo.get(), "month")

    def _on_period_change(self, _: str) -> None:
        self.refresh()

    def refresh(self) -> None:
        """Обновляет отчёты и график."""
        transactions = load_transactions_from_csv()
        period_key = self._period_to_key()
        filtered = get_period_transactions(transactions, period_key)
        income, expense, total = get_income_expense_total(filtered)
        by_cat = get_expenses_by_category(filtered)

        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        summary_inner = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        summary_inner.pack(fill="x")

        ctk.CTkLabel(
            summary_inner,
            text=f"Доходы: {income:,.2f} ₽",
            text_color="green",
            font=ctk.CTkFont(size=14),
        ).pack(side="left", padx=(0, 30))
        ctk.CTkLabel(
            summary_inner,
            text=f"Расходы: {expense:,.2f} ₽",
            text_color="red",
            font=ctk.CTkFont(size=14),
        ).pack(side="left", padx=(0, 30))
        ctk.CTkLabel(
            summary_inner,
            text=f"Итого: {total:,.2f} ₽",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not by_cat:
            ctk.CTkLabel(
                self.chart_frame,
                text="Нет данных о расходах за выбранный период.",
                text_color="gray",
            ).pack(anchor="w")
        else:
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            labels = list(by_cat.keys())
            sizes = list(by_cat.values())
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
