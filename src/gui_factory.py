import json
import logging
import os
import tkinter as tk
import traceback
from collections.abc import Callable

# from gettext import gettext as _
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from data_defaults import DataDefaults

logger = logging.getLogger(__name__)


def handle_gui_error(msg: str):
    """
    Обертывает методы GUI с единой логикой обработки ошибок.

    Регистрирует исключение с сообщением и показывает пользователю общий диалог ошибки.

    Предполагается, что `self` имеет `error_message(title: str, text: str)`.

    Аргументы:
    msg (str): Контекстно-зависимый префикс для сообщения журнала.

    Возвращает:
    Вызываемый: Декорированная функция.
    """

    def decorator(func: Callable):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                error_details = f"{msg}: {e}\n{traceback.format_exc()}"
                error_title = _("Ошибка:")
                error_msg = _("{error}").format(error=str(e))
                logger.error(error_details)
                self.error_message(error_title, error_msg)
                return None

        return wrapper

    return decorator


def set_window_icon(window: tk.Widget = None):
    if window is None:
        logger.error(_("Ошибка: Не указан экземпляр Tkinter."))
        return

    script_dir = Path(__file__).resolve().parent
    icon_path = script_dir.parent / "resources" / "icon.ico"

    if icon_path.exists():
        window.iconbitmap(icon_path)
    else:
        logger.warning(
            _("Иконка {icon_path} не найдена. Используется стандартная иконка.").format(
                icon_path=icon_path
            )
        )


class WidgetFactory:
    def __init__(self, bg_color: str = "#f0f8ff"):
        self.bg_color = bg_color

    def create_widgets(
        self, cls: type[tk.Widget], frame: tk.Widget | None = None, **kwargs
    ) -> tk.Widget | None:
        if not isinstance(cls, type):
            raise ValueError("Ошибка: cls должен быть классом.")

        if cls in [tk.Tk, tk.Toplevel]:
            return self._create_window(cls, **kwargs)

        if frame is None:
            raise ValueError(
                f"Ошибка: Для создания виджета {cls.__name__} необходимо указать frame (родительский контейнер)."
            )

        elif cls is tk.Frame and kwargs.get("is_scrollable", False):
            return self._create_scrollable_frame(frame)

        elif cls is ttk.Combobox:
            return self._create_combo(cls, frame, **kwargs)

        else:
            return self._create_widget(cls, frame, **kwargs)

    def _create_window(
        self, cls: type[tk.Tk | tk.Toplevel], **kwargs
    ) -> tk.Widget | None:
        """
        Создаёт и возвращает новое окно (tk.Tk или tk. Toplevel).

        Аргументы kwargs:
            - title (str): Заголовок окна.
            - size (str): Размер окна, например "800x600".
            - resizable (bool или tuple): Разрешить изменение размера окна.
        """
        title = kwargs.get("title", "Новое Окно")
        size = kwargs.get("size", "500x350")
        resizable = kwargs.get("resizable", (False, False))

        window = cls()
        window.title(title)
        window.geometry(size)
        window.resizable(*resizable)
        window.configure(bg=self.bg_color)
        set_window_icon(window)
        return window

    def _create_scrollable_frame(self, frame: tk.Frame) -> tk.Frame:
        """
        Создает Скроллируемый Фрейм внутри родительского контейнера
        :param frame: Родительский контейнер
        :return: Фрейм с вертикальной поддержкой
        """
        canvas = tk.Canvas(frame, background=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, background=self.bg_color)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        return scrollable_frame

    def _create_widget(
        self, cls: type[tk.Widget], frame: tk.Widget | None, **kwargs
    ) -> tk.Widget | None:
        """Создает виджеты такие, как Button Frame Label и так далее"""
        style_option = kwargs.pop("style", {})
        grid_option = kwargs.pop("grid", {})
        place_option = kwargs.pop("place", {})
        pack_option = kwargs.pop("pack", {})

        try:
            widget = cls(frame, **style_option, **kwargs)

            if grid_option:
                if any(v is None for v in grid_option.values()):
                    raise ValueError("Ошибка размещения виджета: grid содержит None")
                widget.grid(**grid_option)
            elif pack_option:
                if any(v is None for v in pack_option.values()):
                    raise ValueError("Ошибка размещения виджета: pack содержит None")
                widget.pack(**pack_option)
            elif place_option:
                if any(v is None for v in place_option.values()):
                    raise ValueError("Ошибка размещения виджета: place содержит None")
                widget.place(**place_option)

            return widget
        except Exception as e:
            raise ValueError(f"Ошибка размещения виджета: {str(e)}")

    def _create_combo(self, cls: type[ttk.Combobox], frame: tk.Widget | None, **kwargs):
        style_option = kwargs.pop("style", {})
        grid_option = kwargs.pop("grid", {})

        try:
            widget = cls(frame, **style_option, **kwargs)
            if grid_option:
                if any(v is None for v in grid_option.values()):
                    raise ValueError("Ошибка размещения виджета: grid содержит None")
                widget.grid(**grid_option)
            return widget
        except Exception as e:
            raise ValueError(f"Ошибка размещения виджета: {str(e)}")


