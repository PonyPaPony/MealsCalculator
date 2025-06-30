from gettext import gettext as _
from unittest.mock import ANY, MagicMock, patch

import pytest

from localization import Localization, SetupLanguage


@pytest.fixture
def error():
    return MagicMock()


@pytest.mark.parametrize("language", ["en", "ru"])
def test_setup_language_valid(monkeypatch, instance, language):
    mock_translation = MagicMock()
    monkeypatch.setattr("gettext.translation", lambda *a, **k: mock_translation)

    setup = instance(SetupLanguage)
    setup.setup_language(language)

    mock_translation.install.assert_called_once()


def test_setup_language_invalid(monkeypatch, instance):
    monkeypatch.setattr("localization._", lambda x: x)
    monkeypatch.setattr(
        "gettext.translation",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("not found")),
    )

    setup = instance(SetupLanguage)
    setup.setup_language("nonexistent")

    setup._mocks["error_handler"].assert_called_once_with(
        _("Ошибка"), _("Файл перевода не найден.")
    )


def test_on_close_with_root(instance):
    cmd = instance(Localization)
    cmd.root = MagicMock()

    cmd._on_close()

    cmd.root.destroy.assert_called_once()


def test_on_close_without_root(monkeypatch, instance, error):
    monkeypatch.setattr("localization._", lambda x: x)
    cmd = instance(Localization, error_handler=error)
    cmd.root = None

    cmd._on_close()

    error.assert_called_once_with("Ошибка", "Экземпляр tkinter не существует.")


@patch("localization.MainController")
@patch("localization.DataDefaults")
@patch("localization.ProductManager")
@patch("localization.ProductContext")
@patch("localization.Factory")
@pytest.mark.parametrize("language", ["en", "ru"])
def test_start_with_root_calls_destroy(
    mock_factory, mock_context, mock_manager, mock_data, mock_main, language, instance
):
    cmd = instance(Localization)
    cmd.root = MagicMock()
    cmd.start_application_with_language(language, cmd.root)

    mock_factory.assert_called_once_with(language)
    mock_factory.return_value.window_status.assert_called_with(cmd.root, "hide")
    mock_context.assert_called_once_with(language)
    mock_manager.assert_called_once_with(mock_context.return_value)
    mock_data.assert_called_once_with(language)
    cmd.root.destroy.assert_called_once()
    mock_main.assert_called_once_with(language)
    mock_main.return_value.run.assert_called_once()


@patch(
    "localization.read_config", return_value=("ru", ["path_ru.json", "path_en.json"])
)
@patch.object(Localization, "setup_language")
@patch.object(Localization, "start_application_with_language")
def test_run_with_saved_language(mock_start, mock_setup, mock_read, instance):
    app = instance(Localization)
    app.run()

    mock_setup.assert_called_once_with("ru")
    mock_start.assert_called_once_with("ru")
    mock_read.assert_called_once()


@patch(
    "localization.read_config", return_value=(None, ["path_ru.json", "path_en.json"])
)
@patch.object(Localization, "init_window")
@patch.object(Localization, "setup_language")
@patch.object(Localization, "start_application_with_language")
def test_run_without_saved_language(
    mock_start, mock_setup, mock_init, mock_read, instance
):
    app = instance(Localization)
    app.run()

    mock_read.assert_called_once()
    mock_setup.assert_not_called()
    mock_start.assert_not_called()
    mock_init.assert_called_once()


@patch("localization.write_config")
@patch.object(Localization, "setup_language")
@patch.object(Localization, "start_application_with_language")
def test_get_lang_code_behavior(mock_start, mock_setup, mock_write, instance):
    app = instance(Localization)
    app.root = MagicMock()
    app.apply_language_and_start("en")

    mock_write.assert_called_once_with("en")
    mock_setup.assert_called_once_with("en")
    mock_start.assert_called_once_with("en", app.root)


def test_init_window(instance, mock_tkinter):
    cmd = instance(Localization)
    cmd.init_window()

    # Проверяем, что Tk() вызвался
    mock_tkinter["Tk"].assert_called_once()

    # Проверяем вызовы root
    mock_tkinter["tk_instance"].title.assert_called_once_with(
        "Выбор Языка / Set Language"
    )
    mock_tkinter["tk_instance"].geometry.assert_called_once_with("500x350")
    mock_tkinter["tk_instance"].protocol.assert_called_once_with(
        "WM_DELETE_WINDOW", ANY
    )

    # Проверяем создание Frame
    mock_tkinter["Frame"].assert_called_once_with(mock_tkinter["tk_instance"])
    mock_tkinter["frame_instance"].grid.assert_called_once_with(
        row=0, column=0, columnspan=1, padx=10, pady=10, sticky="nsew"
    )

    # Проверяем создание Button's и ежи с ними.
    assert mock_tkinter["Button"].call_count == 3

    button_calls = mock_tkinter["Button"].call_args_list
    button_texts = [call.kwargs["text"] for call in button_calls]

    assert "Russian/Русский" in button_texts
    assert "English/Английский" in button_texts
    assert "Exit/Выход" in button_texts

    assert mock_tkinter["button_instance"].grid.call_count == 3

    # Проверяем вызовы конфигурации.
    for i in range(3):
        mock_tkinter["frame_instance"].grid_rowconfigure.assert_any_call(i, weight=1)
    mock_tkinter["frame_instance"].grid_columnconfigure.assert_called_once_with(
        0, weight=1
    )

    mock_tkinter["tk_instance"].grid_rowconfigure.assert_called_once_with(0, weight=1)
    mock_tkinter["tk_instance"].grid_columnconfigure.assert_called_once_with(
        0, weight=1
    )
    mock_tkinter["tk_instance"].mainloop.assert_called_once()
