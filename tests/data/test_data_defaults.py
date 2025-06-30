import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from data_defaults import DataDefaults


@pytest.fixture
def temp_file_path():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def init_path(instance, language, temp_file_path):
    app = instance(DataDefaults)
    if language == "ru":
        app.PRODUCTS_LIST_RU = temp_file_path
    else:
        app.PRODUCTS_LIST_EN = temp_file_path


test_case = [
    ("ru", "Яблоки"),
    ("en", "Apples"),
]


@patch(
    "data_defaults.read_config",
    return_value=(
        ["ru", "en"],
        ["data/products/products_ru.json", "data/products/products_en.json"],
    ),
)
def test_init_reads_paths_from_config(mock_read, instance):
    # Не передаём path_ru и path_en — они должны подтянуться из read_config
    data_defaults = DataDefaults(language="ru", path_ru=None, path_en=None)

    assert data_defaults.PRODUCTS_LIST_RU == "data/products/products_ru.json"
    assert data_defaults.PRODUCTS_LIST_EN == "data/products/products_en.json"

    # Проверим, что read_config вызывался ровно один раз
    mock_read.assert_called_once()


@pytest.mark.parametrize("language, expected_key", test_case)
def test_get_default_products_valid_languages(
    language, expected_key, temp_file_path, instance
):
    init_path(instance, language, temp_file_path)
    app = instance(DataDefaults)

    # Подготовка временного файла с JSON-данными
    with open(temp_file_path, "w", encoding="utf-8") as f:
        json.dump({expected_key: 42}, f)

    data = app.get_default_products(language)
    assert isinstance(data, dict)
    assert expected_key in data
    assert isinstance(data[expected_key], int)


def test_get_default_products_invalid_language(instance):
    app = instance(DataDefaults)
    result = app.get_default_products("fr")
    assert result is None
    app.error_message.assert_called_once_with("Ошибка", "Не существующий язык.")


@pytest.mark.parametrize("language, expected_key", test_case)
def test_ensure_file_with_defaults_creates_new_file(
    language, expected_key, temp_file_path, instance
):
    # Создание объекта с подставленным путём
    app = instance(DataDefaults)
    if language == "ru":
        app.PRODUCTS_LIST_RU = temp_file_path
    else:
        app.PRODUCTS_LIST_EN = temp_file_path

    result = app.ensure_file_with_defaults(language)
    assert isinstance(result, dict)
    assert expected_key in result

    with open(temp_file_path, encoding="utf-8") as f:
        data = json.load(f)
        assert expected_key in data


def test_ensure_file_with_defaults_reads_existing_file(temp_file_path, instance):
    # Подготовка содержимого
    sample_data = {"Test": 123}
    with open(temp_file_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    app = instance(DataDefaults, language="ru")
    app.PRODUCTS_LIST_RU = temp_file_path
    result = app.ensure_file_with_defaults("ru")

    assert result == sample_data


def test_ensure_file_with_defaults_overwrites_empty_file(temp_file_path, instance):
    # Пустой файл
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write("")

    app = instance(DataDefaults, language="en")
    app.PRODUCTS_LIST_EN = temp_file_path
    result = app.ensure_file_with_defaults("en")

    assert "Apples" in result


def test_ensure_file_with_defaults_handles_invalid_json(temp_file_path, instance):
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")

    app = instance(DataDefaults, language="ru")
    app.PRODUCTS_LIST_RU = temp_file_path
    result = app.ensure_file_with_defaults("ru")

    assert "Яблоки" in result


def test_ensure_file_with_defaults_raises_on_invalid_language(instance):
    app = instance(DataDefaults, language="invalid")
    with pytest.raises(ValueError):
        app.ensure_file_with_defaults("invalid")


def test_ensure_invalid_lang(temp_file_path, instance):
    app = instance(DataDefaults)
    with pytest.raises(ValueError, match="Не существующий язык."):
        app.ensure_file_with_defaults("invalid")


def test_get_default_products_invalid_languages(instance):
    app = instance(DataDefaults)
    app.error_message = MagicMock()
    app.language = "tr"
    app.get_default_products(app.language)
    app.error_message.assert_called_once_with("Ошибка", "Не существующий язык.")


@patch("os.path.exists", return_value=False)
@patch("builtins.open", side_effect=OSError("Disk full"))
def test_write_default_ioerror_handling(mock_open, mocks, instance):
    data_defaults = instance(DataDefaults, language="ru")
    data_defaults.log = MagicMock()
    data_defaults.info_message = MagicMock()
    data_defaults.error_message = MagicMock()

    result = data_defaults.ensure_file_with_defaults("ru")

    # Проверяем, что лог и ошибка вызваны
    assert data_defaults.log.call_count > 0
    assert data_defaults.error_message.call_count > 0

    # Успешное сообщение не должно быть вызвано
    assert data_defaults.info_message.call_count == 0


@patch("builtins.open", create=True)
def test_write_default_ioerror(mock_open, instance, temp_file_path):
    def open_side_effect(file, mode="r", *args, **kwargs):
        if "r" in mode:
            raise OSError("Read permission denied")
        elif "w" in mode:
            raise OSError("Write permission denied")
        else:
            raise ValueError("Unexpected mode")

    mock_open.side_effect = open_side_effect

    data = instance(DataDefaults)
    data.PRODUCTS_LIST_RU = temp_file_path
    data.language = "ru"

    data.error_message = MagicMock()
    data.info_message = MagicMock()
    data.log = MagicMock()

    result = data.ensure_file_with_defaults("ru")

    # Проверка сообщений об ошибках
    error_msgs = [call.args[1] for call in data.error_message.call_args_list]
    assert any(
        "Не удалось записать" in msg for msg in error_msgs
    ), "Ожидалось сообщение о невозможности записи файла"
    assert any(
        "Ошибка чтения" in msg for msg in error_msgs
    ), "Ожидалось сообщение об ошибке чтения файла"

    # Проверка логов
    log_msgs = [call.args[0] for call in data.log.call_args_list]
    assert any(
        "Ошибка записи файла" in msg for msg in log_msgs
    ), "Ожидалось лог-сообщение о создании файла"
    assert any(
        "Ошибка чтения файла" in msg for msg in log_msgs
    ), "Ожидалось лог-сообщение о чтении файла"

    assert isinstance(result, dict)
