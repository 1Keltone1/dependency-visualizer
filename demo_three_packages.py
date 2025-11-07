#!/usr/bin/env python3
"""
Демонстрация визуализации для трех различных пакетов
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import NPMDataCollector
from graph_builder import DependencyGraphBuilder
from simple_visualizer import SimpleGraphVisualizer


def demo_three_packages():
    """Демонстрация для трех различных пакетов"""

    visualizer = SimpleGraphVisualizer()
    packages = [
        ("react", "18.2.0", "React - популярная UI библиотека"),
        ("express", "4.18.0", "Express - веб-фреймворк для Node.js"),
        ("lodash", "4.17.21", "Lodash - утилиты для JavaScript")
    ]

    print(" ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИИ ДЛЯ ТРЕХ ПАКЕТОВ")
    print("=" * 60)

    for package_name, version, description in packages:
        print(f"\n Пакет: {package_name}@{version}")
        print(f" {description}")
        print("-" * 40)

        try:
            collector = NPMDataCollector("https://registry.npmjs.org")
            builder = DependencyGraphBuilder(collector)

            # Строим граф с ограниченной глубиной для демонстрации
            graph = builder.build_dependency_graph(package_name, version, max_depth=2)

            print(f" Размер графа: {len(graph)} узлов")

            # PlantUML
            plantuml_file = f"{package_name}_dependencies.puml"
            visualizer.save_plantuml_code(graph, plantuml_file, f"{package_name}@{version}")

            # SVG
            if len(graph) <= 15:
                svg_file = f"{package_name}_dependencies.svg"
                visualizer.generate_svg(graph, svg_file, f"{package_name}@{version}")
                print(f" SVG: {svg_file}")
            else:
                print(" Граф слишком большой для SVG")

            # Текстовая диаграмма
            txt_file = f"{package_name}_dependencies.txt"
            visualizer.save_text_diagram(graph, txt_file, f"{package_name}@{version}")
            print(f" Текстовая диаграмма: {txt_file}")

            # Сравнение с npm
            comparison = visualizer.compare_with_npm(package_name, version)
            if comparison.get("npm_available"):
                print(
                    f" Сравнение: {comparison.get('dependency_count_our', 'N/A')} vs {comparison.get('dependency_count_npm', 'N/A')} зависимостей")

        except Exception as e:
            print(f" Ошибка: {e}")
            continue

    print("\n" + "=" * 60)
    print(" ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print(" Файлы сохранены в текущей директории")


if __name__ == "__main__":
    demo_three_packages()