class WidgetBuilder(WidgetFactory):
    def __init__(self, bg_color: str = "#f0f8ff"):
        super().__init__(bg_color)

    def create_button(
        self, window: tk.Widget, text: str, command: Callable, **kwargs
    ) -> tk.Button | None:
        return self.create_widgets(
            tk.Button, frame=window, text=text, command=command, **kwargs
        )

    def create_label(self, window: tk.Widget, text: str, **kwargs) -> tk.Label | None:
        return self.create_widgets(tk.Label, frame=window, text=text, **kwargs)

    def create_entry(self, window: tk.Widget, **kwargs) -> tk.Entry | None:
        return self.create_widgets(tk.Entry, frame=window, **kwargs)

    def create_frame(self, window: tk.Widget, **kwargs) -> tk.Frame | None:
        return self.create_widgets(tk.Frame, frame=window, **kwargs)

    def create_scrollable_frame(self, window: tk.Widget, **kwargs) -> tk.Frame | None:
        return self.create_widgets(tk.Frame, frame=window, is_scrollable=True, **kwargs)

    def create_listbox(self, window: tk.Widget, **kwargs) -> tk.Listbox | None:
        return self.create_widgets(tk.Listbox, frame=window, **kwargs)

    def create_combobox(self, window: tk.Widget, **kwargs) -> ttk.Combobox | None:
        return self.create_widgets(ttk.Combobox, frame=window, **kwargs)


