"""Главное окно приложения."""

import customtkinter as ctk

from gui.dashboard import DashboardTab
from gui.transactions import TransactionsTab
from gui.reports import ReportsTab
from gui.goals import GoalsTab


class App(ctk.CTk):
    """Главное окно Finance Rush."""

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.title("Finance Rush — Личный финансовый трекер")
        self.minsize(900, 600)
        self.geometry("1000x700")

        self._build_ui()

    def _build_ui(self) -> None:
        """Создаёт интерфейс с вкладками."""
        self.tabview = ctk.CTkTabview(self, width=880, height=650)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Дашборд")
        self.tabview.add("Транзакции")
        self.tabview.add("Отчёты")
        self.tabview.add("Цели")

        self.dashboard_tab = DashboardTab(self.tabview.tab("Дашборд"), self)
        self.transactions_tab = TransactionsTab(self.tabview.tab("Транзакции"), self)
        self.reports_tab = ReportsTab(self.tabview.tab("Отчёты"), self)
        self.goals_tab = GoalsTab(self.tabview.tab("Цели"), self)

    def refresh_all(self) -> None:
        """Обновляет все вкладки после изменения данных."""
        self.dashboard_tab.refresh()
        self.transactions_tab.refresh()
        self.reports_tab.refresh()
        self.goals_tab.refresh()
