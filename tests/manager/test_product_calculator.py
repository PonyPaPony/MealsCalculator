import tkinter as tk
from unittest.mock import ANY, MagicMock

import pytest

from product_manager import ProductCalculator, ProductContext


@pytest.fixture
def context(instance):
    context = instance(ProductContext, language="ru")
    return context


class MockVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class Assistant:
    def __init__(self, instance, items=None, root=None, button=None, entry=None):
        self.instance = instance
        self.items = items
        self.root = root
        # self.button = button
        # self.entry = entry

        self._setup_mocks(root)

    def _setup_mocks(self, root):
        if not root:
            self.instance.products = {"Яблоки": 52.0, "Бананы": 89.0, "Грибы": 100.0}
            self.data = [(MockVar(key), MockVar(value)) for key, value in self.items]
            self.instance.factory.save_results = MagicMock()
            self.instance.info_message = MagicMock()
        else:
            self.button = MagicMock()
            self.entry = MagicMock()
            self.frame = tk.Frame(root)
            self.instance.products = {"Test": 100}
            self.data = []

            self.instance.builder.create_button = MagicMock(return_value=self.button)
            self.instance.builder.create_entry = MagicMock(return_value=self.entry)


test_case = [
    [("Бананы", "abc"), "Вес должен быть числом."],
    [("Яблоки", "-1"), "Вес должен быть положительным."],
    [("Кефир", "100"), "Продукт 'Кефир' не найден в базе."],
    [("Яблоки", ""), "Вес должен быть числом."],
]
test_case_2 = [
    [("Бананы", "200"), ("Яблоки", "100")],
    [("Грибы", "200"), ("Яблоки", "100")],
    [("Бананы", "200"), ("Грибы", "100")],
    [("Бананы", "200"), ("Яблоки", "100"), ("Грибы", "300")],
]
test_case_3 = [
    ({"test": 10.0}, None, None, "Ошибка: Отсутствуют данные или валидное окно."),
    ({"test": 10.0}, [], None, "Ошибка: Окно должно быть экземпляром tk.Frame"),
    (
        {"test": 10.0},
        None,
        "frame_placeholder",
        "Ошибка: Отсутствуют данные или валидное окно.",
    ),
    ({}, [], "frame_placeholder", "Ошибка: Список продуктов пуст или поврежден."),
]


@pytest.mark.parametrize(
    "items",
    [
        [("Яблоки", "100")],
    ],
)
def test_total_calculator_valid(instance, context, items):
    manager = instance(ProductCalculator, context)
    mock_env = Assistant(manager, items)
    manager.calculate_total(mock_env.data)
    manager.info_message.assert_called()
    manager.factory.save_results.assert_called()


@pytest.mark.parametrize("items, msg", test_case)
def test_total_calculator_invalid(instance, context, items, msg):
    manager = instance(ProductCalculator, context)
    mock_env = Assistant(manager, [items])
    with pytest.raises(ValueError, match=msg):
        manager.calculate_total(mock_env.data)
    manager.info_message.assert_not_called()
    manager.factory.save_results.assert_not_called()


@pytest.mark.parametrize("items", test_case_2)
def test_total_calculator_multiple_calid(instance, context, items):
    manager = instance(ProductCalculator, context)
    mock_env = Assistant(manager, items)
    manager.calculate_total(mock_env.data)
    manager.info_message.assert_called_once()
    manager.factory.save_results.assert_called_once()


def test_create_and_remove_input_row(instance, context, fake_root):
    manager = instance(ProductCalculator, context)
    mock_env = Assistant(manager, root=fake_root)
    remove_command_holder = {}

    def mock_create_button(*args, **kwargs):
        if kwargs.get("text") == "Удалить":
            remove_command_holder["command"] = kwargs["command"]
        return mock_env.button

    manager.builder.create_button = MagicMock(side_effect=mock_create_button)
    manager.builder.create_entry = MagicMock(return_value=mock_env.entry)

    p_var, w_var = manager.create_input_product_row([], frame=mock_env.frame)

    manager.builder.create_button.assert_any_call(
        mock_env.frame,
        text="Удалить",
        command=remove_command_holder["command"],
        style=ANY,
        grid=ANY,
    )

    manager.builder.create_entry.assert_called_once()
    manager.builder.create_button.assert_called_once()

    p_var, w_var = manager.create_input_product_row(mock_env.data, frame=mock_env.frame)

    assert manager.builder.create_entry.call_count == 2
    assert manager.builder.create_button.call_count == 2

    mock_env.data.append((p_var, w_var))
    assert (p_var, w_var) in mock_env.data

    remove_command_holder["command"]()


@pytest.mark.parametrize("items, data, frame, msg", test_case_3)
def test_create_invalid_row(instance, context, fake_root, items, data, frame, msg):
    manager = instance(ProductCalculator, context)
    manager.products = items

    if frame == "frame_placeholder":
        frame = tk.Frame(fake_root)

    with pytest.raises(ValueError, match=msg):
        manager.create_input_product_row(data, frame=frame)