class Factory(WidgetFactory):
    def __init__(
        self,
        language: str,
        info_handler: Callable[[str, str], None] | None = None,
        error_handler: Callable[[str, str], None] | None = None,
    ):
        """
        Инициализирует помощник GUI с дополнительными обработчиками ошибок/информации.

        Аргументы:
        error_handler (Callable): Пользовательская функция для отображения сообщений об ошибках.
        Info_handler (Callable): Пользовательская функция для отображения информационных сообщений.
        """
        super().__init__(bg_color="#f0f8ff")
        self.log = logger.error
        self.log_info = logger.info
        self.info_message = info_handler or messagebox.showinfo
        self.error_message = error_handler or messagebox.showerror
        self.language = language
        self.settings = DataDefaults(self.language)

    @handle_gui_error("Ошибка")
    def window_status(self, root: tk.Tk | tk.Toplevel, action: str) -> None:
        """
        Скрывает или показывает окно Tkinter в зависимости от действия.

        Аргументы:
        root (tk. Tk | tk. Toplevel): Окно для работы.
        Action (str): Одно из значений «hide» или «show».

        Вызывает:
        ValueError: Если root — None или действие недопустимо.
        """
        if root is None and action is None:
            raise ValueError("Ошибка, Нет рабочего окна и не указано действие.")
        if root is None:
            raise ValueError("Ошибка, Не валидный тип окна.")
        match action:
            case "hide":
                root.withdraw()
            case "show":
                root.deiconify()
            case _:
                raise ValueError(
                    "Ошибка, Некорректное значение. Используйте 'hide' или 'show'."
                )

    @handle_gui_error("Ошибка")
    def on_close(self, root: tk.Tk | tk.Toplevel, window: tk.Toplevel = None) -> None:
        """
        Чисто завершает приложение или закрывает дочернее окно.

        Аргументы:
        root (tk. Tk | tk. Toplevel): Главное/корневое окно.
        Window (tk. Toplevel, необязательно): Дочернее окно. Если не указано, закрывает корневое окно.
        """
        if root is None and window is None:
            raise ValueError("Ошибка, 'root' и 'window' не указаны.")
        if root is None:
            raise ValueError("Ошибка, Нет рабочего окна.")
        if window is not None:
            window.destroy()
            if not any(
                w.winfo_exists() and w.winfo_ismapped() for w in root.winfo_children()
            ):
                root.quit()
                root.destroy()
        else:
            root.quit()
            root.destroy()

    @handle_gui_error("Ошибка")
    def restore_root_window(
        self, root: tk.Tk | tk.Toplevel, window: tk.Toplevel = None
    ) -> None:
        """
        Закрывает дочернее окно и возвращает корневое окно обратно в вид.

        Аргументы:
        root (tk. Tk | tk. Toplevel): Главное/корневое окно.
        Window (tk. Toplevel): Дочернее окно для закрытия.
        """
        if root is None and window is None:
            raise ValueError("Ошибка, Нет рабочего окна.")
        if root is None:
            raise ValueError("Ошибка, Не валидный тип окна.")
        if window is not None:
            window.destroy()
        self.window_status(root, "show")

    @handle_gui_error("Ошибка")
    def read_and_write_file(
        self, file_path: str, method: str, data: Any = None
    ) -> Any | None:
        """
        Читает или записывает в файл JSON.

        Аргументы:
        file_path (str): Путь к файлу.
        flag (str): 'r' для чтения, 'w' для записи.
        data (Any, необязательно): Данные для записи, если flag равен 'w'.

        Возвращает:
        Any: Проанализированный JSON при чтении; True, если запись прошла успешно.

        Вызывает:
        ValueError: Если flag недействителен или data содержит значения None.
        """
        if method == "r":
            with open(file_path, method, encoding="utf-8") as f:
                return json.load(f)
        elif method == "w":
            if data is not None:
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key is None and value is None:
                            raise ValueError("Ошибка, Нет ключа и данных.")
                        if value is None:
                            raise ValueError(
                                f"Значение для ключа '{key}' не может быть None"
                            )
                        if key is None:
                            raise ValueError("Ошибка, Ключ отсутствует или поврежден")

                with open(file_path, method, encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    return True
            return None
        else:
            raise ValueError(f"Неподдерживаемый метод: {method}")

    @handle_gui_error("Ошибка")
    def save_results(
        self, file_path: str, entries: list[tuple[str, float, float]]
    ) -> None:
        """
        Сохраняет записи о приеме пищи и общее количество калорий в файл JSON.

        Аргументы:
        записи (список кортежа): Каждый элемент — это (имя, вес, калории).
        File_path (str): Путь к файлу для сохранения результатов.

        Побочные эффекты:
        Обновляет файл, показывает диалоговое окно информации.

        Примечания:
        Пропускает сохранение, если записи неправильно сформированы.
        """
        if not all(isinstance(e, list | tuple) and len(e) == 3 for e in entries):
            self.error_message(
                _("Ошибка"), _("Некорректный формат данных для сохранения.")
            )
            return

        total = sum(c for _, _, c in entries)
        meals_data = {
            "timestamp": datetime.now().isoformat(),
            "items": [{"name": n, "weight": w, "calories": c} for n, w, c in entries],
            "total": total,
        }

        existing_data = []
        if os.path.exists(file_path):
            existing_data = self.read_and_write_file(file_path, "r") or []

        existing_data.append(meals_data)
        self.read_and_write_file(file_path, "w", existing_data)
        msg_title = _("Успех")
        message = _("Данные сохранены в {file_path}").format(file_path=file_path)
        self.info_message(msg_title, message)

    @handle_gui_error("Ошибка")
    def reset_config_settings(self):
        from config_manager import reset_config

        reset_config()
        self.info_message(_("Успех"), _("Языковые настройки сброшены!"))
        self.info_message(_("Инфо"), _("Приложение будет закрыто."))
        self.log_info(_("Успешно: языковые настройки сброшены."))
        quit()
