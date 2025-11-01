#!/usr/bin/env python3
"""
Демонстрационные примеры визуализации для этапа 5
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import NPMDataCollector
from graph_builder import DependencyGraphBuilder
from visualizer import GraphVisualizer


def demo_react():
    """Демонстрация для пакета React"""
    print(" Демонстрация 1: Пакет React")
    print("=" * 50)

    collector = NPMDataCollector("https://registry.npmjs.org")
    builder = DependencyGraphBuilder(collector)
    visualizer = GraphVisualizer()

    try:
        graph = builder.build_dependency_graph("react", "18.2.0", max_depth=3)
        visualizer.generate_svg(graph, "react_dependencies.svg", "Зависимости React 18.2.0")
        print(" Граф React создан: react_dependencies.svg")
    except Exception as e:
        print(f" Ошибка: {e}")


def demo_express():
    """Демонстрация для пакета Express"""
    print("\n Демонстрация 2: Пакет Express")
    print("=" * 50)

    collector = NPMDataCollector("https://registry.npmjs.org")
    builder = DependencyGraphBuilder(collector)
    visualizer = GraphVisualizer()

    try:
        graph = builder.build_dependency_graph("express", "4.18.0", max_depth=2)
        visualizer.generate_svg(graph, "express_dependencies.svg", "Зависимости Express 4.18.0")
        print(" Граф Express создан: express_dependencies.svg")
    except Exception as e:
        print(f" Ошибка: {e}")


def demo_lodash():
    """Демонстрация для пакета Lodash"""
    print("\n Демонстрация 3: Пакет Lodash")
    print("=" * 50)

    collector = NPMDataCollector("https://registry.npmjs.org")
    builder = DependencyGraphBuilder(collector)
    visualizer = GraphVisualizer()

    try:
        graph = builder.build_dependency_graph("lodash", "4.17.21", max_depth=2)
        visualizer.generate_svg(graph, "lodash_dependencies.svg", "Зависимости Lodash 4.17.21")
        print(" Граф Lodash создан: lodash_dependencies.svg")
    except Exception as e:
        print(f" Ошибка: {e}")


def demo_test_repository():
    """Демонстрация для тестового репозитория"""
    print("\n Демонстрация 4: Тестовый репозиторий")
    print("=" * 50)

    collector = NPMDataCollector("test_graph.json", test_mode=True)
    builder = DependencyGraphBuilder(collector)
    visualizer = GraphVisualizer()

    try:
        graph = builder.build_dependency_graph("A", max_depth=4)
        visualizer.generate_svg(graph, "test_graph_dependencies.svg", "Тестовый граф зависимостей")
        print(" Тестовый граф создан: test_graph_dependencies.svg")
    except Exception as e:
        print(f" Ошибка: {e}")


if __name__ == "__main__":
    print(" ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИИ ГРАФОВ ЗАВИСИМОСТЕЙ")
    print("Этап 5: Визуализация\n")

    demo_react()
    demo_express()
    demo_lodash()
    demo_test_repository()

    print("\n Все демонстрации завершены!")
    print(" Файлы SVG сохранены в текущей директории")