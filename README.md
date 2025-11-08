Инструмент для визуализации графов зависимостей npm пакетов. Собирает информацию о зависимостях, строит граф и создает визуализации в различных форматах.
# Возможности

- **Анализ зависимостей** - сбор информации о прямых и транзитивных зависимостях
- **Визуализация** - генерация SVG, PlantUML кода и текстовых диаграмм
- **Обратные зависимости** - поиск пакетов, зависящих от целевого пакета
- **Гибкая настройка** - фильтрация, ограничение глубины, тестовый режим
- **Без зависимостей** - использует только стандартную библиотеку Python

#  Базовые команды
## Анализ реального пакета
python main.py --package react --repo-url https://registry.npmjs.org --output graph.svg

## Тестовый режим (без интернета)
python main.py --package A --repo-url test_graph.json --test-mode --output test.puml

## С ограничением глубины
python main.py --package express --repo-url https://registry.npmjs.org --output deps.txt --max-depth 2

## Обратные зависимости
python main.py --package chalk --repo-url https://registry.npmjs.org --reverse-deps --root-package express --output reverse.txt

## С фильтрацией
python main.py --package webpack --repo-url https://registry.npmjs.org --filter "loader" --output filtered.puml

# Тестирование
## Быстрый тест на тестовых данных
python main.py --package A --repo-url test_graph.json --test-mode --output test.puml

## Проверка реального пакета
python main.py --package react --repo-url https://registry.npmjs.org --output react.svg --max-depth 1

## Демонстрация обратных зависимостей
python main.py --package D --repo-url test_graph.json --test-mode --reverse-deps --root-package A --output reverse.txt
