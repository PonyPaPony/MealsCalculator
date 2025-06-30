import json
import logging
import os
from collections.abc import Callable
from tkinter import messagebox
from typing import Any

# from gettext import gettext as _
from config_manager import read_config

logger = logging.getLogger(__name__)
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class DataDefaults:
    def __init__(
        self,
        language: str,
        path_ru=None,
        path_en=None,
        info_handler: Callable[[str, str], None] | None = None,
        error_handler: Callable[[str, str], None] | None = None,
    ):

        # -- Log_Settings -- #
        self.log = logger.error
        self.info_message = info_handler or messagebox.showinfo
        self.error_message = error_handler or messagebox.showerror
        self.language = language

        # -- File-Path -- #
        if path_ru is None or path_en is None:
            lang, paths = read_config()
            path_ru = path_ru or (paths[0] if paths else None)
            path_en = path_en or (paths[1] if paths else None)
        self.PRODUCTS_LIST_RU = path_ru or path + "/data/products/products_ru.json"
        self.PRODUCTS_LIST_EN = path_en or path + "/data/products/products_en.json"
        self.MEALS_LIST = path + "/data/meals.json"

        # -- Colors -- #
        self.red = {"bg": "#f44336"}
        self.blue = {"bg": "#2196f3"}
        self.green = {"bg": "#4CAF50"}

        # -- Styles -- #
        self.font_10 = {"font": ("Arial", 10, "bold")}
        self.font_10_ = {"fg": "white", "relief": "flat", "font": ("Arial", 10, "bold")}
        self.font_12 = {"fg": "white", "relief": "flat", "font": ("Arial", 12, "bold")}

        # -- Geometry Settings -- #
        self.frame_grid = {
            "row": 0,
            "column": 0,
            "columnspan": 1,
            "padx": 10,
            "pady": 10,
            "sticky": "nsew",
        }
        self.button_grid = {
            "row": 0,
            "column": 0,
            "padx": 10,
            "pady": 10,
            "sticky": "ew",
        }
        self.button_grid_low = {
            "row": 0,
            "column": 0,
            "padx": 5,
            "pady": 5,
            "sticky": "ew",
        }
        self.label_grid = {"row": 0, "column": 0, "padx": 5, "pady": 5}
        self.entry_grid = {"row": 0, "column": 1, "padx": 5, "pady": 5}
        # -- Listbox Settings -- #
        self.listbox_style = {
            "height": 12,
            "width": 50,
            "font": ("Arial", 10, "bold"),
            "selectmode": "tk.SINGLE",
        }
        self.listbox_grid = {
            "row": 1,
            "column": 0,
            "columnspan": 2,
            "padx": 10,
            "pady": 10,
        }
        self.listbox_button = {
            "row": 0,
            "column": 0,
            "padx": 5,
            "pady": 5,
            "sticky": "sw",
        }
        self.listbox_button_second = {
            "row": 0,
            "column": 1,
            "padx": 5,
            "pady": 5,
            "sticky": "ne",
        }
        # -- Combobox Settings -- #
        self.combo_style = {"state": "readonly", "font": ("Arial", 10, "bold")}
        self.combo_grid = {"row": 0, "column": 0, "padx": 5, "pady": 5, "sticky": "ew"}

    def get_default_products(self, language: str):
        if language == "ru":
            return {
                "Яблоки": 52,
                "Бананы": 89,
                "Груши": 57,
                "Апельсины": 43,
                "Клубника": 32,
                "Виноград": 69,
                "Малина": 39,
                "Черника": 57,
                "Абрикосы": 48,
                "Персики": 39,
                "Сливы": 46,
                "Киви": 61,
                "Манго": 60,
                "Арбуз": 30,
                "Дыня": 37,
                "Грейпфрут": 42,
                "Картофель (варёный)": 80,
                "Морковь": 41,
                "Огурцы": 15,
                "Помидоры": 20,
                "Капуста белокочанная": 30,
                "Брокколи": 34,
                "Цветная капуста": 25,
                "Шпинат": 20,
                "Лук репчатый": 40,
                "Чеснок": 150,
                "Сельдерей": 16,
                "Перец сладкий": 26,
                "Свекла": 43,
                "Салатный лист": 1,
                "Цукини": 17,
                "Тыква": 26,
                "Кабачки": 16,
                "Грибы (шампиньоны)": 22,
                "Гречка (варёная)": 110,
                "Рис (варёный)": 130,
                "Овсяная крупа": 374,
                "Макароны (варёные)": 130,
                "Перловая крупа": 342,
                "Манка": 340,
                "Булгур": 342,
                "Кукурузная крупа": 337,
                "Гречневая крупа": 306,
                "Чечевица": 310,
                "Фасоль белая": 102,
                "Фасоль красная": 93,
                "Фасоль чёрная": 132,
                "Зелёный горох": 280,
                "Соя": 395,
                "Нут": 364,
                "Киноа": 368,
                "Кускус": 376,
                "Овсяные хлопья": 350,
                "Кукурузные хлопья": 363,
                "Сахар": 400,
                "Мёд": 320,
                "Шоколад молочный": 550,
                "Шоколад горький": 542,
                "Печенье": 450,
                'Пирожное "Эклер"': 430,
                "Пряник": 380,
                "Мороженое": 207,
                "Зефир": 308,
                "Маршмеллоу": 318,
                "Карамель": 394,
                "Пончик": 350,
                "Пирог с яблоками": 250,
                "Сыр твёрдый": 350,
                "Сыр плавленый": 320,
                "Сырок": 380,
                "Творог 18%": 226,
                "Сметана 20%": 210,
                "Сливки 20%": 300,
                "Йогурт": 51,
                "Кефир 1%": 38,
                "Кефир 0%": 30,
                "Молоко 3,2%": 60,
                "Молоко 2,5%": 60,
                "Обезжиренный творог": 80,
                "Простокваша": 59,
                "Ацидофильное молоко": 58,
                "Ряженка": 85,
                "Куриное яйцо": 150,
                "Перепелиное яйцо": 168,
                "Куриная грудка (варёная)": 170,
                "Говядина (нежирная)": 150,
                "Свинина (нежирная)": 242,
                "Гусь": 300,
                "Утка": 348,
                "Индейка": 192,
                "Кролик": 197,
                "Говяжья печень": 100,
                "Говяжье сердце": 89,
                "Говяжий язык": 160,
                "Курица (без кожи)": 110,
                "Лосось (запечённый)": 200,
                "Треска (варёная)": 100,
                "Креветки (варёные)": 100,
                "Салака": 98,
                "Окунь": 95,
                "Камбала": 88,
                "Кальмар": 75,
                "Минтай": 70,
                "Крабы": 70,
                "Треска": 59,
                "Атлантическая сельдь": 57,
                "Лещь": 48,
                "Карп": 46,
                "Судак": 43,
                "Щука": 41,
                "Морская капуста": 16,
                "Протеиновый батончик (шоколадный)": 250,
                "Протеиновый батончик (ванильный)": 230,
                "Орехи (миндаль)": 576,
                "Орехи (грецкие)": 654,
                "Орехи (кешью)": 553,
                "Фундук": 628,
                "Арахис": 567,
                "Семена подсолнечника": 570,
                "Чиа (семена)": 486,
                "Тыквенные семечки": 446,
                "Фисташки": 560,
                "Миндальное молоко": 13,
                "Кокосовое молоко": 230,
                "Рикотта": 174,
                "Спирулина (порошок)": 290,
            }
        elif language == "en":
            return {
                "Apples": 52,
                "Bananas": 89,
                "Pears": 57,
                "Oranges": 43,
                "Strawberries": 32,
                "Grapes": 69,
                "Raspberries": 39,
                "Blueberries": 57,
                "Apricots": 48,
                "Peaches": 39,
                "Plums": 46,
                "Kiwis": 61,
                "Mangoes": 60,
                "Watermelon": 30,
                "Melon": 37,
                "Grapefruit": 42,
                "Boiled Potatoes": 80,
                "Carrots": 41,
                "Cucumbers": 15,
                "Tomatoes": 20,
                "White Cabbage": 30,
                "Broccoli": 34,
                "Cauliflower": 25,
                "Spinach": 20,
                "Onions": 40,
                "Garlic": 150,
                "Celery": 16,
                "Bell Peppers": 26,
                "Beetroot": 43,
                "Lettuce": 1,
                "Zucchini": 17,
                "Pumpkin": 26,
                "Squash": 16,
                "Mushrooms (Champignons)": 22,
                "Buckwheat (boiled)": 110,
                "Rice (boiled)": 130,
                "Oatmeal": 374,
                "Pasta (boiled)": 130,
                "Pearl Barley": 342,
                "Semolina": 340,
                "Bulgur": 342,
                "Cornmeal": 337,
                "Buckwheat Groats": 306,
                "Lentils": 310,
                "White Beans": 102,
                "Red Beans": 93,
                "Black Beans": 132,
                "Green Peas": 280,
                "Soy": 395,
                "Chickpeas": 364,
                "Quinoa": 368,
                "Couscous": 376,
                "Oats": 350,
                "Cornflakes": 363,
                "Sugar": 400,
                "Honey": 320,
                "Milk Chocolate": 550,
                "Dark Chocolate": 542,
                "Cookies": 450,
                "Eclair Pastry": 430,
                "Gingerbread": 380,
                "Ice Cream": 207,
                "Marshmallows": 318,
                "Caramel": 394,
                "Donuts": 350,
                "Apple Pie": 250,
                "Hard Cheese": 350,
                "Processed Cheese": 320,
                "Cheese Bar": 380,
                "Cottage Cheese 18%": 226,
                "Sour Cream 20%": 210,
                "Cream 20%": 300,
                "Yogurt": 51,
                "Kefir 1%": 38,
                "Kefir 0%": 30,
                "Milk 3.2%": 60,
                "Milk 2.5%": 60,
                "Low-fat Cottage Cheese": 80,
                "Prostokvasha": 59,
                "Acidophilus Milk": 58,
                "Ryazhenka": 85,
                "Chicken Egg": 150,
                "Quail Egg": 168,
                "Boiled Chicken Breast": 170,
                "Lean Beef": 150,
                "Lean Pork": 242,
                "Goose": 300,
                "Duck": 348,
                "Turkey": 192,
                "Rabbit": 197,
                "Beef Liver": 100,
                "Beef Heart": 89,
                "Beef Tongue": 160,
                "Chicken (skinless)": 110,
                "Baked Salmon": 200,
                "Boiled Cod": 100,
                "Boiled Shrimp": 100,
                "Sarak": 98,
                "Perch": 95,
                "Flounder": 88,
                "Squid": 75,
                "Pollock": 70,
                "Crabs": 70,
                "Cod": 59,
                "Atlantic Herring": 57,
                "Roach": 48,
                "Carp": 46,
                "Pikeperch": 43,
                "Pike": 41,
                "Seaweed": 16,
                "Chocolate Protein Bar": 250,
                "Vanilla Protein Bar": 230,
                "Almonds": 576,
                "Walnuts": 654,
                "Cashews": 553,
                "Hazelnuts": 628,
                "Peanuts": 567,
                "Sunflower Seeds": 570,
                "Chia Seeds": 486,
                "Pumpkin Seeds": 446,
                "Pistachios": 560,
                "Almond Milk": 13,
                "Coconut Milk": 230,
                "Ricotta": 174,
                "Spirulina Powder": 290,
            }
        else:
            error_message = "Ошибка Не существующий язык."
            self.log(error_message)
            self.error_message(_("Ошибка"), _("Не существующий язык."))
            return None

    def ensure_file_with_defaults(
        self,
        language: str,
        default_data_func: Callable[[], dict[str, Any]] | None = None,
    ):
        supported_languages = {
            "ru": self.PRODUCTS_LIST_RU,
            "en": self.PRODUCTS_LIST_EN,
        }

        if language not in supported_languages:
            error_title = _("Ошибка")
            error_message = _("Не существующий язык.")
            self.log(error_message)
            self.error_message(error_title, error_message)
            raise ValueError(f"Не существующий язык: {language}")

        default_data_func = default_data_func or (
            lambda: self.get_default_products(language)
        )
        file_path = supported_languages.get(language)

        def write_default(data: dict[str, Any]):
            try:
                print(f"Текущая рабочая директория: {os.getcwd()}")
                print(f"Путь к файлу перед записью: {file_path}")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Путь к файлу после записи: {file_path}")
                info_title = _("Успех")
                info_message = _(f"Файл {file_path} создан с дефолтными значениями.")
                self.info_message(info_title, info_message)
            except OSError as e:
                self.log(f"Ошибка записи файла {file_path}: {e}")
                self.error_message(
                    _("Ошибка"), _("Не удалось записать {f}.").format(f=file_path)
                )
            return data

        if not os.path.exists(file_path):
            return write_default(default_data_func())

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return write_default(default_data_func())
                return json.loads(content)
        except (OSError, json.JSONDecodeError) as e:
            self.log(f"Ошибка чтения файла {file_path}: {e}")
            self.error_message(
                _("Ошибка"),
                _("Ошибка чтения {f}. Загружаем дефолтные данные").format(f=file_path),
            )
            return write_default(default_data_func())
