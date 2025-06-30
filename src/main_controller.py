import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from gettext import gettext as _
from data_defaults import DataDefaults
from gui_factory import Factory, WidgetBuilder
from product_manager import ProductCalculator, ProductContext, ProductManager
from stats_manager import StatsManager

logger = logging.getLogger(__name__)


class MainController:
    def __init__(
        self,
        language: str,
        info_handler: Callable[[str, str], None] | None = None,
        error_handler: Callable[[str, str], None] | None = None,
    ):
        self.language = language
        self.info_message = info_handler or messagebox.showinfo
        self.error_message = error_handler or messagebox.showerror
        self.log = logger.error

        self.settings = DataDefaults(self.language)
        self.context = ProductContext(self.language)
        self.manager = ProductManager(self.context)
        self.calculator = ProductCalculator(self.context, self.manager.products)
        self.factory = Factory(self.language)
        self.builder = WidgetBuilder()
        self.stats_manager = StatsManager()

    def get_button_style(self, text, case=0):
        """Определяет стиль для кнопки на основе её текста"""
        style = {**self.settings.font_12, **self.settings.green}

        # Применяем особые стили для некоторых кнопок
        if case == 0:
            special_styles = {
                "Выход": self.settings.red,
                "Exit": self.settings.red,
                "Cбросить Языковые Настройки": self.settings.blue,
                "Reset Language Settings": self.settings.blue,
            }
        elif case == 1:
            special_styles = {
                "Назад": self.settings.red,
                "Back": self.settings.red,
                "Рассчитать": self.settings.blue,
                "Calculate": self.settings.blue,
            }

        # Если текст кнопки соответствует одному из ключей, меняем стиль
        style.update(special_styles.get(text, {}))

        return style

    def create_buttons(self, frame):
        """Создаёт и отображает кнопки"""
        buttons = [
            (_("Рассчитать калории"), self.open_calculate_window),
            (_("Меню управления продуктами"), self.open_manager_products_menu),
            (_("Показать статистику"), self.open_stats_menu),
            (_("Выход"), lambda: self.factory.on_close(self.root)),
            (_("Cбросить Языковые Настройки"), self.factory.reset_config_settings),
        ]

        for idx, (text, command) in enumerate(buttons):
            style = self.get_button_style(text)
            # Создаём кнопку с заданным стилем
            self.builder.create_button(
                frame,
                text,
                command,
                style=style,
                grid={**self.settings.button_grid, "row": idx},
            )
            frame.grid_rowconfigure(idx, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def _win_(self, title, size):
        self.factory.window_status(self.root, "hide")
        win = self.builder.create_widgets(cls=tk.Toplevel, title=_(title), size=size)
        win.protocol("WM_DELETE_WINDOW", lambda: self.factory.on_close(self.root, win))
        return win

    def run(self):
        self.root = self.builder.create_widgets(
            cls=tk.Tk, title=_("Главное Меню"), size="500x350"
        )
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.factory.on_close(self.root))
        main_frame = self.builder.create_frame(
            self.root, grid={**self.settings.frame_grid}
        )
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_buttons(main_frame)

        self.root.mainloop()

    def open_calculate_window(self):
        if not self.manager.products:
            self.error_message(_("Ошибка"), _("Нет продуктов для расчёта."))
            return

        win = self._win_("Рассчитать калории", "500x500")
        frame = self.builder.create_frame(win, grid={**self.settings.frame_grid})
        scrollable_area = self.builder.create_scrollable_frame(frame)
        product_rows = []

        def add_row():
            row = self.calculator.create_input_product_row(
                product_rows, scrollable_area
            )
            product_rows.append(row)
            scrollable_area.grid_rowconfigure(0, weight=1)
            scrollable_area.grid_columnconfigure(1, weight=1)

        add_row()

        btn_frame = self.builder.create_frame(
            win, grid={**self.settings.frame_grid, "row": 1}
        )

        buttons = [
            (_("+ Добавить продукт"), add_row),
            (_("Рассчитать"), lambda: self.calculator.calculate_total(product_rows)),
            (_("Назад"), lambda: self.factory.restore_root_window(self.root, win)),
        ]

        for idx, (text, command) in enumerate(buttons):
            style = self.get_button_style(text, case=1)
            grid = {**self.settings.button_grid_low, "column": idx}
            self.builder.create_button(btn_frame, text, command, style=style, grid=grid)
            btn_frame.grid_columnconfigure(idx, weight=1)
        btn_frame.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

    def open_manager_products_menu(self):
        win = self._win_("Меню управления продуктами", "500x350")
        frame = self.builder.create_frame(win, grid={**self.settings.frame_grid})

        actions = [
            (_("Добавить продукт"), "Append"),
            (_("Удалить продукт"), "Delete"),
            (_("Изменить Калорийность"), "Change"),
        ]

        for idx, (label, tag) in enumerate(actions):
            self.builder.create_button(
                frame,
                text=label,
                command=lambda t=tag: self.manager.root_for_window(win, tag=t),
                style={**self.settings.font_12, **self.settings.green},
                grid={**self.settings.button_grid, "row": idx},
            )

        self.builder.create_button(
            frame,
            text=_("Назад в меню"),
            command=lambda: self.factory.restore_root_window(self.root, win),
            style={**self.settings.font_12, **self.settings.red},
            grid={**self.settings.button_grid, "row": len(actions)},
        )

        for i in range(len(actions) + 1):
            frame.grid_rowconfigure(i, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

    def open_stats_menu(self):
        win = self._win_("Показать статистику", "500x350")
        frame = self.builder.create_frame(win, grid={**self.settings.frame_grid})

        buttons = [
            (
                _("Статистика за 7 дней:"),
                lambda: self.show_stats_window(
                    _("7 дней"), self.stats_manager.get_stats_by_period("week")
                ),
            ),
            (
                _("Статистика за 30 дней:"),
                lambda: self.show_stats_window(
                    _("30 дней"), self.stats_manager.get_stats_by_period("month")
                ),
            ),
            (_("Статистика за указанный период:"), None),  # TODO: Пока не брался за это
            (
                _("Статистика за все время:"),
                lambda: self.show_stats_window(
                    _("Все время"), self.stats_manager.get_stats_by_period("all")
                ),
            ),
            (_("Назад"), lambda: self.factory.restore_root_window(self.root, win)),
        ]

        for idx, (text, command) in enumerate(buttons):
            style = {**self.settings.font_12, **self.settings.green}
            grid = {**self.settings.button_grid, "row": idx}
            if text in ["Назад", "Back"]:
                style = {**self.settings.font_12, **self.settings.red}
            if command is None:
                style = {
                    **self.settings.font_12,
                    **self.settings.blue,
                }  # Убрать после реализации.
            self.builder.create_button(
                frame, text=text, command=command, style=style, grid=grid
            )
        for i in range(len(buttons) + 1):
            frame.grid_rowconfigure(i, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

    def show_stats_window(self, title: str, stats: list[dict]):
        win = self._win_(title, "700x500")
        frame = self.builder.create_scrollable_frame(win)

        # Если нет данных, показываем сообщение
        if not stats:
            self.builder.create_label(
                frame,
                text=_("Нет данных за указанный период"),
                grid={**self.settings.label_grid},
                style={**self.settings.font_10},
            )
            return

        # Подготовим данные для графика
        dates = []
        total_calories = []
        label_n_title = [_("Дата"), _("Итого Калорий"), _("Калорий за День")]

        for entry in stats:
            timestamp = entry.get("timestamp", "")[:10]  # Только дата без времени
            total_calories.append(entry.get("total", 0.0))
            dates.append(timestamp)

        # Создаём график
        fig, ax = plt.subplots(figsize=(6, 4))

        ax.plot(
            dates,
            total_calories,
            marker="o",
            linestyle="-",
            color="b",
            label="Calories",
        )
        ax.set_xlabel(label_n_title[0])
        ax.set_ylabel(label_n_title[1])
        ax.set_title(label_n_title[2])

        # Добавим подписи для каждой точки
        for i, txt in enumerate(total_calories):
            ax.annotate(
                f"{txt:.2f}",
                (dates[i], total_calories[i]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
            )

        ax.grid(True)
        ax.legend()

        # Встраиваем график в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)  # Создаём виджет для графика
        canvas.draw()  # Отображаем график
        canvas.get_tk_widget().grid(
            row=0, column=0, sticky="nsew"
        )  # Добавляем его в окно Tkinter

        # Настройка прокрутки
        frame.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

    def show_error(self, title: str, message: str):
        logger.error(f"{title}: {message}")
        self.error_message(title, message)
