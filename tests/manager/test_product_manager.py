import logging
from unittest.mock import MagicMock, patch

import pytest

from product_manager import ProductContext, ProductManager

logger = logging.getLogger(__name__)


class Assistant:
    def __init__(self, instance, language, mock_save=False, mock_path=True):
        self.instance = instance
        self.instance.products = {"Яблоки": 52.0}
        self.language = language

        self._set_mock(mock_save)
        self._set_path(mock_path)

    def _set_mock(self, mock_save):
        self.instance.factory.read_and_write_file = MagicMock()
        self.instance.settings.ensure_file_with_defaults = MagicMock()
        self.instance.info_message = MagicMock()
        self.instance.error_message = MagicMock()
        if mock_save:
            self.instance._save_products = MagicMock()

    def _set_path(self, mock_path):
        if mock_path:
            file_paths = {
                "ru": self.instance.settings.PRODUCTS_LIST_RU,
                "en": self.instance.settings.PRODUCTS_LIST_EN,
            }

            self.file_path = file_paths.get(self.language)


test_case = [
    ("ru", "Успех", "Продукты сохранены!"),
    (
        "en",
        "Успех",
        "Продукты сохранены!",
    ),  # TODO: Требуется повторный тест после подключения перевода.
]
test_case_2 = [
    ("", "Ошибка: Не указан параметр языка.", "ru"),
    ("tr", "Ошибка: Указанный перевод не доступен.", "ru"),
    # TODO: Требуется дополнительный тест после подключения перевода.
]
test_case_3 = [
    ("", "Ошибка: Не указан параметр языка.", "ru"),
    (None, "Ошибка: Не указан параметр языка.", "ru"),
    ("tr", "Ошибка: Указанный перевод не доступен.", "ru"),
    (1, "Ошибка: Указанный перевод не доступен.", "ru"),
    # TODO: Требуется дополнительный тест после подключения перевода.
]
test_case_4 = [
    ("Яблоко", 52.0, None, None),
    ("Яблоко", 52, None, None),
    ("  яБлОкО ", 33.3, None, None),
    ("", "", "Ошибка", "Название и калорийность обязательны."),
    (None, 111.11, "Ошибка", "Название и калорийность обязательны."),
    ("Груша", "abc", "Ошибка", "Калорийность abc не является числом."),
    ("Слива", None, "Ошибка", "Название и калорийность обязательны."),
    (None, None, "Ошибка", "Название и калорийность обязательны."),
    ("ПесПатрон", "%!#$%", "Ошибка", "Калорийность %!#$% не является числом."),
]
test_case_5 = [
    ("Яблоко", 53.19),
    ("Яблоко", 3.14),
    ("Яблоко", 14.88),
    ("Яблоко", 3.22),
    ("Яблоко", 0.19),
    ("Яблоко", 1),
    ("  яБлОкО ", 33.3),
]
test_case_6 = [
    ("", None, {"Яблоки": 52.0}, "Ошибка: Неверно указаны данные name или kcal"),
    (None, 3.14, {"Яблоки": 52.0}, "Ошибка: Неверно указаны данные name или kcal"),
    (
        3.14,
        14.88,
        {"Яблоки": 52.0},
        "Ошибка: Наименование продукта не может быть числом.",
    ),
    ("Яблоко", "abc", {"Яблоки": 52.0}, "Ошибка: Калорийность должна быть числом."),
    (
        "Яблоко",
        0,
        {"Яблоки": 52.0},
        "Ошибка: Калорийность должна быть положительным числом.",
    ),
    (
        "Яблоко",
        -9999,
        {"Яблоки": 52.0},
        "Ошибка: Калорийность должна быть положительным числом.",
    ),
]
test_case_7 = [
    ("ru", {"Бананы": 100}),
    ("en", {"Bananas": 100}),
]


@pytest.fixture
def context(instance):
    context = instance(ProductContext)
    return context


@pytest.mark.parametrize("language, title, msg", test_case)
@patch("product_manager.SUPPORTED_LANGUAGES", {"ru", "en"})
def test_save_products(instance, context, language, title, msg):
    context.language = language
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, language)

    manager._save_products(language)
    manager.factory.read_and_write_file.assert_called_with(
        mock_env.file_path, "w", manager.products
    )
    manager.info_message.assert_called_with(title, msg)


@pytest.mark.parametrize("language, msg, init_language", test_case_2)
@patch("product_manager.SUPPORTED_LANGUAGES", {"ru", "en"})
def test_save_products_errors(instance, context, language, msg, init_language):
    context.language = init_language
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, init_language)
    with pytest.raises(ValueError, match=msg):
        manager._save_products(language)

    manager.factory.read_and_write_file.assert_not_called()
    manager.info_message.assert_not_called()


@pytest.mark.parametrize("language, items", test_case_7)
@patch("product_manager.SUPPORTED_LANGUAGES", {"ru", "en"})
@patch("os.path.exists", return_value=True)
def test_load_products_internal(mock_exists, instance, context, language, items):
    context.language = language
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, language, mock_path=True)

    manager.factory.read_and_write_file.return_value = items
    result = manager._load_products_internal(language)
    manager.factory.read_and_write_file.assert_called_with(mock_env.file_path, "r")

    assert result == items


@pytest.mark.parametrize("language, items", test_case_7)
@patch("product_manager.SUPPORTED_LANGUAGES", {"ru", "en"})
@patch("os.path.exists", return_value=False)
def test_load_products_internal_file_missing(
    mock_exists, instance, context, language, items
):
    context.language = language
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, language, mock_path=True)

    manager.settings.ensure_file_with_defaults.return_value = items
    result = manager._load_products_internal(language)
    manager.settings.ensure_file_with_defaults.assert_called_with(language)

    assert result == items


@pytest.mark.parametrize("language, msg, init_language", test_case_3)
def test_load_products_internal_with_error(
    instance, context, language, msg, init_language
):
    context.language = init_language
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, init_language)
    with pytest.raises(ValueError, match=msg):
        manager._load_products_internal(language)

    manager.settings.ensure_file_with_defaults.assert_not_called()
    manager.factory.read_and_write_file.assert_not_called()


@pytest.mark.parametrize("name, kcal, title, msg", test_case_4)
def test_validate_product_input(instance, context, name, kcal, title, msg):
    context.language = "ru"
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, "ru")
    if not name or not isinstance(kcal, int | float):
        manager.validate_product_input(name, kcal)
        manager.error_message.assert_called_with(title, msg)
    else:
        result = manager.validate_product_input(name, kcal)
        assert result == (True, kcal)
        assert isinstance(result[0], bool)
        assert isinstance(result[1], int | float)
        manager.error_message.assert_not_called()


@pytest.mark.parametrize("name, kcal", test_case_5)
def test_update_product_data(instance, context, name, kcal):
    context.language = "ru"
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, "ru", mock_save=True)

    manager.update_product_data(name, kcal)
    assert manager.products[name.title()] == kcal
    manager._save_products.assert_called()


@pytest.mark.parametrize("name, kcal, items, msg", test_case_6)
def test_update_product_data_errors(instance, context, name, kcal, items, msg):
    context.language = "ru"
    manager = instance(ProductManager, context)
    mock_env = Assistant(manager, "ru", mock_save=True)

    with pytest.raises(ValueError, match=msg):
        manager.update_product_data(name, kcal)

    assert manager.products == items
    manager._save_products.assert_not_called()
