import logging
import tkinter as tk
from gettext import gettext as _
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gui_factory import set_window_icon

logger = logging.getLogger(__name__)


@pytest.fixture
def fake_script_path():
    # Путь к "фейковому" файлу gui_factory.py в структуре проекта (например, .../src/gui_factory.py)
    return Path.cwd() / "src" / "gui_factory.py"


@pytest.fixture
def expected_icon_path(fake_script_path):
    # Ожидаемый путь к иконке относительно fake_script_path
    return fake_script_path.parent.parent / "resources" / "icon.ico"


def test_set_window_icon(monkeypatch, fake_script_path, expected_icon_path):
    """
    Тест: Проверяем, что set_window_icon корректно формирует путь к иконке
    и вызывает метод iconbitmap с правильным аргументом,
    если файл иконки существует.
    """
    # Мокаем путь к модулю gui_factory
    monkeypatch.setattr("gui_factory.__file__", str(fake_script_path))

    mock_window = MagicMock(spec=tk.Tk)

    # Мокаем проверку существования файла иконки как True
    with patch("pathlib.Path.exists", return_value=True):
        set_window_icon(mock_window)

    # Проверяем, что iconbitmap вызван один раз с ожидаемым путем
    mock_window.iconbitmap.assert_called_once_with(expected_icon_path)

    actual_path = mock_window.iconbitmap.call_args[0][0]
    assert isinstance(
        actual_path, Path
    ), f"Аргумент должен быть Path, но был {type(actual_path)}"
    assert (
        actual_path == expected_icon_path
    ), f"Ожидался путь {expected_icon_path}, но был {actual_path}"

    logger.info(fake_script_path)
    logger.info(expected_icon_path)


def test_icon_not_found(expected_icon_path):
    """
    Тест: Проверяем поведение, когда иконка не найдена.
    Ожидается, что iconbitmap не вызывается,
    и появляется предупреждение в логах.
    """
    with patch("pathlib.Path.exists", return_value=False) as mock_exists, patch(
        "gui_factory.logger"
    ) as mock_logger:
        mock_window = MagicMock(spec=tk.Tk)
        set_window_icon(mock_window)

    msg = f"Иконка {expected_icon_path} не найдена. Используется стандартная иконка."
    mock_window.iconbitmap.assert_not_called()
    mock_logger.warning.assert_called_once_with(msg)
    logger.info(msg)


def test_window_icon_not_found():
    """
    Тест: Проверяем поведение функции при вызове без аргумента окна.
    Ожидается, что появится ошибка в логах,
    и никаких вызовов iconbitmap и warning не произойдет.
    """
    with patch("gui_factory.logger") as mock_logger:
        set_window_icon()

    msg = _("Ошибка: Не указан экземпляр Tkinter.")

    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_called_once_with(msg)
