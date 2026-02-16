"""Вкладка Цели — заглушка."""

import customtkinter as ctk


class GoalsTab:
    """Вкладка финансовых целей (заглушка)."""

    def __init__(self, parent: ctk.CTkFrame, app: "ctk.CTk") -> None:
        self.parent = parent
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self.parent,
            text="Финансовые цели",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=20)

        ctk.CTkLabel(
            self.parent,
            text="Раздел в разработке. Здесь будет отслеживание прогресса по целям.",
            text_color="gray",
        ).pack(anchor="w", padx=10, pady=10)

    def refresh(self) -> None:
        """Обновление (пока пусто)."""
        pass
