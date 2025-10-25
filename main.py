#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов
Этап 2: Сбор данных
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli import CommandLineInterface
from config import Config
from data_collector import NPMDataCollector
from errors import DependencyVisualizerError, ValidationError, ConfigError, PackageNotFoundError, NetworkError


class DependencyVisualizer:
    def __init__(self):
        self.cli = CommandLineInterface()
        self.config = None
        self.data_collector = None

    def run(self):
        """Основной метод запуска приложения"""
        try:
            print("=== Инструмент визуализации графа зависимостей ===")
            print("Этап 2: Сбор данных")
            print("Загрузка конфигурации...")

            # Парсинг аргументов командной строки
            self.config = self.cli.parse_arguments()

            # Вывод всех параметров в формате ключ-значение
            print("\n" + "=" * 50)
            print("ТЕКУЩАЯ КОНФИГУРАЦИЯ:")
            print("=" * 50)
            self._print_configuration()
            print("=" * 50)

            # Инициализация сборщика данных
            self.data_collector = NPMDataCollector(self.config.repository_url)

            # Получение и вывод зависимостей
            self._collect_and_display_dependencies()

            print("\n✅ Этап 2 завершен успешно!")

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
            "Версия пакета": self.config.package_version or "Не указана (будет использована последняя)",
            "Имя файла с изображением": self.config.output_filename,
            "Подстрока для фильтрации": self.config.filter_substring or "Не указана"
        }

        for key, value in config_dict.items():
            print(f"{key}: {value}")

    def _collect_and_display_dependencies(self):
        """Сбор и отображение зависимостей"""
        print(f"\n📦 Получение зависимостей для пакета '{self.config.package_name}'...")

        try:
            # Получаем зависимости
            dependencies = self.data_collector.get_package_dependencies(
                self.config.package_name,
                self.config.package_version
            )

            # Применяем фильтр если указан
            if self.config.filter_substring:
                dependencies = self.data_collector.filter_dependencies(
                    dependencies,
                    self.config.filter_substring
                )

            # Выводим результат
            self._display_dependencies(dependencies)

        except PackageNotFoundError:
            print(f"\n❌ Пакет '{self.config.package_name}' не найден в репозитории")
            raise
        except NetworkError as e:
            print(f"\n❌ Ошибка сети: {e}")
            raise
        except PackageDataError as e:
            print(f"\n❌ Ошибка данных пакета: {e}")
            raise

    def _display_dependencies(self, dependencies):
        """Отображает зависимости в читаемом формате"""
        if not dependencies:
            print(f"\n📭 Пакет '{self.config.package_name}' не имеет зависимостей")
            return

        print(f"\n🎯 ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА '{self.config.package_name}':")
        print("=" * 60)

        for i, (package, version) in enumerate(dependencies.items(), 1):
            print(f"{i:2d}. {package}: {version}")

        print("=" * 60)
        print(f"Всего зависимостей: {len(dependencies)}")

        # Дополнительная статистика
        if dependencies:
            unique_packages = set(dependencies.keys())
            print(f"Уникальных пакетов: {len(unique_packages)}")


def main():
    """Точка входа в приложение"""
    app = DependencyVisualizer()
    app.run()


if __name__ == "__main__":
    main()