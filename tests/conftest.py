import configparser
import inspect
import logging
import tkinter as tk
import types
from unittest.mock import MagicMock, patch

import pytest

# --- Умное создание моков по типам --- #


def smart_mock(name, hint):
    if hint is None:
        return MagicMock(name=f"mock_{name}")
    if hint is str:
        return f"mocked_{name}"
    if hint is int:
        return 0
    if hint is bool:
        return False
    if hint is list:
        return []
    if hint is dict:
        return {}
    if hint is float:
        return 0.0
    if hint is set:
        return set()
    if hint is types.FunctionType:
        return MagicMock(name=f"mock_func_{name}")
    if callable(hint):
        return MagicMock(name=f"mock_callable_{name}")
    return MagicMock(name=f"mock_{name}")


def auto_mock_factory(cls, *args, **kwargs):
    sig = inspect.signature(cls.__init__)
    params = sig.parameters

    final_kwargs = dict(kwargs)
    mocks = {}

    for name, param in params.items():
        if name == "self":
            continue
        if name == "context":  # Исключаем context, если он уже есть в final_kwargs
            continue
        if name not in final_kwargs:
            hint = param.annotation if param.annotation != inspect._empty else None
            mock = smart_mock(name, hint)
            final_kwargs[name] = mock
            mocks[name] = mock
        elif isinstance(final_kwargs[name], MagicMock):
            mocks[name] = final_kwargs[name]

    instance = cls(*args, **final_kwargs)
    instance._mocks = mocks
    return instance


# --- Pytest Fixtures --- #


@pytest.fixture
def instance():
    """Фикстура фабрики моков."""
    return auto_mock_factory


@pytest.fixture
def fake_config(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("configs")
    config_path = tmp_dir / "test_config.ini"
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"language": "en"}
    with open(config_path, "w") as f:
        config.write(f)
    return config_path


@pytest.fixture
def fake_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def mock_tkinter():
    with (
        patch("tkinter.Tk") as mock_tk,
        patch("tkinter.Toplevel") as mock_toplevel,
        patch("tkinter.Frame") as mock_frame,
        patch("tkinter.Button") as mock_button,
        patch("tkinter.Scrollbar") as mock_scrollbar,
        patch("tkinter.Listbox") as mock_listbox,
        patch("tkinter.Label") as mock_label,
        patch("tkinter.Entry") as mock_entry,
    ):

        mocks = {
            "Tk": mock_tk,
            "Toplevel": mock_toplevel,
            "Frame": mock_frame,
            "Button": mock_button,
            "Scrollbar": mock_scrollbar,
            "Listbox": mock_listbox,
            "Entry": mock_entry,
            "Label": mock_label,
            "tk_instance": MagicMock(),
            "toplevel_instance": MagicMock(),
            "frame_instance": MagicMock(),
            "button_instance": MagicMock(),
            "scrollbar_instance": MagicMock(),
            "listbox_instance": MagicMock(),
            "entry_instance": MagicMock(),
            "label_instance": MagicMock(),
        }

        mock_tk.return_value = mocks["tk_instance"]
        mock_toplevel.return_value = mocks["toplevel_instance"]
        mock_frame.return_value = mocks["frame_instance"]
        mock_button.return_value = mocks["button_instance"]
        mock_scrollbar.return_value = mocks["scrollbar_instance"]
        mock_listbox.return_value = mocks["listbox_instance"]
        mock_entry.return_value = mocks["entry_instance"]
        mock_label.return_value = mocks["label_instance"]

        yield mocks


def pytest_configure():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
