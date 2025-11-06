#!/usr/bin/env python3
"""
Демонстрация простой визуализации
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_visualizer import SimpleGraphVisualizer


def demo_simple_visualization():
    """Демонстрация работы визуализатора"""
    print(" ДЕМОНСТРАЦИЯ ВИЗУАЛИЗАЦИИ")
    print("=" * 40)

    visualizer = SimpleGraphVisualizer()

    # Простой тестовый граф
    test_graph = {
        "React": {"loose-envify": "^1.0.0", "js-tokens": "^4.0.0"},
        "loose-envify": {"js-tokens": "^3.0.0"},
        "js-tokens": {}
    }

    # SVG визуализация
    try:
        visualizer.generate_svg(test_graph, "demo_graph.svg", "Демонстрационный граф")
        print(" Демо SVG создан: demo_graph.svg")
    except Exception as e:
        print(f" Ошибка SVG: {e}")

    # Текстовая визуализация
    visualizer.save_text_diagram(test_graph, "demo_graph.txt", "Демонстрационный граф")
    print(" Демо текстовая диаграмма: demo_graph.txt")

    print("\n Текстовая диаграмма:")
    print(visualizer.generate_text_diagram(test_graph))


if __name__ == "__main__":
    demo_simple_visualization()