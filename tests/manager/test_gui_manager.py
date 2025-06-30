from unittest.mock import MagicMock, call

import pytest

from product_manager import ProductContext, ProductManagerGUI
from tests.conftest import fake_root


class ButtonCall:
    def __init__(self, app, mock=False, key=None, value=None, name=None, kcal=None):
        self.app = app
        self.key = key
        self.value = value
        self.name = name
        self.kcal = kcal

        self.window = MagicMock()
        self.frame = MagicMock()
        self.entry_name = MagicMock()
        self.entry_kcal = MagicMock()
        self.button = MagicMock()
        self.listbox = MagicMock()

        self.entry_name.get.return_value = name
        self.entry_kcal.get.return_value = kcal

        if mock:
            self._mocks()

    def click(self, command=0):
        try:
            button_call = self.app.builder.create_button.call_args_list[command]
        except IndexError:
            raise IndexError(
                f"Нет кнопки с индексом {command} в create_button.call_args_list"
            )
        button_func = button_call[1]["command"]
        button_func()

    def _mocks(self):
        self.app.factory.create_widgets.return_value = self.window
        self.app.builder.create_frame.return_value = self.frame
        self.app.builder.create_entry.side_effect = [self.entry_name, self.entry_kcal]
        self.app.builder.create_button.return_value = self.button
        self.app.builder.create_listbox.return_value = self.listbox
        self.app.factory.restore_root_window = MagicMock()
        self.app.validate_product_input = MagicMock(return_value=(self.key, self.value))
        self.app.update_product_data = MagicMock()
        self.app._save_products = MagicMock()
        self.app.setup.setup_autocomplete = MagicMock()
        self.app.error_message = MagicMock()
        self.app.info_message = MagicMock()


test_case = [
    ("Append", "open_add_products_window"),
    ("Delete", "open_del_products_window"),
    ("Change", "open_change_products_window"),
]
test_case_2 = [
    (None, "Append", "Отсутствует экземпляр Tkinter", None),
    (fake_root, None, "Не указан тэг действия", None),
    (
        fake_root,
        "abc",
        "Неизвестный таг действия: abc",
        "Ошибка: Неизвестный таг действия — abc",
    ),
]
test_case_3 = [
    ("Огурец", "15", True, 15.0, "Успех", "Добавлен Огурец с калорийностью 15.0."),
    ("Сало", "19", None, None, "Внимание", "Такой продукт уже существует."),
    ("Кабачок", "abc", False, None, "Внимание", "Неверный формат калорийности."),
    ("", "10", False, None, "Ошибка", "Поле продукта не может быть пустым."),
]
test_case_4 = [
    ("Яблоко", "Успех", "Продукт Яблоко удалён."),
    ("Сало", "Ошибка", "Продукт Сало не найден."),
    ("", "Ошибка", "Введите название продукта."),
]
test_case_5 = [
    ("Огурец", "15", True, 15.0, "Успех", "Калорийность Огурец обновлена."),
    ("", "15", False, 15.0, "Ошибка", "Введите название продукта."),
    ("Сало", "15", False, 15.0, "Ошибка", "Продукт Сало не найден."),
    ("Огурец", "", False, None, "Ошибка", "Введите калории для продукта."),
]


@pytest.fixture
def context(instance):
    context = instance(ProductContext, language="ru")
    return context


@pytest.mark.parametrize("tag, method", test_case)
def test_window_root(instance, context, fake_root, tag, method):
    app = instance(ProductManagerGUI, context)
    setattr(app, method, MagicMock())
    other_methods = {
        "open_add_products_window",
        "open_del_products_window",
        "open_change_products_window",
    } - {method}
    for m in other_methods:
        setattr(app, m, MagicMock())

    app.root_for_window(fake_root, tag)

    getattr(app, method).assert_called_once_with(fake_root)
    for m in other_methods:
        getattr(app, m).assert_not_called()


@pytest.mark.parametrize("window, tag, msg, log", test_case_2)
def test_invalid_window_root(instance, context, window, tag, msg, log):
    app = instance(ProductManagerGUI, context)
    app.log = MagicMock()
    with pytest.raises(ValueError, match=msg):
        app.root_for_window(window, tag)

    if log is not None:
        app.log.assert_called_once_with(log)
    else:
        app.log.assert_not_called()


@pytest.mark.parametrize("name, kcal, key, value, title, msg", test_case_3)
def test_open_add_products_window(
    instance, context, fake_root, name, kcal, key, value, title, msg
):
    app = instance(ProductManagerGUI, context)
    btn = ButtonCall(app, True, key, value, name, kcal)
    if name == "Сало":
        app.products = {name: float(kcal)}

    app.open_add_products_window(fake_root)

    btn.click()

    if key:
        app.validate_product_input.assert_called_once_with(name, kcal)
        app.update_product_data.assert_called_once_with(name, float(kcal))
        app.info_message.assert_called_once_with(title, msg)
    elif name in app.products:
        app.info_message.assert_called_once_with(title, msg)
    else:
        app.error_message.assert_called_once_with(title, msg)

    btn.click(1)
    app.factory.restore_root_window.assert_called()


@pytest.mark.parametrize("name, title, msg", test_case_4)
def test_open_del_products_window(instance, context, fake_root, name, title, msg):
    app = instance(ProductManagerGUI, context)
    btn = ButtonCall(app, True, name=name)
    if name == "Яблоко":
        app.products = {name: 15.0}

    app.open_del_products_window(fake_root)
    btn.click()

    if name == "Яблоко":
        app._save_products.assert_called()
        app.info_message.assert_called_once_with(title, msg)
    else:
        app._save_products.assert_not_called()
        app.error_message.assert_called_once_with(title, msg)

    btn.click(1)
    app.factory.restore_root_window.assert_called()


@pytest.mark.parametrize("name, kcal, key, value, title, msg", test_case_5)
def test_open_change_products_window(
    instance, context, fake_root, name, kcal, key, value, title, msg
):
    app = instance(ProductManagerGUI, context)
    btn = ButtonCall(app, True, key, value, name, kcal)
    if name == "Огурец" and kcal != "":
        app.products = {name: float(kcal)}
    elif name == "Сало":
        app.products = {"Огурец": 15.0}
    else:
        app.products = {"Огурец": 15.0}

    app.open_change_products_window(fake_root)
    btn.click()

    if key and value:
        app.validate_product_input.assert_called_once_with(name, kcal)
        app.update_product_data.assert_called_once_with(name, float(kcal))
        app.info_message.assert_called_once_with(title, msg)
    else:
        error_calls = app.error_message.call_args_list
        assert any(
            call_ == call(title, msg) for call_ in error_calls
        ), f"Ожидался вызов error_message({title}, {msg}), но среди вызовов: {error_calls}"

    btn.click(1)
    app.factory.restore_root_window.assert_called()
