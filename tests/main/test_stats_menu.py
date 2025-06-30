from unittest.mock import MagicMock, patch

import pytest
from matplotlib.figure import Figure

from main_controller import MainController


@pytest.fixture
def controller(instance):
    return instance(MainController, language="ru")


def test_show_stats_window_empty_stats(controller):
    mock_win = MagicMock()
    mock_frame = MagicMock()

    controller._win_ = MagicMock(return_value=mock_win)
    controller.builder = MagicMock()  # 🔧 Добавлено
    controller.builder.create_scrollable_frame.return_value = mock_frame
    controller.builder.create_label = MagicMock()
    controller.settings.label_grid = {"padx": 5}
    controller.settings.font_10 = {"font": "Arial"}

    controller.show_stats_window("Test Title", [])

    controller._win_.assert_called_once_with("Test Title", "700x500")
    controller.builder.create_scrollable_frame.assert_called_once_with(mock_win)

    controller.builder.create_label.assert_called_once_with(
        mock_frame,
        text="Нет данных за указанный период",
        grid={"padx": 5},
        style={"font": "Arial"},
    )


@patch("main_controller.plt")  # Патчим matplotlib.pyplot
@patch("main_controller.FigureCanvasTkAgg")  # Патчим отрисовку в Tkinter
def test_show_stats_window_with_data(mock_canvas, mock_plt, controller):
    mock_win = MagicMock()
    mock_frame = MagicMock()
    mock_fig = MagicMock(spec=Figure)
    mock_ax = MagicMock()

    mock_plt.subplots.return_value = (mock_fig, mock_ax)

    controller._win_ = MagicMock(return_value=mock_win)
    controller.builder = MagicMock()  # 🔧 Добавлено
    controller.builder.create_scrollable_frame.return_value = mock_frame

    # Пример входных данных
    stats = [
        {"timestamp": "2025-06-01T12:00:00", "total": 250.5},
        {"timestamp": "2025-06-02T12:00:00", "total": 300.0},
    ]

    controller.show_stats_window("Stats Title", stats)

    # Проверка вызовов
    controller._win_.assert_called_once_with("Stats Title", "700x500")
    controller.builder.create_scrollable_frame.assert_called_once_with(mock_win)

    # Проверка построения графика
    mock_plt.subplots.assert_called_once_with(figsize=(6, 4))
    mock_ax.plot.assert_called_once()
    mock_ax.set_xlabel.assert_called_once_with("Дата")
    mock_ax.set_ylabel.assert_called_once_with("Итого Калорий")
    mock_ax.set_title.assert_called_once_with("Калорий за День")
    mock_ax.grid.assert_called_once_with(True)
    mock_ax.legend.assert_called_once()

    # Проверка аннотаций на точках
    assert mock_ax.annotate.call_count == len(stats)

    # Проверка размещения графика
    mock_canvas.assert_called_once_with(mock_fig, master=mock_frame)
    mock_canvas.return_value.draw.assert_called_once()
    mock_canvas.return_value.get_tk_widget.return_value.grid.assert_called_once_with(
        row=0, column=0, sticky="nsew"
    )

    # Проверка конфигурации сетки
    mock_frame.grid_columnconfigure.assert_called_once_with(0, weight=1)
    mock_win.grid_rowconfigure.assert_called_once_with(0, weight=1)
    mock_win.grid_columnconfigure.assert_called_once_with(0, weight=1)
