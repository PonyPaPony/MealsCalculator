import tkinter as tk
from unittest.mock import ANY, MagicMock, patch

import pytest

from gui_factory import Factory
from tests.conftest import fake_root

test_container = [
    (None, tk.Frame(), "Ошибка, Нет рабочего окна."),
    (None, None, "Ошибка, 'root' и 'window' не указаны."),
]
test_container_2 = [
    (None, None, "Ошибка, Нет рабочего окна и не указано действие."),
    (None, "show", "Ошибка, Не валидный тип окна."),
    (
        fake_root,
        "invalid",
        "Ошибка, Некорректное значение. Используйте 'hide' или 'show'.",
    ),
]
test_container_3 = [
    (None, tk.Frame(), "Ошибка, Не валидный тип окна."),
    (None, None, "Ошибка, Нет рабочего окна."),
]
test_container_4 = [
    ({"key": None}, "w", "Значение для ключа 'key' не может быть None"),
    ({None: "value"}, "w", "Ошибка, Ключ отсутствует или поврежден"),
    ({None: None}, "w", "Ошибка, Нет ключа и данных."),
    ({"key": "value"}, "t", "Неподдерживаемый метод: t"),
]


def test_on_close_root(instance):
    app = instance(Factory)
    root = tk.Tk()
    root.quit = MagicMock()
    root.destroy = MagicMock()
    app.on_close(root)
    root.quit.assert_called_once()
    root.destroy.assert_called_once()


def test_on_close_window(instance, fake_root):
    app = instance(Factory)
    frame = tk.Frame(fake_root)
    frame.destroy = MagicMock()
    fake_root.quit = MagicMock()
    fake_root.destroy = MagicMock()
    app.on_close(fake_root, frame)
    frame.destroy.assert_called_once()
    fake_root.quit.assert_called_once()
    fake_root.destroy.assert_called_once()


@pytest.mark.parametrize("window, method, msg", test_container)
def test_on_close_invalid(instance, window, method, msg):
    app = instance(Factory)
    with pytest.raises(ValueError, match=msg):
        app.on_close(window, method)


def test_window_status(instance, fake_root):
    app = instance(Factory)
    app.window_status(fake_root, "hide")
    fake_root.update()
    assert not fake_root.winfo_viewable()

    app.window_status(fake_root, "show")
    fake_root.update()
    assert fake_root.winfo_viewable()


@pytest.mark.parametrize("window, method, msg", test_container_2)
def test_window_status_invalid(instance, window, method, msg):
    app = instance(Factory)
    with pytest.raises(ValueError, match=msg):
        app.window_status(window, method)


def test_restore_window(instance, fake_root):
    app = instance(Factory)
    frame = tk.Frame(fake_root)
    frame.destroy = MagicMock()
    app.restore_root_window(fake_root, frame)
    frame.destroy.assert_called_once()


@pytest.mark.parametrize("window, method, msg", test_container_3)
def test_restore_window_invalid(instance, window, method, msg):
    app = instance(Factory)
    with pytest.raises(ValueError, match=msg):
        app.restore_root_window(window, method)


@patch("os.path.exists", return_value=True)
def test_save_results(_, instance, tmp_path):
    app = instance(Factory)
    file_path = tmp_path / "test.json"

    app.read_and_write_file = MagicMock(
        side_effect=lambda path, mode, data=None: ([] if mode == "r" else None)
    )

    app.info_message = MagicMock()
    app.error_message = MagicMock()

    entries = [("Яблоко", 150.0, 78.0), ("Банан", 200.0, 120.0)]

    app.save_results(str(file_path), entries)
    app.read_and_write_file.assert_any_call(str(file_path), "r")
    app.read_and_write_file.assert_any_call(str(file_path), "w", ANY)
    app.info_message.assert_called_once()
    app.error_message.assert_not_called()

    # --- INVALID INPUT --- #
    bad_entries = [("Плохое", 123)]
    app.save_results(str(file_path), bad_entries)
    app.error_message.assert_called_with(
        "Ошибка", "Некорректный формат данных для сохранения."
    )


def test_read_and_write(instance, tmp_path):
    app = instance(Factory)
    file_path = tmp_path / "test.json"
    data = {"key": "value"}

    app.read_and_write_file(file_path, "w", data)

    with open(file_path) as f:
        read_data = app.read_and_write_file(file_path, "r")
        assert read_data == data


@pytest.mark.parametrize("data, method, msg", test_container_4)
def test_read_and_write_invalid(instance, data, method, msg, tmp_path):
    app = instance(Factory)
    file_path = tmp_path / "test.json"
    with pytest.raises(ValueError, match=msg):
        app.read_and_write_file(file_path, method, data)


def test_write_none_data_returns_none(instance, tmp_path):
    app = instance(Factory)
    file_path = tmp_path / "test.json"
    result = app.read_and_write_file(file_path, "w", None)
    assert result is None


@patch("builtins.quit")
@patch("config_manager.reset_config")
def test_reset_config_settings(mock_reset_config, mock_quit, instance):
    app = instance(Factory)
    app.info_message = MagicMock()
    app.reset_config_settings()

    mock_reset_config.assert_called_once()
    app.info_message.assert_any_call("Успех", "Языковые настройки сброшены!")
    app.info_message.assert_any_call("Инфо", "Приложение будет закрыто.")
    mock_quit.assert_called_once()
