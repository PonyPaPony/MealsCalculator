import logging
import os
import tkinter as tk
from tkinter import messagebox

from autocomplete import Autocomplete
from data_defaults import DataDefaults

# from gettext import gettext as _
from gui_factory import Factory, WidgetBuilder, handle_gui_error

logger = logging.getLogger(__name__)
SUPPORTED_LANGUAGES = {"ru", "en"}


class ProductContext:
    def __init__(self, language: str, factory=None, builder=None, settings=None):
        self.language = language
        self.factory = factory or Factory(language)
        self.builder = builder or WidgetBuilder(language)
        self.settings = settings or DataDefaults(language)


class ProductManagerGUI:
    def __init__(
        self, context: ProductContext, products, info_message=None, error_message=None
    ):
        self.context = context
        self.products = products
        self.language = context.language

        self.builder = context.builder
        self.factory = context.factory
        self.settings = context.settings

        self.setup = Autocomplete()

        self.log = logger.error
        self.info_message = info_message or messagebox.showinfo
        self.error_message = error_message or messagebox.showerror

    @handle_gui_error("Ошибка")
    def root_for_window(self, window: tk.Toplevel, tag: str):
        if not window:
            raise ValueError("Отсутствует экземпляр Tkinter")
        if not tag:
            raise ValueError("Не указан тэг действия")
        match tag:
            case "Append":
                self.open_add_products_window(window)
            case "Change":
                self.open_change_products_window(window)
            case "Delete":
                self.open_del_products_window(window)
            case _:
                self.log(f"Ошибка: Неизвестный таг действия — {tag}")
                raise ValueError(f"Неизвестный таг действия: {tag}")

    @handle_gui_error("Ошибка")
    def open_add_products_window(self, root: tk.Tk | tk.Toplevel = None):
        self.factory.window_status(root, "hide")
        win = self.factory.create_widgets(
            cls=tk.Toplevel, title=_("Добавить продукт"), size="300x150"
        )
        win.protocol(
            "WM_DELETE_WINDOW", lambda: self.factory.on_close(root=root, window=win)
        )
        frame = self.builder.create_frame(window=win, grid={**self.settings.frame_grid})

        self.builder.create_label(
            frame,
            text=_("Название продукта:"),
            style={**self.settings.font_10},
            grid={**self.settings.label_grid},
        )
        self.builder.create_label(
            frame,
            text=_("Калорийность:"),
            style={**self.settings.font_10},
            grid={**self.settings.label_grid, "row": 1},
        )

        entry_name = self.builder.create_entry(frame, grid={**self.settings.entry_grid})
        entry_kcal = self.builder.create_entry(
            frame, grid={**self.settings.entry_grid, "row": 1}
        )

        def submit():
            name = entry_name.get().strip()
            if name in self.products:
                self.info_message(_("Внимание"), _("Такой продукт уже существует."))
                return
            if not name:
                self.error_message(
                    _(
                        "Ошибка",
                    ),
                    _("Поле продукта не может быть пустым."),
                )
                return
            kcal = entry_kcal.get().strip()
            is_valid, kcal_value = self.validate_product_input(name, kcal)
            if is_valid:
                self.update_product_data(name, kcal_value)
                self.info_message(
                    _("Успех"),
                    _("Добавлен {n} с калорийностью {kcal}.").format(
                        n=name, kcal=kcal_value
                    ),
                )
            else:
                self.error_message(_("Внимание"), _("Неверный формат калорийности."))
                return

        self.builder.create_button(
            frame,
            text=_("Сохранить"),
            command=submit,
            style={**self.settings.font_12, **self.settings.green},
            grid={**self.settings.button_grid, "row": 2},
        )
        self.builder.create_button(
            frame,
            text=_("Назад"),
            command=lambda: self.factory.restore_root_window(root=root, window=win),
            style={**self.settings.font_12, **self.settings.red},
            grid={**self.settings.button_grid, "row": 2, "column": 1},
        )

        for i in range(2):
            win.grid_rowconfigure(i, weight=1)
            win.grid_columnconfigure(i, weight=1)

    @handle_gui_error("Ошибка")
    def open_del_products_window(self, root: tk.Tk | tk.Toplevel = None):
        self.factory.window_status(root, "hide")
        win = self.factory.create_widgets(
            cls=tk.Toplevel, title=_("Удалить продукт"), size="400x350"
        )
        win.protocol(
            "WM_DELETE_WINDOW", lambda: self.factory.on_close(root=root, window=win)
        )
        frame = self.builder.create_frame(window=win, grid={**self.settings.frame_grid})

        self.builder.create_label(
            frame,
            text=_("Продукт для удаления:"),
            style={**self.settings.font_10},
            grid={**self.settings.label_grid},
        )
        entry = self.builder.create_entry(frame, grid={**self.settings.entry_grid})

        listbox = self.builder.create_listbox(
            frame,
            style={**self.settings.listbox_style},
            grid={**self.settings.listbox_grid},
        )

        self.setup.setup_autocomplete(entry, self.products, listbox)

        def delete():
            name = entry.get().strip()
            if not name:
                self.error_message(_("Ошибка"), _("Введите название продукта."))
                return
            elif name in self.products:
                del self.products[name]
                self._save_products(self.language)
                self.info_message(
                    _("Успех"), _("Продукт {name} удалён.").format(name=name)
                )
            else:
                self.error_message(
                    _("Ошибка"), _("Продукт {name} не найден.").format(name=name)
                )

        btn_frame = self.builder.create_frame(
            win, grid={**self.settings.frame_grid, "row": 1, "sticky": "ew"}
        )
        self.builder.create_button(
            btn_frame,
            text=_("Удалить"),
            command=delete,
            style={**self.settings.font_12, **self.settings.red},
            grid={**self.settings.listbox_button},
        )
        self.builder.create_button(
            btn_frame,
            text=_("Назад"),
            command=lambda: self.factory.restore_root_window(root=root, window=win),
            style={**self.settings.font_12, **self.settings.blue},
            grid={**self.settings.listbox_button_second},
        )

        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)
        btn_frame.grid_rowconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(0, weight=2)
        btn_frame.grid_columnconfigure(1, weight=1)

    @handle_gui_error("Ошибка")
    def open_change_products_window(self, root: tk.Tk | tk.Toplevel = None):
        self.factory.window_status(root, "hide")
        win = self.factory.create_widgets(
            cls=tk.Toplevel, title=_("Изменить калорийность"), size="400x350"
        )
        win.protocol(
            "WM_DELETE_WINDOW", lambda: self.factory.on_close(root=root, window=win)
        )
        frame = self.builder.create_frame(window=win, grid={**self.settings.frame_grid})

        self.builder.create_label(
            frame,
            text=_("Продукт:"),
            style={**self.settings.font_10},
            grid={**self.settings.label_grid},
        )
        self.builder.create_label(
            frame,
            text=_("Новая калорийность:"),
            style={**self.settings.font_10},
            grid={**self.settings.label_grid, "row": 1},
        )

        entry_product = self.builder.create_entry(
            frame, grid={**self.settings.entry_grid}
        )
        entry_kcal = self.builder.create_entry(
            frame, grid={**self.settings.entry_grid, "row": 1}
        )

        listbox = self.builder.create_listbox(
            frame,
            style={**self.settings.listbox_style},
            grid={**self.settings.listbox_grid, "row": 2},
        )

        self.setup.setup_autocomplete(entry_product, self.products, listbox)

        def update():
            name = entry_product.get().strip()
            if not name:
                self.error_message(_("Ошибка"), _("Введите название продукта."))
                return
            elif name not in self.products:
                self.error_message(
                    _("Ошибка"), _("Продукт {n} не найден.").format(n=name)
                )
            kcal = entry_kcal.get()
            if not kcal:
                self.error_message(_("Ошибка"), _("Введите калории для продукта."))
                return
            is_valid, kcal_value = self.validate_product_input(name, kcal)
            if is_valid:
                self.update_product_data(name, kcal_value)
                self.info_message(
                    _("Успех"), _("Калорийность {n} обновлена.").format(n=name)
                )

        btn_frame = self.builder.create_frame(
            win, grid={**self.settings.frame_grid, "row": 3, "sticky": "ew"}
        )
        self.builder.create_button(
            btn_frame,
            text=_("Изменить"),
            command=update,
            style={**self.settings.font_12, **self.settings.green},
            grid={**self.settings.listbox_button, "row": 3},
        )
        self.builder.create_button(
            btn_frame,
            text=_("Назад"),
            command=lambda: self.factory.restore_root_window(root=root, window=win),
            style={**self.settings.font_12, **self.settings.red},
            grid={**self.settings.listbox_button_second, "row": 3},
        )

        for i in range(3):
            win.grid_rowconfigure(i, weight=1)
        win.grid_columnconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)
        for i in range(1):
            btn_frame.grid_columnconfigure(i, weight=1)


