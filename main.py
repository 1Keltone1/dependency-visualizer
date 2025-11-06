#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов
Этап 5: Визуализация графа зависимостей
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli import CommandLineInterface
from config import Config
from data_collector import NPMDataCollector
from graph_builder import DependencyGraphBuilder
from simple_visualizer import SimpleGraphVisualizer
from errors import (DependencyVisualizerError, ValidationError, ConfigError,
                    PackageNotFoundError, NetworkError, PackageDataError, CyclicDependencyError)


class DependencyVisualizer:
    def __init__(self):
        self.cli = CommandLineInterface()
        self.config = None
        self.data_collector = None
        self.graph_builder = None
        self.visualizer = None

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

            # Инициализация компонентов
            self.data_collector = NPMDataCollector(
                self.config.repository_url,
                self.config.test_repo_mode
            )
            self.visualizer = SimpleGraphVisualizer()

            # Выполнение операций в зависимости от режима
            if self.config.reverse_dependencies:
                self._find_and_display_reverse_dependencies()
            else:
                # Стандартный режим - построение и визуализация графа
                dependency_graph = self._build_dependency_graph()
                self._display_graph_results(dependency_graph)
                self._visualize_graph(dependency_graph)

            print("\n Программа завершена успешно!")

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
        mode = "Обратные зависимости" if self.config.reverse_dependencies else "Прямые зависимости"

        config_dict = {
            "Режим работы": mode,
            "Имя анализируемого пакета": self.config.package_name,
            "Тип репозитория": repo_type,
            "URL репозитория/путь к файлу": self.config.repository_url,
            "Версия пакета": self.config.package_version or "Не указана (будет использована последняя)",
            "Имя файла с изображением": self.config.output_filename,
            "Подстрока для фильтрации": self.config.filter_substring or "Не указана"
        }

        if self.config.reverse_dependencies:
            config_dict["Корневой пакет для обхода"] = self.config.root_package

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

    def _find_and_display_reverse_dependencies(self):
        """Находит и отображает обратные зависимости"""
        print(f"\n Поиск обратных зависимостей для пакета '{self.config.package_name}'...")
        print(f" Начало обхода от корневого пакета '{self.config.root_package}'")

        # Инициализация построителя графа
        self.graph_builder = DependencyGraphBuilder(self.data_collector)

        # Поиск обратных зависимостей
        reverse_deps = self.graph_builder.find_reverse_dependencies(
            target_package=self.config.package_name,
            root_package=self.config.root_package,
            root_version=self.config.package_version,
            filter_substring=self.config.filter_substring,
            max_depth=10
        )

        # Отображение результатов
        self._display_reverse_dependencies(reverse_deps)

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
                print(f"   └──  Ошибка: {dependencies['ERROR']}")
            else:
                print("   └── (нет зависимостей)")

        print("\n" + "=" * 70)
        print(" СТАТИСТИКА ГРАФА:")
        print(f"   Всего пакетов: {stats['total_packages']}")
        print(f"   Всего зависимостей: {stats['total_dependencies']}")
        print(f"   Максимальная глубина: {stats['max_depth']}")
        print(f"   Обнаружены циклы: {'Да' if stats['has_cycles'] else 'Нет'}")

    def _display_reverse_dependencies(self, reverse_deps):
        """Отображает обратные зависимости"""
        if not reverse_deps:
            print(f"\n Не найдено пакетов, зависящих от '{self.config.package_name}'")
            return

        print(f"\n ПАКЕТЫ, ЗАВИСЯЩИЕ ОТ '{self.config.package_name}':")
        print("=" * 60)

        for i, package in enumerate(sorted(reverse_deps), 1):
            print(f"{i:2d}. {package}")

        print("=" * 60)
        print(f"Всего обратных зависимостей: {len(reverse_deps)}")

    def _visualize_graph(self, graph):
        """Визуализирует граф зависимостей"""
        if not graph:
            print(f"\n Невозможно визуализировать пустой граф")
            return

        print(f"\n ВИЗУАЛИЗАЦИЯ ГРАФА:")
        print("=" * 50)

        # Всегда создаем текстовую диаграмму
        text_file = self.config.output_filename.replace('.svg', '.txt')
        text_path = self.visualizer.save_text_diagram(
            graph,
            text_file,
            f"Зависимости пакета {self.config.package_name}"
        )
        print(f"Текстовая диаграмма сохранена: {text_path}")

        # Пытаемся создать SVG только для небольших графов
        if len(graph) <= 20:
            try:
                svg_path = self.visualizer.generate_svg(
                    graph,
                    self.config.output_filename,
                    f"Зависимости пакета {self.config.package_name}"
                )
                print(f"SVG изображение сохранено: {svg_path}")
            except Exception as e:
                print(f"Не удалось создать SVG: {e}")
                print("SVG создается только для графов до 20 узлов")
        else:
            print(f"Граф слишком большой для SVG ({len(graph)} узлов)")
            print("Просмотрите текстовую диаграмму для полной информации")


def main():
    """Точка входа в приложение"""
    app = DependencyVisualizer()
    app.run()


if __name__ == "__main__":
    main()