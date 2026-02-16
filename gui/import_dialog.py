"""Диалог импорта CSV с маппингом колонок."""

from datetime import datetime
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk
import pandas as pd

from models import Transaction
from storage import append_transaction_to_csv, load_transactions_from_csv

REQUIRED_FIELDS = [
    ("datetime", "Дата/время"),
    ("amount", "Сумма"),
    ("type", "Тип (Доход/Расход)"),
    ("category", "Категория"),
    ("subcategory", "Подкатегория"),
    ("account", "Счёт"),
    ("description", "Описание"),
]


class ImportDialog(ctk.CTkToplevel):
    """Окно импорта CSV с предпросмотром и маппингом."""

    def __init__(self, parent: ctk.CTk, on_import_done: Callable[[], None]) -> None:
        super().__init__(parent)
        self.on_import_done = on_import_done
        self.df: pd.DataFrame | None = None
        self.file_path: str | None = None

        self.title("Импорт CSV")
        self.geometry("900x600")
        self.minsize(700, 500)

        self._build_ui()

    def _build_ui(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            top,
            text="Выбрать файл CSV",
            command=self._select_file,
            width=150,
        ).pack(side="left", padx=(0, 10))

        self.file_label = ctk.CTkLabel(top, text="Файл не выбран", text_color="gray")
        self.file_label.pack(side="left")

        ctk.CTkLabel(
            self,
            text="Маппинг колонок",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.mapping_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mapping_frame.pack(fill="x", padx=10, pady=5)

        self.combos: dict[str, ctk.CTkComboBox] = {}
        for i, (field_id, field_label) in enumerate(REQUIRED_FIELDS):
            row = ctk.CTkFrame(self.mapping_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{field_label}:", width=180).pack(side="left", padx=(0, 5))
            combo = ctk.CTkComboBox(row, values=["— Не использовать —"], width=200)
            combo.pack(side="left")
            self.combos[field_id] = combo

        ctk.CTkLabel(
            self,
            text="Предпросмотр",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(15, 5))

        self.preview_scroll = ctk.CTkScrollableFrame(self, height=200, fg_color="transparent")
        self.preview_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=15)

        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="Импортировать",
            command=self._do_import,
            width=150,
            state="disabled",
        )
        self.import_btn.pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy, width=100).pack(side="left")

    def _select_file(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("Все файлы", "*.*")],
            title="Выберите CSV файл",
        )
        if not path:
            return

        def read_csv_safe(p: str, enc: str) -> pd.DataFrame | None:
            try:
                return pd.read_csv(p, encoding=enc, on_bad_lines="skip")
            except TypeError:
                return pd.read_csv(p, encoding=enc, error_bad_lines=False)
            except Exception:
                return None

        self.df = read_csv_safe(path, "utf-8") or read_csv_safe(path, "cp1251")
        if self.df is None:
            self.file_label.configure(text="Ошибка чтения файла", text_color="red")
            return

        self.file_path = path
        self.file_label.configure(text=path, text_color="inherit")

        columns = list(self.df.columns)
        combo_values = ["— Не использовать —"] + columns

        for combo in self.combos.values():
            combo.configure(values=combo_values)

        self._update_preview()
        self.import_btn.configure(state="normal")

    def _update_preview(self) -> None:
        """Обновляет предпросмотр таблицы."""
        for widget in self.preview_scroll.winfo_children():
            widget.destroy()

        if self.df is None or self.df.empty:
            ctk.CTkLabel(
                self.preview_scroll,
                text="Нет данных для предпросмотра.",
                text_color="gray",
            ).pack(anchor="w")
            return

        headers = list(self.df.columns)
        header_row = ctk.CTkFrame(self.preview_scroll, fg_color="transparent", height=24)
        header_row.pack(fill="x", pady=(0, 5))
        header_row.pack_propagate(False)
        for h in headers[:8]:
            ctk.CTkLabel(header_row, text=str(h)[:15], width=100, font=ctk.CTkFont(weight="bold")).pack(
                side="left"
            )

        for _, row in self.df.head(20).iterrows():
            r = ctk.CTkFrame(self.preview_scroll, fg_color="transparent", height=22)
            r.pack(fill="x", pady=1)
            r.pack_propagate(False)
            for v in row[:8]:
                ctk.CTkLabel(r, text=str(v)[:15] if pd.notna(v) else "", width=100).pack(
                    side="left"
                )

    def _parse_datetime(self, val: str) -> datetime | None:
        """Парсит дату из строки."""
        if pd.isna(val) or str(val).strip() == "":
            return None
        val = str(val).strip()
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M", "%d.%m.%Y", "%d/%m/%Y"]:
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue
        return None

    def _parse_amount(self, val) -> float:
        """Парсит сумму."""
        if pd.isna(val):
            return 0.0
        s = str(val).replace(",", ".").replace(" ", "").replace("\xa0", "")
        try:
            return float(s)
        except ValueError:
            return 0.0

    def _detect_type(self, val: str, amount: float) -> str:
        """Определяет тип по значению или по знаку суммы."""
        if pd.isna(val):
            return "Доход" if amount > 0 else "Расход"
        v = str(val).lower()
        if "доход" in v or "income" in v or "приход" in v:
            return "Доход"
        if "расход" in v or "expense" in v or "списание" in v:
            return "Расход"
        return "Доход" if amount > 0 else "Расход"

    def _get_row_val(self, row: pd.Series, col_name: str | None):
        """Получает значение из строки по имени колонки."""
        if not col_name or col_name not in row.index:
            return None
        return row[col_name]

    def _do_import(self) -> None:
        """Выполняет импорт с маппингом."""
        if self.df is None or self.file_path is None:
            return

        existing = load_transactions_from_csv()
        existing_keys = {
            (t.datetime.strftime("%Y-%m-%d %H:%M"), t.amount, t.account, t.description or "")
            for t in existing
        }

        col_map = {}
        for field_id, combo in self.combos.items():
            val = combo.get()
            if val and val != "— Не использовать —":
                col_map[field_id] = val

        if "amount" not in col_map:
            return

        for _, row in self.df.iterrows():
            amount_raw = self._get_row_val(row, col_map.get("amount"))
            amount = abs(self._parse_amount(amount_raw))

            dt_val = self._get_row_val(row, col_map.get("datetime"))
            dt = self._parse_datetime(str(dt_val)) if dt_val is not None else datetime.now()

            type_val = str(self._get_row_val(row, col_map.get("type")) or "")
            tx_type = self._detect_type(type_val, self._parse_amount(amount_raw))

            category = str(self._get_row_val(row, col_map.get("category")) or "Прочее")
            subcategory = self._get_row_val(row, col_map.get("subcategory"))
            if subcategory is None or str(subcategory) in ("nan", ""):
                subcategory = None
            else:
                subcategory = str(subcategory)

            account = str(self._get_row_val(row, col_map.get("account")) or "Сбер")
            description = self._get_row_val(row, col_map.get("description"))
            if description is None or str(description) in ("nan", ""):
                description = None
            else:
                description = str(description)

            key = (dt.strftime("%Y-%m-%d %H:%M"), amount, account, description or "")
            if key in existing_keys:
                continue

            tx = Transaction(
                datetime=dt,
                amount=amount,
                type=tx_type,
                category=category,
                subcategory=subcategory,
                account=account,
                description=description,
            )
            append_transaction_to_csv(tx)
            existing_keys.add(key)

        self.on_import_done()
        self.destroy()
