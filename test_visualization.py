#!/usr/bin/env python3
"""
Тестирование визуализации на разных графах
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import NPMDataCollector
from graph_builder import DependencyGraphBuilder
from simple_visualizer import SimpleGraphVisualizer


def test_simple_graph():
    """Тест с простым графом"""
    print(" ТЕСТ 1: Простой граф")
    print("=" * 40)

    visualizer = SimpleGraphVisualizer()

    test_graph = {
        "A": {"B": "1.0", "C": "2.0"},
        "B": {"D": "1.0"},
        "C": {"D": "1.0", "E": "3.0"},
        "D": {},
        "E": {}
    }

    try:
        visualizer.generate_svg(test_graph, "test_simple.svg", "Простой тестовый граф")
        print(" SVG создан: test_simple.svg")
    except Exception as e:
        print(f" Ошибка SVG: {e}")

    visualizer.save_text_diagram(test_graph, "test_simple.txt", "Простой тестовый граф")
    print(" Текстовая диаграмма: test_simple.txt")


def test_test_repository():
    """Тест с тестовым репозиторием"""
    print("\n ТЕСТ 2: Тестовый репозиторий")
    print("=" * 40)

    try:
        collector = NPMDataCollector("test_graph.json", test_mode=True)
        builder = DependencyGraphBuilder(collector)
        visualizer = SimpleGraphVisualizer()

        graph = builder.build_dependency_graph("A", max_depth=2)
        print(f" Размер графа: {len(graph)} узлов")

        visualizer.save_text_diagram(graph, "test_repo.txt", "Тестовый репозиторий - пакет A")
        print(" Текстовая диаграмма: test_repo.txt")

        if len(graph) <= 20:
            visualizer.generate_svg(graph, "test_repo.svg", "Тестовый репозиторий - пакет A")
            print(" SVG создан: test_repo.svg")
        else:
            print(" Граф слишком большой для SVG визуализации")

    except Exception as e:
        print(f" Ошибка: {e}")


def test_real_package_simple():
    """Тест с реальным пакетом (упрощенный)"""
    print("\n ТЕСТ 3: Реальный пакет (React)")
    print("=" * 40)

    try:
        collector = NPMDataCollector("https://registry.npmjs.org")
        builder = DependencyGraphBuilder(collector)
        visualizer = SimpleGraphVisualizer()

        graph = builder.build_dependency_graph("react", "18.2.0", max_depth=1)
        print(f" Размер графа: {len(graph)} узлов")

        visualizer.save_text_diagram(graph, "react_simple.txt", "React зависимости (упрощенно)")
        print(" Текстовая диаграмма: react_simple.txt")

        if len(graph) <= 20:
            visualizer.generate_svg(graph, "react_simple.svg", "React зависимости")
            print(" SVG создан: react_simple.svg")
        else:
            print(" Граф слишком большой для SVG визуализации")

    except Exception as e:
        print(f" Ошибка: {e}")


def main():
    """Запуск всех тестов"""
    print(" ТЕСТИРОВАНИЕ ВИЗУАЛИЗАЦИИ ГРАФОВ")
    print("=" * 50)

    test_simple_graph()
    test_test_repository()
    test_real_package_simple()

    print("\n" + "=" * 50)
    print(" ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print(" Проверьте созданные файлы в текущей директории")


if __name__ == "__main__":
    main()