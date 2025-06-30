import tkinter as tk
from gettext import gettext as _
from unittest.mock import ANY, MagicMock, patch

import pytest

from main_controller import MainController


class MockController:
    def __init__(self, instance, language, with_attrs=False):
        with patch("main_controller.DataDefaults"), patch(
            "main_controller.ProductContext"
        ), patch("main_controller.ProductManager"), patch(
            "main_controller.ProductCalculator"
        ), patch(
            "main_controller.Factory"
        ), patch(
            "main_controller.WidgetBuilder"
        ), patch(
            "main_controller.StatsManager"
        ), patch(
            "main_controller.tk.Tk"
        ) as mock_tk:

            self.language = language
            self.main = instance(
                MainController,
                language=language,
                info_handler=MagicMock(),
                error_handler=MagicMock(),
            )
            self._set_mocks(mock_tk)
            if with_attrs:
                self._set_attrs()

    def _set_attrs(self):
        self.attrs = {
            "frame_grid": {"padx": 10},
            "button_grid": {"sticky": "ew"},
            "font_12": {"font": "Arial"},
            "green": {"bg": "green"},
            "red": {"bg": "red"},
            "blue": {"bg": "blue"},
        }

    def _set_mocks(self, mock_tk):
        self.window_mock = MagicMock()
        mock_tk.return_value.mainloop = MagicMock()

        self.main.info_message = MagicMock()
        self.main.error_message = MagicMock()

        self.main.create_buttons = MagicMock(wraps=self.main.create_buttons)

        self.main.builder.create_widgets = MagicMock()
        self.main.builder.create_button = MagicMock()
        self.main.builder.create_frame = MagicMock()
        self.main.builder.create_label = MagicMock()
        self.main.builder.create_scrollable_frame = MagicMock()

        self.main.factory.on_close = MagicMock()
        self.main.factory.reset_config_settings = MagicMock()
        self.main.factory.restore_root_window = MagicMock()

        self.main.calculator.create_input_product_row = MagicMock()
        self.main.calculator.calculate_total = MagicMock()

        self.main.manager.root_for_window = MagicMock()

        self.main.stats_manager.get_stats_by_period = MagicMock()


test_case = [
    ("Выход", 0, {"bg": "red"}),
    ("Exit", 0, {"bg": "red"}),
    ("Cбросить Языковые Настройки", 0, {"bg": "blue"}),
    ("Reset Language Settings", 0, {"bg": "blue"}),
    ("Назад", 1, {"bg": "red"}),
    ("Back", 1, {"bg": "red"}),
    ("Рассчитать", 1, {"bg": "blue"}),
    ("Calculate", 1, {"bg": "blue"}),
]
test_case_2 = [
    ("Рассчитать Калории", "500x500"),
    ("Меню управления продуктами", "500x350"),
]


@pytest.fixture
def app(instance):
    return MockController(instance, "ru", with_attrs=True)


@pytest.fixture
def controller(app):
    for attr_name, value in app.attrs.items():
        setattr(app.main.settings, attr_name, value)
    return app.main


def test_run_method(controller):
    mock_root = MagicMock()
    mock_frame = MagicMock()

    controller.builder.create_widgets.return_value = mock_root
    controller.builder.create_frame.return_value = mock_frame

    controller.open_calculate_window = MagicMock()
    controller.open_manager_products_menu = MagicMock()
    controller.open_stats_menu = MagicMock()

    controller.run()

    controller.builder.create_widgets.assert_called_once_with(
        cls=tk.Tk, title=_("Главное Меню"), size="500x350"
    )
    controller.builder.create_frame.assert_called_once_with(
        mock_root, grid={"padx": 10}
    )

    assert controller.create_buttons.call_count == 1

    with patch("main_controller.MainController.create_buttons"):
        assert controller.builder.create_button.call_count == 5

    commands = [
        controller.open_calculate_window,
        controller.open_manager_products_menu,
        controller.open_stats_menu,
        controller.factory.on_close,
        controller.factory.reset_config_settings,
    ]

    for idx, call in enumerate(controller.builder.create_button.call_args_list):
        cmd = call.args[2]
        if idx == 3:
            cmd()
            controller.factory.on_close.assert_called_with(mock_root)
        else:
            cmd()
            commands[idx].assert_called_once()

    mock_root.protocol.assert_called_once_with("WM_DELETE_WINDOW", ANY)
    protocol_callback = mock_root.protocol.call_args[0][1]
    protocol_callback()
    controller.factory.on_close.assert_called_with(mock_root)
    mock_root.mainloop.assert_called_once()


@pytest.mark.parametrize("text, case, expected", test_case)
def test_get_button_style(controller, text, case, expected):
    base_style = {"font": "Arial", "bg": "green"}

    result = controller.get_button_style(text, case)

    assert result["font"] == base_style["font"]

    if expected:
        assert result["bg"] == expected["bg"]
    else:
        assert result["bg"] == base_style["bg"]


@pytest.mark.parametrize("text, size", test_case_2)
def test_win(controller, text, size):
    mock_root = MagicMock()
    mock_win = MagicMock()

    controller.root = mock_root
    controller.builder.create_widgets.return_value = mock_win
    controller.builder.create_frame.return_value = MagicMock()
    controller.factory.window_status = MagicMock()

    result = controller._win_(title=text, size=size)

    controller.factory.window_status.assert_called_once_with(mock_root, "hide")
    controller.builder.create_widgets.assert_called_once_with(
        cls=tk.Toplevel, title=_(text), size=size
    )

    mock_win.protocol.assert_called_once_with("WM_DELETE_WINDOW", ANY)

    callback = mock_win.protocol.call_args[0][1]
    callback()
    controller.factory.on_close.assert_called_once_with(mock_root, mock_win)

    assert result == mock_win


