import gettext
import logging
import os
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox

# —— Project Imports —— #
from config_manager import read_config, write_config
from log import setup_logger

from data_defaults import DataDefaults
from gui_factory import Factory, handle_gui_error
from main_controller import MainController
from product_manager import ProductContext, ProductManager

# —— Setup Language —— #
logger = logging.getLogger(__name__)


class SetupLanguage:
    """
    Класс инициализирует языковой перевод приложения, используя gettext.
    """

    def __init__(self, error_handler: Callable[[str, str], None] | None = None):
        """
        Args:
            error_handler (Optional[Callable[[str, str], None]]):
                Обработчик ошибок. По умолчанию отображается через messagebox.
        """
        self.log = logger.error
        self.log_info = logger.info
        self.error_message = error_handler or messagebox.showerror

    @handle_gui_error("Ошибка")
    def setup_language(self, language_code: str):
        """
        Загружает и применяет файл перевода для указанного языка.

        Args:
            language_code (str): Код языка (например, 'ru', 'en').
        """
        global _  # очень важно — объявить здесь, чтобы изменять глобальную переменную

        locale_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "locales")
        )

        try:
            lang = gettext.translation(
                domain="messages",
                localedir=locale_dir,
                languages=[language_code],
                fallback=True,
            )
            lang.install()
            _ = lang.gettext
        except FileNotFoundError:

            def _(s):
                return s  # fallback — просто возвращает строку без перевода

            error_message = _("Файл перевода не найден.")
            self.log(error_message)
            self.error_message(_("Ошибка"), error_message)


class Localization(SetupLanguage):
    """
    Класс управления локализацией с графическим интерфейсом выбора языка.
    """

    def __init__(self, error_handler=None):
        super().__init__(error_handler=error_handler)

    def init_window(self):
        """Инициализирует графическое окно выбора языка."""
        self.root = tk.Tk()
        self.root.title("Выбор Языка / Set Language")
        self.root.geometry("500x350")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, columnspan=1, pady=10, padx=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        buttons = [
            ("Russian/Русский", lambda: self.apply_language_and_start("ru")),
            ("English/Английский", lambda: self.apply_language_and_start("en")),
            ("Exit/Выход", self._on_close),
        ]

        for idx, (text, command) in enumerate(buttons):
            style = {"fg": "white", "relief": "flat", "font": ("Arial", 12, "bold")}
            grid = {"column": 0, "padx": 10, "pady": 10, "sticky": "ew", "row": idx}
            bg_color = {
                "Russian/Русский": "#4CAF50",
                "English/Английский": "#2196f3",
            }.get(text, "#f44336")

            tk.Button(frame, text=text, command=command, bg=bg_color, **style).grid(
                **grid
            )
            frame.grid_rowconfigure(idx, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.root.mainloop()

    def start_application_with_language(self, language_code: str, root: tk.Tk = None):
        """
        Запускает приложение с выбранной локализацией.

        Args:
            language_code (str): Выбранный язык.
        """
        if root:
            factory = Factory(language_code)
            factory.window_status(root, "hide")
            settings = DataDefaults(language_code)
            context = ProductContext(language_code)
            manager = ProductManager(context)
            root.destroy()
        # Здесь инициализируется основное приложение.
        setup_logger()
        msg = _("Выбранный язык: {language_code}").format(language_code=language_code)
        self.log_info(msg)
        main = MainController(language_code)
        main.run()

    @handle_gui_error("Ошибка")
    def _on_close(self):
        """Закрывает окно приложения."""
        if self.root:
            self.root.destroy()
        else:
            self.error_message(_("Ошибка"), _("Экземпляр tkinter не существует."))

    def apply_language_and_start(self, language_code: str):
        """
        Применяет выбранный язык и запускает приложение.

        Args:
            language_code (str): Код выбранного языка.
        """
        write_config(language_code)
        self.setup_language(language_code)
        self.start_application_with_language(language_code, self.root)

    def run(self):
        """
        Основная точка запуска модуля локализации.
        Если сохранён язык — запускается сразу приложение, иначе — окно выбора.
        """
        saved_language, file_paths = read_config()
        if saved_language:
            self.setup_language(saved_language)
            self.start_application_with_language(saved_language)
        else:
            self.init_window()
