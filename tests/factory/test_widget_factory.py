import re
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch

import pytest

from gui_factory import WidgetFactory


def check_widget_placement(widget, placement_method, expected_params):
    if placement_method == "grid":
        info = widget.grid_info()
    elif placement_method == "pack":
        info = widget.pack_info()
    elif placement_method == "place":
        info = widget.place_info()
    else:
        raise ValueError(f"Неизвестный метод размещения: {placement_method}")

    for key, expected_value in expected_params.items():
        actual_value = info.get(key)
        assert str(actual_value) == str(
            expected_value
        ), f"{placement_method.capitalize()} параметр '{key}' — ожидалось '{expected_value}', получили '{actual_value}'"


widgets_all = [
    # cls, style, placement_dict, placement_type, extra_options
    (tk.Tk, {}, {}, "grid", {"title": "Test", "size": "100x100"}),
    (tk.Toplevel, {}, {}, "grid", {"title": "Test", "size": "100x100"}),
    (tk.Frame, {}, {}, "grid", {"is_scrollable": True}),
    (tk.Frame, {}, {"row": 0, "column": 0}, "grid", {}),
    (tk.Entry, {}, {"row": 1, "column": 0}, "grid", {}),
    (tk.Listbox, {}, {"row": 2, "column": 0}, "grid", {}),
    (tk.Label, {"text": "test"}, {"row": 3, "column": 0}, "grid", {}),
    (
        tk.Button,
        {"text": "test", "command": MagicMock()},
        {"row": 4, "column": 0},
        "grid",
        {},
    ),
    (ttk.Combobox, {}, {"row": 5, "column": 0}, "grid", {}),
    # Pack
    (tk.Frame, {}, {"side": "top", "fill": "x"}, "pack", {}),
    (tk.Entry, {}, {"side": "top", "fill": "x"}, "pack", {}),
    (tk.Listbox, {}, {"side": "top", "fill": "x"}, "pack", {}),
    (tk.Label, {"text": "test"}, {"side": "top", "fill": "x"}, "pack", {}),
    (
        tk.Button,
        {"text": "test", "command": MagicMock()},
        {"side": "top", "fill": "x"},
        "pack",
        {},
    ),
    # Place
    (tk.Frame, {}, {"width": 10, "height": 10}, "place", {}),
    (tk.Entry, {}, {"width": 10, "height": 10}, "place", {}),
    (tk.Listbox, {}, {"width": 10, "height": 10}, "place", {}),
    (tk.Label, {"text": "test"}, {"width": 10, "height": 10}, "place", {}),
    (
        tk.Button,
        {"text": "test", "command": MagicMock()},
        {"width": 10, "height": 10},
        "place",
        {},
    ),
]
widgets_wid = [
    # cls, style, placement_dict, placement_type, extra_options
    (tk.Frame, {}, {"row": 0, "column": None}, "grid", {}),
    (tk.Entry, {}, {"row": 1, "column": None}, "grid", {}),
    (tk.Listbox, {}, {"row": 2, "column": None}, "grid", {}),
    (tk.Label, {"text": "test"}, {"row": 3, "column": None}, "grid", {}),
    (
        tk.Button,
        {"text": "test", "command": MagicMock()},
        {"row": 4, "column": None},
        "grid",
        {},
    ),
    (ttk.Combobox, {}, {"row": 5, "column": None}, "grid", {}),
    # Pack
    (tk.Frame, {}, {"side": "top", "fill": None}, "pack", {}),
    (tk.Entry, {}, {"side": "top", "fill": None}, "pack", {}),
    (tk.Listbox, {}, {"side": "top", "fill": None}, "pack", {}),
    (tk.Label, {"text": "test"}, {"side": "top", "fill": None}, "pack", {}),
    (
        tk.Button,
        {"text": "test", "command": MagicMock()},
        {"side": "top", "fill": None},
        "pack",
        {},
    ),
    # Place
    (tk.Frame, {}, {"width": 10, "height": None}, "place", {}),
    (tk.Entry, {}, {"width": 10, "height": None}, "place", {}),
    (tk.Listbox, {}, {"width": 10, "height": None}, "place", {}),
    (tk.Label, {"text": "test"}, {"width": 10, "height": None}, "place", {}),
    (
        tk.Button,
        {"text": "test", "command": MagicMock()},
        {"width": 10, "height": None},
        "place",
        {},
    ),
]

