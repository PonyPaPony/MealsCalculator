import logging
from logging.handlers import RotatingFileHandler


# from gettext import gettext as _
def setup_logger(level=logging.INFO, log_path="logs/app.log"):
    logger = logging.getLogger()
    if logger.handlers:
        return

    log_formater = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    log_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    log_handler.setFormatter(log_formater)

    logger.setLevel(level)
    logger.addHandler(log_handler)

    logging.info(_("Приложение Запущено"))