class ProductManager(ProductManagerGUI):
    def __init__(self, context: ProductContext, info_message=None, error_message=None):
        super().__init__(context, [], info_message, error_message)
        self.products = self._load_products_internal(context.language)

    @handle_gui_error("Ошибка")
    def _save_products(self, language: str):
        """
        Функция записи новых продуктов в файл
        :param language: язык активного перевода для определения путей
        """
        if not language:
            raise ValueError("Ошибка: Не указан параметр языка.")
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError("Ошибка: Указанный перевод не доступен.")

        file_paths = {
            "ru": self.settings.PRODUCTS_LIST_RU,
            "en": self.settings.PRODUCTS_LIST_EN,
        }

        file_path = file_paths.get(language)
        self.factory.read_and_write_file(file_path, "w", self.products)
        self.info_message(_("Успех"), _("Продукты сохранены!"))

    @handle_gui_error("Ошибка")
    def _load_products_internal(self, language: str):
        """
        Функция загружает список продуктов из файла
        :param language: параметр перевода по которому определяем откуда загружать список продуктов
        :return: возвращаем загруженный список продуктов
        """
        if not language:
            raise ValueError("Ошибка: Не указан параметр языка.")
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError("Ошибка: Указанный перевод не доступен.")

        file_paths = {
            "ru": self.settings.PRODUCTS_LIST_RU,
            "en": self.settings.PRODUCTS_LIST_EN,
        }

        file_path = file_paths.get(language)
        if not os.path.exists(file_path):
            return self.settings.ensure_file_with_defaults(language)
        return self.factory.read_and_write_file(file_path, "r")

    @handle_gui_error("Ошибка")
    def validate_product_input(self, name: str, kcal: str) -> tuple[bool, float | None]:
        """
        Проверяем корректность ввода.
        :param name: Наименование продукта
        :param kcal: Значение калорий (должно быть положительным числом)
        :return: возвращаем True и float(kcal) если данные переданы правильно. Иначе False, None
        """
        if not name or not kcal:
            self.error_message(_("Ошибка"), _("Название и калорийность обязательны."))
            return False, None
        try:
            return True, float(kcal)
        except ValueError:
            self.error_message(
                _("Ошибка"),
                _("Калорийность {kcal} не является числом.").format(kcal=kcal),
            )
            return False, None

    @handle_gui_error("Ошибка")
    def update_product_data(self, name: str, kcal: float):
        """
        Функция обновления калорийности продуктов.
        :param name: Наименование продукта
        :param kcal: Значение калорий (должно быть положительным числом)
        """
        if not name or kcal is None:
            raise ValueError("Ошибка: Неверно указаны данные name или kcal")
        if not isinstance(name, str):
            raise ValueError("Ошибка: Наименование продукта не может быть числом.")
        if not isinstance(kcal, int | float):
            raise ValueError("Ошибка: Калорийность должна быть числом.")
        if kcal <= 0:
            raise ValueError("Ошибка: Калорийность должна быть положительным числом.")

        self.products[name.title()] = kcal
        self._save_products(self.language)