@pytest.mark.parametrize("products_exist", [True, False])
def test_open_calculate_window(controller, products_exist):
    controller.manager.products = ["product1"] if products_exist else []
    if not products_exist:
        controller.open_calculate_window()
        controller.error_message.assert_called_once_with(
            _("Ошибка"), _("Нет продуктов для расчёта.")
        )
    else:
        controller._win_ = MagicMock()
        controller.builder.create_frame.return_value = MagicMock()
        controller.builder.create_scrollable_frame.return_value = MagicMock()
        controller.root = MagicMock()

        controller.open_calculate_window()

        controller._win_.assert_called_once_with("Рассчитать калории", "500x500")
        controller.calculator.create_input_product_row.assert_called_once()
        assert controller.builder.create_button.call_count == 3

        calculate_command = controller.builder.create_button.call_args_list[1].args[2]
        calculate_command()
        controller.calculator.calculate_total.assert_called_once()

        back_command = controller.builder.create_button.call_args_list[2].args[2]
        back_command()
        controller.factory.restore_root_window.assert_called_once()


def test_open_manager_products_menu(controller):
    mock_win = MagicMock()
    controller._win_ = MagicMock(return_value=mock_win)
    controller.builder.create_frame.return_value = MagicMock()
    controller.root = MagicMock()

    controller.open_manager_products_menu()

    controller._win_.assert_called_once_with("Меню управления продуктами", "500x350")
    assert controller.builder.create_button.call_count == 4

    tags = ["Append", "Delete", "Change"]
    for idx, tag in enumerate(tags):
        button_call = controller.builder.create_button.call_args_list[idx]
        command = button_call.kwargs["command"]
        command()
        controller.manager.root_for_window.assert_any_call(mock_win, tag=tag)

    back_command = controller.builder.create_button.call_args_list[3].kwargs["command"]
    back_command()
    controller.factory.restore_root_window.assert_called_once()


def test_show_error_calls_error_message_and_logger(controller):
    with patch("main_controller.logger") as mock_logger:
        controller.show_error("Test", "Best")
        controller.error_message.assert_called_once_with(_("Test"), _("Best"))
        mock_logger.error.assert_called_once_with("Test: Best")


def test_open_stats_menu(controller):
    mock_win = MagicMock()
    mock_frame = MagicMock()
    controller._win_ = MagicMock(return_value=mock_win)
    controller.builder.create_frame.return_value = mock_frame
    controller.root = MagicMock()

    # Настройка mock для stats_manager
    stats_week = MagicMock()
    stats_month = MagicMock()
    stats_all = MagicMock()

    controller.stats_manager.get_stats_by_period.side_effect = [
        stats_week,
        stats_month,
        stats_all,
    ]

    controller.show_stats_window = MagicMock()

    controller.open_stats_menu()

    # Проверка создания окна и фрейма
    controller._win_.assert_called_once_with("Показать статистику", "500x350")
    controller.builder.create_frame.assert_called_once_with(
        mock_win, grid=controller.settings.frame_grid
    )

    # Проверка кнопок
    assert controller.builder.create_button.call_count == 5

    button_texts = [
        "Статистика за 7 дней:",
        "Статистика за 30 дней:",
        "Статистика за указанный период:",
        "Статистика за все время:",
        "Назад",
    ]

    for idx, call in enumerate(controller.builder.create_button.call_args_list):
        assert call.kwargs["text"] == button_texts[idx]
        assert call.kwargs["grid"]["row"] == idx

        style = call.kwargs["style"]
        if button_texts[idx] in ["Назад", "Back"]:
            assert style["bg"] == controller.settings.red["bg"]
        else:
            assert style["bg"] == controller.settings.green["bg"]
        assert style["font"] == controller.settings.font_12["font"]

    # Проверка, что колбэки вызываются корректно
    # Статистика за 7 дней
    call_7_days = controller.builder.create_button.call_args_list[0]
    call_7_days.kwargs["command"]()
    controller.show_stats_window.assert_any_call("7 дней", stats_week)

    # Статистика за 30 дней
    call_30_days = controller.builder.create_button.call_args_list[1]
    call_30_days.kwargs["command"]()
    controller.show_stats_window.assert_any_call("30 дней", stats_month)

    # Пропускаем кнопку без команды (индекс 2)

    # Статистика за всё время
    call_all_time = controller.builder.create_button.call_args_list[3]
    call_all_time.kwargs["command"]()
    controller.show_stats_window.assert_any_call("Все время", stats_all)

    # Назад
    call_back = controller.builder.create_button.call_args_list[4]
    call_back.kwargs["command"]()
    controller.factory.restore_root_window.assert_called_once_with(
        controller.root, mock_win
    )

    # Проверка настройки сетки
    assert mock_frame.grid_rowconfigure.call_count == 6  # кнопок 5 + 1
    mock_frame.grid_columnconfigure.assert_called_once_with(0, weight=1)
    mock_win.grid_rowconfigure.assert_called_once_with(0, weight=1)
    mock_win.grid_columnconfigure.assert_called_once_with(0, weight=1)
