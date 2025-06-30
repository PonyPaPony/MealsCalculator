import tkinter as tk
from unittest.mock import MagicMock, patch

import pytest

from autocomplete import Autocomplete

testing_case = [
    (None, None, None, "Ошибка: Получения Данных"),
    ("val", None, tk.Listbox(), "Ошибка: Получения Данных"),
    (None, {"А": 1}, tk.Listbox(), "Ошибка: Получения Данных"),
    ("val", {"А": 1}, None, "Ошибка: Получения Данных"),
    (
        "mock_entry",
        {"А": 1},
        tk.Listbox(),
        "Ошибка: entry_widget и listbox_widget должны быть классом tkinter",
    ),
    (
        tk.Entry(),
        {"А": 1},
        "mock_listbox",
        "Ошибка: entry_widget и listbox_widget должны быть классом tkinter",
    ),
    (
        tk.Entry(),
        {"А": 1},
        tk.Listbox,
        "Ошибка: entry_widget и listbox_widget должны быть классом tkinter",
    ),
]
testing_case_2 = [
    ("Ба", "Банан"),
    ("Ар", "Арбуз"),
    ("Ап", "Апельсин"),
    ("ба", "Банан"),
    ("ар", "Арбуз"),
    ("ап", "Апельсин"),
    ("бА", "Банан"),
    ("аР", "Арбуз"),
    ("аП", "Апельсин"),
    ("БА", "Банан"),
    ("АР", "Арбуз"),
    ("АП", "Апельсин"),
]


@pytest.fixture
def autocomplete_helper(fake_root):
    entry = tk.Entry(fake_root)
    listbox = tk.Listbox(fake_root)
    products = {"Апельсин": 1, "Арбуз": 2, "Банан": 3}
    return {
        "entry": entry,
        "listbox": listbox,
        "products": products,
    }


@pytest.mark.parametrize("product", ["Арбуз", "Банан"])
def test_autocomplete_valid(instance, fake_root, autocomplete_helper, product):
    app = instance(Autocomplete)

    update_suggestions = app.setup_autocomplete(
        autocomplete_helper["entry"],
        list(autocomplete_helper["products"].keys()),
        autocomplete_helper["listbox"],
    )

    autocomplete_helper["entry"].delete(0, tk.END)
    autocomplete_helper["entry"].insert(0, product[:2])  # Вставляем часть строки

    update_suggestions()

    fake_root.update_idletasks()
    fake_root.update()

    values = autocomplete_helper["listbox"].get(0, tk.END)
    assert product in values


@pytest.mark.parametrize("key, target", [("А", "Апельсин")])
def test_setup_autocomplete_handlers(
    instance, fake_root, autocomplete_helper, key, target
):
    app = instance(Autocomplete)

    entry = autocomplete_helper["entry"]
    listbox = autocomplete_helper["listbox"]
    suggestions = list(autocomplete_helper["products"].keys())

    with patch.object(entry, "bind", wraps=entry.bind) as mock_entry_bind, patch.object(
        listbox, "bind", wraps=listbox.bind
    ) as mock_listbox_bind, patch.object(entry, "delete") as mock_delete, patch.object(
        entry, "insert"
    ) as mock_insert:

        app.setup_autocomplete(entry, suggestions, listbox)

        entry.insert(0, key)
        update_cb = mock_entry_bind.call_args_list[0][0][1]
        fill_cb = mock_listbox_bind.call_args_list[0][0][1]
        select_cb = mock_listbox_bind.call_args_list[1][0][1]

        update_cb()
        listbox.insert(tk.END, target)  # вручную имитируем появление элемента в listbox

        fill_cb(event=MagicMock(y=0))
        select_cb(event=None)

        mock_delete.assert_called()
        mock_insert.assert_called_with(0, target)


@pytest.mark.parametrize("entry, suggestions, listbox, msg", testing_case)
def test_autocomplete_invalid(instance, entry, suggestions, listbox, msg):
    app = instance(Autocomplete)
    with pytest.raises(ValueError, match=msg):
        app.setup_autocomplete(entry, suggestions, listbox)


@pytest.mark.parametrize("key, target", testing_case_2)
def test_on_select_behavior(instance, fake_root, autocomplete_helper, key, target):
    app = instance(Autocomplete)

    entry = autocomplete_helper["entry"]
    listbox = autocomplete_helper["listbox"]
    suggestions = list(autocomplete_helper["products"].keys())

    with patch.object(entry, "delete") as mock_delete, patch.object(
        entry, "insert"
    ) as mock_insert, patch.object(
        listbox, "delete"
    ) as mock_listbox_delete, patch.object(
        listbox, "bind", wraps=listbox.bind
    ) as mock_listbox_bind, patch.object(
        listbox, "curselection", return_value=(0,)
    ), patch.object(
        listbox, "get", return_value=target
    ):

        app.setup_autocomplete(entry, suggestions, listbox)
        on_select_cb = mock_listbox_bind.call_args_list[1][0][1]
        on_select_cb(event=None)

        mock_delete.assert_called_once_with(0, tk.END)
        mock_insert.assert_called_once_with(0, target.title())
        mock_listbox_delete.assert_called_once_with(0, tk.END)
