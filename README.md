# MealsCalculator

Приложение для расчёта питания и управления продуктами с поддержкой статистики и локализации.

## Возможности

- Управление продуктами и блюдами  
- Подсчёт и отображение статистики по питанию  
- Многоязыковая поддержка (gettext)  
- Юнит-тесты для основных модулей

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/PonyPaPony/MealsCalculator.git
   ```

2. Перейдите в папку проекта:

   ```bash
   cd MealsCalculator
   ```

3. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

4. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

## Запуск

Запустите основное приложение командой:

```bash
python src/main.py
```

## Тестирование

Для запуска тестов используйте:

```bash
pytest
```

## Локализация

В проекте используется gettext для поддержки нескольких языков.  
Файлы перевода расположены в папке `locales`.

## Структура проекта

- main.py — точка входа приложения
- src/ — исходный код приложения
- config/ — модули конфигурации
- data/products/ — данные о продуктах (пока пустая папка с .gitkeep)
- locales/ — файлы локализации (переводы)
- logs/ — модуль логирования
- resources/ — дополнительные ресурсы (например, иконки)
- tests/ — юнит-тесты
- .github/workflows/ — настройки CI/CD (GitHub Actions)
- Конфигурационные файлы: pyproject.toml, pytest.ini, requirements.txt

## Вклад

Если хотите помочь развитию проекта — создавайте issue или pull request.

---

Автор: PonyPaPony