class ProductCalculator(ProductManagerGUI):
    def __init__(
        self, context: ProductContext, products, info_message=None, error_message=None
    ):
        super().__init__(context, products, info_message, error_message)

    @handle_gui_error("Ошибка")
    def calculate_total(self, data):
        total = 0
        entries = []

        for product_var, weight_var in data:
            name = product_var.get().strip()
            if name not in self.products:
                raise ValueError(
                    _("Продукт '{name}' не найден в базе.").format(name=name)
                )
            try:
                weight = float(weight_var.get())
            except ValueError:
                raise ValueError("Вес должен быть числом.")
            if weight <= 0:
                raise ValueError("Вес должен быть положительным.")

            kcal = self.products[name] * weight / 100
            entries.append((name, weight, kcal))
            total += kcal

        summary = "\n".join(f"{n} — {w}g — {c:.1f} kcal" for n, w, c in entries)
        summary += f"\n\nTOTAL: {total:.1f} kcal"

        self.info_message(_("Результат"), summary)
        self.factory.save_results(file_path=self.settings.MEALS_LIST, entries=entries)

    @handle_gui_error("Ошибка")
    def create_input_product_row(self, data, frame: tk.Frame):
        if data is None:
            raise ValueError("Ошибка: Отсутствуют данные или валидное окно.")
        if not isinstance(frame, tk.Frame):
            raise ValueError("Ошибка: Окно должно быть экземпляром tk.Frame")
        if self.products == {}:
            raise ValueError("Ошибка: Список продуктов пуст или поврежден.")

        row_index = len(data)

        product_var = tk.StringVar(value=list(self.products.keys())[0])
        weight_var = tk.StringVar()

        box = self.builder.create_combobox(
            frame,
            textvariable=product_var,
            values=list(self.products.keys()),
            style={**self.settings.combo_style},
            grid={**self.settings.combo_grid, "row": row_index},
        )

        entry = self.builder.create_entry(
            frame,
            textvariable=weight_var,
            style={**self.settings.font_10},
            grid={**self.settings.entry_grid, "row": row_index, "sticky": "ew"},
        )

        def remove_row():
            box.destroy()
            entry.destroy()
            btn.destroy()
            data.remove((product_var, weight_var))

        btn = self.builder.create_button(
            frame,
            text=_("Удалить"),
            command=remove_row,
            style={**self.settings.font_10_, **self.settings.red},
            grid={**self.settings.button_grid_low, "row": row_index, "column": 2},
        )

        return product_var, weight_var
