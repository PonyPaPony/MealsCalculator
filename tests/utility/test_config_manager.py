import configparser
import logging
import os
from unittest.mock import patch

import pytest
from config_manager import read_config, reset_config, write_config

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def cleanup_config(fake_config):
    """
    Автоматически удаляет временный конфиг-файл до и после каждого теста.
    """
    if os.path.exists(fake_config):
        os.remove(fake_config)
    yield
    if os.path.exists(fake_config):
        os.remove(fake_config)


@pytest.mark.parametrize("lang", ["ru", "en"])
def test_config_functional(fake_config, lang):
    """
    Проверяет базовую функциональность конфиг-менеджера:
    - запись языка и путей в конфиг;
    - чтение сохранённых значений;
    - корректный сброс конфигурации.
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        logger.info(f"Тест: Запись и чтение конфигурации с языком '{lang}'")
        write_config(lang)
        saved_lang, file_paths = read_config()

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        path_ru = os.path.join(project_root, "data/products/products_ru.json")
        path_en = os.path.join(project_root, "data/products/products_en.json")

        assert saved_lang == lang, f"Ожидался язык '{lang}', получен '{saved_lang}'"
        assert file_paths[0] == path_ru, "Неверный путь к русскому файлу"
        assert file_paths[1] == path_en, "Неверный путь к английскому файлу"

        logger.info("Тест: Проверка сброса конфигурации")
        reset_config()
        saved_lang, file_paths = read_config()

        assert saved_lang is None, "После сброса язык должен быть None"
        assert file_paths == [None, None], "После сброса пути должны быть [None, None]"
        logger.info("Тест: Завершен успешно.")


def test_without_config_file(fake_config):
    """
    Проверяет, что чтение конфигурации без существующего файла возвращает (None, []).
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        logger.info("Тест: Чтение отсутствующего конфиг файла")
        saved_lang, file_paths = read_config()

        assert saved_lang is None, "Язык должен быть None, если конфиг отсутствует"
        assert (
            file_paths == []
        ), "Пути должны быть пустым списком, если конфиг отсутствует"
        logger.info("Тест: Завершен успешно.")


def test_read_with_missing_key(fake_config):
    """
    Проверяет чтение конфигурации с секциями без ключей (пустые словари).
    Ожидается (None, [None, None]).
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        config = configparser.ConfigParser()
        config["settings"] = {}
        config["file_path"] = {}
        with open(fake_config, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        saved_lang, file_paths = read_config()
        assert (
            saved_lang is None
        ), "Язык должен быть None при отсутствии ключа 'language'"
        assert file_paths == [
            None,
            None,
        ], "Пути должны быть [None, None] при отсутствии ключей"


def test_read_config_missing_settings_section(fake_config):
    """
    Проверяет поведение при наличии пустого конфига без секций.
    Ожидается (None, [None, None]).
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        logger.info("Тест: Чтение пустого config.ini без секций")
        config = configparser.ConfigParser()
        # Пишем пустой файл (без секций)
        with open(fake_config, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        saved_lang, file_paths = read_config()
        assert (
            saved_lang is None
        ), "Язык должен быть None при отсутствии секции 'settings'"
        assert file_paths == [
            None,
            None,
        ], "Пути должны быть [None, None] при отсутствии секции 'file_path'"


def test_read_corrupted_config(fake_config):
    """
    Проверяет, что при повреждённом ini-файле функция read_config корректно возвращает (None, [None, None]).
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        logger.info("Тест: Чтение поврежденного ini файла")
        with open(fake_config, "w", encoding="utf-8") as configfile:
            configfile.write("::: this is not valid ini :::")

        saved_lang, file_paths = read_config()
        assert saved_lang is None, "Язык должен быть None при повреждённом файле"
        assert file_paths == [
            None,
            None,
        ], "Пути должны быть [None, None] при повреждённом файле"


def test_read_empty_file(fake_config):
    """
    Проверяет чтение пустого файла (0 байт).
    Ожидается (None, [None, None]).
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        logger.info("Тест: Чтение пустого файла (0 байт)")
        with open(fake_config, "w", encoding="utf-8") as f:
            pass  # создаём пустой файл

        saved_lang, file_paths = read_config()
        assert saved_lang is None, "Язык должен быть None при пустом файле"
        assert file_paths == [
            None,
            None,
        ], "Пути должны быть [None, None] при пустом файле"


def test_read_config_returns_nothing(fake_config):
    """
    Проверяет поведение, когда ConfigParser.read возвращает пустой список,
    имитируя, что файл не был прочитан.
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        with open(fake_config, "w", encoding="utf-8") as f:
            f.write("")

        with patch("configparser.ConfigParser.read", return_value=[]):
            saved_lang, file_paths = read_config()
            assert saved_lang is None, "Язык должен быть None, если файл не прочитан"
            assert file_paths == [
                None,
                None,
            ], "Пути должны быть [None, None], если файл не прочитан"


def test_write_and_reset_config_contents(fake_config):
    """
    Проверяет содержимое файла конфигурации после записи и сброса.
    """
    with patch("config_manager.CONFIG_PATH", str(fake_config)):
        write_config("ru")

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        path_ru = os.path.join(project_root, "data/products/products_ru.json")

        config = configparser.ConfigParser()
        config.read(fake_config)
        assert (
            config.get("settings", "language") == "ru"
        ), "Язык в конфиге должен быть 'ru'"
        assert (
            config.get("file_path", "path_ru") == path_ru
        ), "Путь к русскому файлу некорректен"

        reset_config()
        # Повторно читаем конфиг после сброса
        config = configparser.ConfigParser()
        config.read(fake_config)
        assert (
            config.get("settings", "language") == ""
        ), "После сброса язык должен быть пустой строкой"