invalid_widgets = [
    None,
    tk.Frame(),
    type("NotAWidget", (), {})(),
    "string",
    123,
    tk.Tk(),
    tk.Toplevel(),
]
frames = [
    tk.Frame,
    tk.Entry,
    tk.Label,
    tk.Listbox,
    tk.Button,
    ttk.Combobox,
]


@pytest.mark.parametrize(
    "cls, style, placement, placement_type, extra_options", widgets_all
)
def test_factory_combined(
    instance, fake_root, cls, style, placement, placement_type, extra_options
):
    kwargs = {placement_type: placement} if placement else {}

    if cls in [tk.Tk, tk.Toplevel]:
        with patch("gui_factory.set_window_icon", return_value=None):
            app = instance(WidgetFactory, bg_color="#f0f8ff")
            widget = app.create_widgets(
                cls=cls, frame=fake_root, style=style, **kwargs, **extra_options
            )
    else:
        app = instance(WidgetFactory, bg_color="#f0f8ff")
        widget = app.create_widgets(
            cls=cls, frame=fake_root, style=style, **kwargs, **extra_options
        )

    assert isinstance(
        widget, cls
    ), f"Ожидался объект класса {cls}, получили {type(widget)}"

    for key, expected_value in style.items():
        if key in widget.keys():
            if callable(expected_value):
                continue
            actual_value = widget.cget(key)
            assert str(actual_value) == str(
                expected_value
            ), f"Неверное значение свойства '{key}' — ожидалось '{expected_value}', получили '{actual_value}'"

    if cls not in [tk.Tk, tk.Toplevel]:
        if extra_options.get("is_scrollable", False):
            from tkinter import Canvas

            assert isinstance(
                widget.master, Canvas
            ), "Scrollable frame должен иметь Canvas в качестве master"
        else:
            assert (
                widget.master == fake_root
            ), "Обычные виджеты должны иметь root в качестве master"

    if cls in [tk.Tk, tk.Toplevel]:
        widget.destroy()
        return

    check_widget_placement(widget, placement_type, placement)

    if cls is tk.Button and "command" in style:
        mock_command = style["command"]
        mock_command.assert_not_called()
        widget.invoke()
        mock_command.assert_called_once()


@pytest.mark.parametrize(
    "cls, style, placement, placement_type, extra_options", widgets_wid
)
def test_factory_invalid_placement(
    instance, fake_root, cls, style, placement, placement_type, extra_options
):
    """
    Проверяем что create_widgets бросает ValueError на неправильные входные данные
    """
    kwargs = {placement_type: placement} if placement else {}
    app = instance(WidgetFactory, bg_color="#f0f8ff")
    with pytest.raises(ValueError, match="Ошибка размещения виджета:"):
        app.create_widgets(
            cls=cls, frame=fake_root, style=style, **kwargs, **extra_options
        )


@pytest.mark.parametrize("invalid_cls", invalid_widgets)
def test_factory_invalid_widget(instance, invalid_cls):
    """
    Проверяем что create_widgets бросает ValueError на неправильные входные данные
    """
    app = instance(WidgetFactory, bg_color="#f0f8ff")
    with pytest.raises(ValueError) as e:
        app.create_widgets(invalid_cls)

    err_msg = str(e.value)
    assert "Ошибка: cls должен быть классом." in err_msg


@pytest.mark.parametrize("cls", frames)
def test_create_widgets_without_frame(instance, cls):
    """
    Проверяем, что создание виджета (кроме Tk/Toplevel) без frame кидает ошибку
    """
    app = instance(WidgetFactory, bg_color="#f0f8ff")
    expected_message = f"Ошибка: Для создания виджета {cls.__name__} необходимо указать frame (родительский контейнер)."

    with pytest.raises(ValueError, match=re.escape(expected_message)):
        app.create_widgets(cls=cls, frame=None)
