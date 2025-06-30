import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock

import pytest

from gui_factory import WidgetBuilder

widgets_test_container = [
    (
        "create_button",
        {"text": "test"},
        {"command": MagicMock()},
        {"row": 0, "column": 0},
    ),
    ("create_label", {"text": "test"}, {}, {"row": 0, "column": 0}),
    ("create_entry", {}, {}, {"row": 0, "column": 0}),
    ("create_listbox", {}, {}, {"row": 0, "column": 0}),
    ("create_frame", {}, {}, {"row": 0, "column": 0}),
    ("create_scrollable_frame", {}, {}, {}),
    ("create_combobox", {}, {}, {"row": 0, "column": 0}),
]


@pytest.mark.parametrize("method_name, text, command, grid", widgets_test_container)
def test_widget_builder(instance, fake_root, method_name, text, command, grid):
    app = instance(WidgetBuilder, bg_color="#f0f8ff")
    if method_name == "create_entry" or method_name == "create_combobox":
        var = tk.StringVar(fake_root, value="test")
        text = {"textvariable": var}

    method = getattr(app, method_name)
    widget = method(window=fake_root, **text, **command, grid={**grid})
    assert isinstance(widget, tk.Widget) or isinstance(widget, ttk.Combobox)

    if "text" in text:
        if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
            assert text["textvariable"].get() == var.get()
        else:
            assert widget.cget("text") == text.get("text")

    grid_info = widget.grid_info()
    for key, value in grid.items():
        assert str(grid_info.get(key)) == str(value)

    if isinstance(widget, tk.Button):
        widget.invoke()
        command.get("command").assert_called_once()
