import logging
from unittest.mock import MagicMock, patch

from log import setup_logger


def test_logger_return_if_already_initialized(tmp_path):
    temp_log_path = tmp_path / "app.log"
    logger = logging.getLogger()
    # Сохраним оригинальные обработчики
    original_handlers = logger.handlers[:]
    logger.handlers.clear()

    with (
        patch("log.RotatingFileHandler") as mock_handler_cls,
        patch("logging.info") as mock_info,
    ):
        mock_handler = MagicMock()
        mock_handler_cls.return_value = mock_handler

        # Первый вызов: инициализация логгера
        setup_logger(log_path=str(temp_log_path))
        assert mock_handler_cls.call_count == 1
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1

        mock_info.assert_called_with("Приложение Запущено")

        # Второй вызов: не должен создавать новый обработчик
        setup_logger(log_path=str(temp_log_path))
        assert mock_handler_cls.call_count == 1  # не добавился новый

    # Восстановим оригинальные обработчики
    logger.handlers = original_handlers
