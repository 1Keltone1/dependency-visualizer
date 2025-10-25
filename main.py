#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов
Минимальный прототип с конфигурацией - Этап 1
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli import CommandLineInterface
from config import Config
from errors import DependencyVisualizerError, ValidationError, ConfigError


class DependencyVisualizer:
    def __init__(self):
        self.cli = CommandLineInterface()
        self.config = None

    def run(self):
        """Основной метод запуска приложения"""
        try:
            print("=== Инструмент визуализации графа зависимостей ===")
            print("Загрузка конфигурации...")

            # Парсинг аргументов командной строки
            self.config = self.cli.parse_arguments()

            # Вывод всех параметров в формате ключ-значение
            print("\n" + "=" * 50)
            print("ТЕКУЩАЯ КОНФИГУРАЦИЯ:")
            print("=" * 50)
            self._print_configuration()
            print("=" * 50)

            # Демонстрация работы приложения
            self._demonstrate_workflow()

            print("\nПриложение успешно завершило работу!")

        except DependencyVisualizerError as e:
            print(f"\n❌ Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nПрервано пользователем", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)

    def _print_configuration(self):
        """Вывод конфигурации в формате ключ-значение"""
        config_dict = {
            "Имя анализируемого пакета": self.config.package_name,
            "URL репозитория/путь к файлу": self.config.repository_url,
            "Режим тестового репозитория": "Включен" if self.config.test_repo_mode else "Отключен",
            "Версия пакета": self.config.package_version or "Не указана",
            "Имя файла с изображением": self.config.output_filename,
            "Подстрока для фильтрации": self.config.filter_substring or "Не указана"
        }

        for key, value in config_dict.items():
            print(f"{key}: {value}")

    def _demonstrate_workflow(self):
        """Демонстрация рабочего процесса"""
        print("\n🔧 Демонстрация рабочего процесса:")

        # Симуляция анализа зависимостей
        print(f"1. Анализ пакета '{self.config.package_name}'...")

        if self.config.test_repo_mode:
            print("2. Работа в режиме тестового репозитория...")
        else:
            print("2. Работа с основным репозиторием...")

        if self.config.package_version:
            print(f"3. Используется версия: {self.config.package_version}")

        if self.config.filter_substring:
            print(f"4. Применен фильтр: '{self.config.filter_substring}'")

        print(f"5. Подготовка к генерации файла: {self.config.output_filename}")
        print("6. [Здесь будет построение графа зависимостей]")


def main():
    """Точка входа в приложение"""
    app = DependencyVisualizer()
    app.run()


if __name__ == "__main__":
    main()