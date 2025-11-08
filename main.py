#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей для менеджера пакетов
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli import CommandLineInterface
from config import Config
from data_collector import NPMDataCollector
from graph_builder import DependencyGraphBuilder
from simple_visualizer import SimpleGraphVisualizer
from errors import DependencyVisualizerError


class DependencyVisualizer:
    def __init__(self):
        self.cli = CommandLineInterface()
        self.config = None

    def run(self):
        try:
            print("=== Инструмент визуализации графа зависимостей ===")

            self.config = self.cli.parse_arguments()

            print("\n" + "=" * 50)
            print("КОНФИГУРАЦИЯ:")
            print("=" * 50)
            self._print_configuration()
            print("=" * 50)

            collector = NPMDataCollector(self.config.repository_url, self.config.test_repo_mode)
            builder = DependencyGraphBuilder(collector)
            visualizer = SimpleGraphVisualizer()

            if self.config.reverse_dependencies:
                self._find_reverse_deps(builder, visualizer)
            else:
                graph = builder.build_dependency_graph(
                    self.config.package_name,
                    self.config.package_version,
                    self.config.filter_substring,
                    self.config.max_depth
                )
                self._display_graph(graph, builder)
                self._visualize_graph(graph, visualizer)

            print("\n✅ Готово!")

        except DependencyVisualizerError as e:
            print(f"\n❌ Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)

    def _print_configuration(self):
        config_dict = {
            "Пакет": self.config.package_name,
            "Репозиторий": self.config.repository_url,
            "Режим": "тестовый" if self.config.test_repo_mode else "npm",
            "Версия": self.config.package_version or "последняя",
            "Выходной файл": self.config.output_filename,
            "Фильтр": self.config.filter_substring or "нет",
            "Максимальная глубина": self.config.max_depth
        }

        if self.config.reverse_dependencies:
            config_dict["Режим"] = "обратные зависимости"
            config_dict["Корневой пакет"] = self.config.root_package

        for key, value in config_dict.items():
            print(f"{key}: {value}")

    def _find_reverse_deps(self, builder, visualizer):
        print(f"\n🔄 Поиск обратных зависимостей для '{self.config.package_name}'...")

        reverse_deps = builder.find_reverse_dependencies(
            self.config.package_name,
            self.config.root_package,
            self.config.package_version,
            self.config.filter_substring,
            self.config.max_depth
        )

        if not reverse_deps:
            print(f"📭 Не найдено пакетов, зависящих от '{self.config.package_name}'")
            return

        print(f"\n🔄 Пакеты, зависящие от '{self.config.package_name}':")
        print("=" * 50)
        for i, package in enumerate(sorted(reverse_deps), 1):
            print(f"{i:2d}. {package}")
        print(f"Всего: {len(reverse_deps)}")

    def _display_graph(self, graph, builder):
        if not graph:
            print(f"\n📭 Граф пуст")
            return

        stats = builder.get_graph_statistics(graph)

        print(f"\n📊 ГРАФ ЗАВИСИМОСТЕЙ:")
        print("=" * 60)

        packages_with_deps = 0
        packages_with_errors = 0

        for package, dependencies in graph.items():
            print(f"\n📦 {package}:")

            if dependencies and "ERROR" not in next(iter(dependencies.keys()), ""):
                packages_with_deps += 1
                for dep, version in dependencies.items():
                    print(f"   └── {dep}: {version}")
            elif dependencies and "ERROR" in dependencies:
                packages_with_errors += 1
                print(f"   └── ❌ {dependencies['ERROR']}")
            else:
                print("   └── (нет зависимостей)")

        print("\n" + "=" * 60)
        print(f"📈 Статистика: {stats['total_packages']} пакетов, "
              f"{stats['total_dependencies']} зависимостей")
        print(f"   📦 С зависимостями: {packages_with_deps}")
        print(f"   ❌ С ошибками: {packages_with_errors}")
        print(f"   📏 Глубина: {stats['max_depth']}")
        print(f"   🔄 Циклы: {'да' if stats['has_cycles'] else 'нет'}")

    def _visualize_graph(self, graph, visualizer):
        if not graph:
            return

        print(f"\n🎨 ВИЗУАЛИЗАЦИЯ...")

        if '.' in self.config.output_filename:
            base_name = os.path.splitext(self.config.output_filename)[0]
        else:
            base_name = self.config.output_filename

        title = f"Зависимости {self.config.package_name}"

        files_created = []

        # 1. PlantUML
        try:
            puml_file = f"{base_name}.puml"
            visualizer.save_plantuml_code(graph, puml_file, title)
            files_created.append(puml_file)
            print(f"✅ PlantUML: {puml_file}")
        except Exception as e:
            print(f"❌ Ошибка PlantUML: {e}")

        # 2. Текстовая диаграмма
        try:
            txt_file = f"{base_name}.txt"
            visualizer.save_text_diagram(graph, txt_file, title)
            files_created.append(txt_file)
            print(f"✅ Текст: {txt_file}")
        except Exception as e:
            print(f"❌ Ошибка текста: {e}")

        # 3. SVG изображение
        if len(graph) <= 20:
            try:
                svg_file = f"{base_name}.svg"
                visualizer.generate_svg(graph, svg_file, title)
                files_created.append(svg_file)
                print(f"✅ SVG: {svg_file}")
            except Exception as e:
                print(f"❌ Ошибка SVG: {e}")
        else:
            print(f"📊 Граф слишком большой для SVG ({len(graph)} узлов)")

        if files_created:
            print(f"\n📁 Создано файлов: {len(files_created)}")
            for file in files_created:
                print(f"   📄 {file}")


def main():
    DependencyVisualizer().run()


if __name__ == "__main__":
    main()