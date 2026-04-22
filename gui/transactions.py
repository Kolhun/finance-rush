"""Вкладка Транзакции — форма и таблица."""

from datetime import datetime

import customtkinter as ctk

from models import Transaction
from storage import append_transaction_to_csv, load_transactions_from_csv
from gui.import_dialog import ImportDialog

DEFAULT_ACCOUNTS = ["Тинькофф", "Сбер", "Наличные", "Крипто"]
DEFAULT_CATEGORIES = [
    "Еда",
    "Транспорт",
    "Развлечения",
    "Жильё",
    "Здоровье",
    "Одежда",
    "Образование",
    "Прочее",
]


class TransactionsTab:
    """Вкладка с формой добавления и таблицей транзакций."""

    def __init__(self, parent: ctk.CTkFrame, app: "ctk.CTk") -> None:
        self.parent = parent
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        form_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            form_frame,
            text="Добавить транзакцию",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Сумма:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=3)
        self.amount_entry = ctk.CTkEntry(form_frame, width=120, placeholder_text="0.00")
        self.amount_entry.grid(row=1, column=1, sticky="w", pady=3)

        ctk.CTkLabel(form_frame, text="Тип:").grid(row=1, column=2, sticky="w", padx=(20, 5), pady=3)
        self.type_combo = ctk.CTkComboBox(
            form_frame,
            values=["Расход", "Доход"],
            width=120,
        )
        self.type_combo.grid(row=1, column=3, sticky="w", pady=3)

        ctk.CTkLabel(form_frame, text="Счёт:").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=3)
        self.account_combo = ctk.CTkComboBox(
            form_frame,
            values=DEFAULT_ACCOUNTS,
            width=120,
        )
        self.account_combo.grid(row=2, column=1, sticky="w", pady=3)

        ctk.CTkLabel(form_frame, text="Категория:").grid(
            row=2, column=2, sticky="w", padx=(20, 5), pady=3
        )
        self.category_combo = ctk.CTkComboBox(
            form_frame,
            values=DEFAULT_CATEGORIES,
            width=120,
        )
        self.category_combo.grid(row=2, column=3, sticky="w", pady=3)

        ctk.CTkLabel(form_frame, text="Дата:").grid(row=3, column=0, sticky="w", padx=(0, 5), pady=3)
        self.date_entry = ctk.CTkEntry(
            form_frame,
            width=120,
            placeholder_text="ГГГГ-ММ-ДД или пусто = сегодня",
        )
        self.date_entry.grid(row=3, column=1, sticky="w", pady=3)

        ctk.CTkLabel(form_frame, text="Описание:").grid(
            row=3, column=2, sticky="w", padx=(20, 5), pady=3
        )
        self.description_entry = ctk.CTkEntry(
            form_frame,
            width=200,
            placeholder_text="Необязательно",
        )
        self.description_entry.grid(row=3, column=3, sticky="w", pady=3)

        self.save_btn = ctk.CTkButton(
            form_frame,
            text="Сохранить",
            command=self._on_save,
            width=120,
        )
        self.save_btn.grid(row=4, column=1, sticky="w", pady=15)

        ctk.CTkButton(
            form_frame,
            text="Импорт CSV",
            command=self._on_import_csv,
            width=120,
        ).grid(row=4, column=2, sticky="w", padx=(10, 0), pady=15)

        ctk.CTkLabel(
            self.parent,
            text="Список транзакций",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.table_scroll = ctk.CTkScrollableFrame(
            self.parent, height=280, fg_color="transparent"
        )
        self.table_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh()

    def _on_import_csv(self) -> None:
        """Открывает диалог импорта CSV."""
        ImportDialog(self.app, on_import_done=self.app.refresh_all)

    def _on_save(self) -> None:
        """Сохраняет новую транзакцию."""
        try:
            amount = float(self.amount_entry.get().replace(",", ".").strip())
        except ValueError:
            return

        date_str = self.date_entry.get().strip()
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                dt = dt.replace(hour=datetime.now().hour, minute=datetime.now().minute)
            except ValueError:
                dt = datetime.now()
        else:
            dt = datetime.now()

        tx = Transaction(
            datetime=dt,
            amount=amount,
            type=self.type_combo.get(),
            category=self.category_combo.get(),
            subcategory=None,
            account=self.account_combo.get(),
            description=self.description_entry.get().strip() or None,
        )

        append_transaction_to_csv(tx)
        self.amount_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.app.refresh_all()

    def refresh(self) -> None:
        """Обновляет таблицу транзакций."""
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        transactions = load_transactions_from_csv()
        sorted_tx = sorted(transactions, key=lambda t: t.datetime, reverse=True)

        header = ctk.CTkFrame(self.table_scroll, fg_color="transparent", height=24)
        header.pack(fill="x", pady=(0, 5))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Дата", width=90, font=ctk.CTkFont(weight="bold")).pack(
            side="left"
        )
        ctk.CTkLabel(header, text="Сумма", width=80, font=ctk.CTkFont(weight="bold")).pack(
            side="left"
        )
        ctk.CTkLabel(header, text="Тип", width=70, font=ctk.CTkFont(weight="bold")).pack(
            side="left"
        )
        ctk.CTkLabel(header, text="Категория", width=100, font=ctk.CTkFont(weight="bold")).pack(
            side="left"
        )
        ctk.CTkLabel(header, text="Счёт", width=90, font=ctk.CTkFont(weight="bold")).pack(
            side="left"
        )
        ctk.CTkLabel(header, text="Описание", font=ctk.CTkFont(weight="bold")).pack(
            side="left", fill="x", expand=True
        )
        ctk.CTkLabel(header, text="", width=120, font=ctk.CTkFont(weight="bold")).pack(
            side="right"
        )

        for tx in sorted_tx:
            row = ctk.CTkFrame(self.table_scroll, fg_color="transparent", height=28)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=tx.datetime.strftime("%d.%m.%Y %H:%M"), width=90).pack(
                side="left"
            )
            amount_str = f"{tx.amount:,.2f}"
            ctk.CTkLabel(row, text=amount_str, width=80).pack(side="left")
            ctk.CTkLabel(row, text=tx.type, width=70).pack(side="left")
            ctk.CTkLabel(row, text=tx.category, width=100).pack(side="left")
            ctk.CTkLabel(row, text=tx.account, width=90).pack(side="left")
            desc = (tx.description or "")[:50]
            ctk.CTkLabel(row, text=desc).pack(side="left", fill="x", expand=True)

            edit_btn = ctk.CTkButton(row, text="Ред.", width=50, command=lambda: None)
            edit_btn.pack(side="right", padx=2)
            del_btn = ctk.CTkButton(row, text="Удал.", width=50, command=lambda: None)
            del_btn.pack(side="right")
