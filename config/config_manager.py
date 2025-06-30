import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.ini")


def read_config():
    """
    Считывает конфигурацию из файла config.ini.

    Возвращает кортеж (language, file_paths), где:
        - language: строка с кодом языка из секции [settings], либо None,
        - file_paths: список из двух элементов [path_ru, path_en], где
          path_ru и path_en — пути из секции [file_path], либо [None, None]
          если ключи отсутствуют или файл повреждён.

    В случае отсутствия файла возвращает (None, []).

    Если файл существует, но:
        - не прочитан,
        - отсутствуют необходимые секции,
        - отсутствуют ключи,
    возвращает (None, [None, None]).

    При возникновении ошибки чтения (например, синтаксическая ошибка в ini)
    возвращает (None, [None, None]).
    """
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        try:
            read_files = config.read(CONFIG_PATH)
            if not read_files:
                # файл пустой или не прочитан
                return None, [None, None]

            if not config.has_section("settings") or not config.has_section(
                "file_path"
            ):
                return None, [None, None]

            language = config.get("settings", "language", fallback=None)
            path_ru = config.get("file_path", "path_ru", fallback=None)
            path_en = config.get("file_path", "path_en", fallback=None)

            if language is None and path_ru is None and path_en is None:
                return None, [None, None]

            return language, [path_ru, path_en]
        except configparser.Error:
            return None, [None, None]
    return None, []


def write_config(lang_code):
    """
    Записывает базовую конфигурацию в файл config.ini.

    Аргументы:
        lang_code (str): код языка для записи в секцию [settings].

    Записывает в конфиг:
        - в секцию [settings]: ключ language с переданным значением,
        - в секцию [file_path]: ключи path_ru и path_en с фиксированными путями
          к русской и английской версии файлов продуктов.

    Создаёт или перезаписывает файл config.ini.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Строим абсолютные пути для файлов
    path_ru = os.path.join(project_root, "data/products/products_ru.json")
    path_en = os.path.join(project_root, "data/products/products_en.json")

    config = configparser.ConfigParser()
    config["settings"] = {"language": lang_code}
    config["file_path"] = {
        "path_ru": path_ru,
        "path_en": path_en,  # Убрал лишний апостроф
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as configfile:
        config.write(configfile)


def reset_config():
    """
    Сбрасывает конфигурацию, записывая пустой язык в config.ini.

    Записывает в секцию [settings]:
        - ключ language со значением пустой строки.

    Используется для очистки или инициализации состояния конфига.
    """
    config = configparser.ConfigParser()
    config["settings"] = {"language": ""}
    with open(CONFIG_PATH, "w", encoding="utf-8") as configfile:
        config.write(configfile)
