#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов
Этап 3: Основные операции с графом
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli import CommandLineInterface
from config import Config
from data_collector import NPMDataCollector
from graph_builder import DependencyGraphBuilder
from errors import (DependencyVisualizerError, ValidationError, ConfigError,
                    PackageNotFoundError, NetworkError, PackageDataError, CyclicDependencyError)


class DependencyVisualizer:
    def __init__(self):
        self.cli = CommandLineInterface()
        self.config = None
        self.data_collector = None
        self.graph_builder = None

    def run(self):
        """Основной метод запуска приложения"""
        try:
            print("=== Инструмент визуализации графа зависимостей ===")
            print("Этап 3: Основные операции с графом")
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
            self.data_collector = NPMDataCollector(
                self.config.repository_url,
                self.config.test_repo_mode
            )

            # Построение графа зависимостей
            dependency_graph = self._build_dependency_graph()

            # Вывод результатов
            self._display_graph_results(dependency_graph)

            print("\n Этап 3 завершен успешно!")

        except (PackageNotFoundError, PackageDataError, NetworkError, CyclicDependencyError) as e:
            print(f"\n Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
        except DependencyVisualizerError as e:
            print(f"\n Ошибка приложения: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nПрервано пользователем", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)

    def _print_configuration(self):
        """Вывод конфигурации в формате ключ-значение"""
        repo_type = "Тестовый репозиторий" if self.config.test_repo_mode else "NPM репозиторий"

        config_dict = {
            "Имя анализируемого пакета": self.config.package_name,
            "Тип репозитория": repo_type,
            "URL репозитория/путь к файлу": self.config.repository_url,
            "Версия пакета": self.config.package_version or "Не указана (будет использована последняя)",
            "Имя файла с изображением": self.config.output_filename,
            "Подстрока для фильтрации": self.config.filter_substring or "Не указана"
        }

        for key, value in config_dict.items():
            print(f"{key}: {value}")

    def _build_dependency_graph(self):
        """Строит граф зависимостей"""
        print(f"\n Построение графа зависимостей для пакета '{self.config.package_name}'...")

        # Инициализация построителя графа
        self.graph_builder = DependencyGraphBuilder(self.data_collector)

        # Построение графа
        graph = self.graph_builder.build_dependency_graph(
            root_package=self.config.package_name,
            root_version=self.config.package_version,
            filter_substring=self.config.filter_substring,
            max_depth=10
        )

        return graph

    def _display_graph_results(self, graph):
        """Отображает результаты построения графа"""
        if not graph:
            print(f"\n Граф зависимостей пуст для пакета '{self.config.package_name}'")
            return

        # Статистика графа
        stats = self.graph_builder.get_graph_statistics()

        print(f"\n ГРАФ ЗАВИСИМОСТЕЙ ПАКЕТА '{self.config.package_name}':")
        print("=" * 70)

        # Вывод графа в читаемом формате
        for package, dependencies in graph.items():
            print(f"\n {package}:")
            if dependencies and "ERROR" not in dependencies:
                for dep, version in dependencies.items():
                    print(f"   └── {dep}: {version}")
            elif "ERROR" in dependencies:
                print(f"   └── Ошибка: {dependencies['ERROR']}")
            else:
                print("   └── (нет зависимостей)")

        print("\n" + "=" * 70)
        print("СТАТИСТИКА ГРАФА:")
        print(f"   Всего пакетов: {stats['total_packages']}")
        print(f"   Всего зависимостей: {stats['total_dependencies']}")
        print(f"   Максимальная глубина: {stats['max_depth']}")
        print(f"   Обнаружены циклы: {'Да' if stats['has_cycles'] else 'Нет'}")


def main():
    """Точка входа в приложение"""
    app = DependencyVisualizer()
    app.run()


if __name__ == "__main__":
    main()