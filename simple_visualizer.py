import os
import math
from collections import deque


class SimpleGraphVisualizer:
    def generate_svg(self, graph, output_filename, title="Граф зависимостей"):
        try:
            simplified = self._simplify_graph(graph)
            layout = self._create_layout(simplified)
            svg_content = self._generate_svg_content(simplified, layout, title)

            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)

            return output_filename
        except Exception as e:
            raise Exception(f"Ошибка создания SVG: {e}")

    def save_plantuml_code(self, graph, filename, title="Граф зависимостей"):
        try:
            code = self._generate_plantuml_code(graph, title)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            return filename
        except Exception as e:
            raise Exception(f"Ошибка создания PlantUML: {e}")

    def save_text_diagram(self, graph, filename, title="Граф зависимостей"):
        try:
            text = self._generate_text_diagram(graph, title)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)
            return filename
        except Exception as e:
            raise Exception(f"Ошибка создания текста: {e}")

    def _simplify_graph(self, graph, max_nodes=15):
        simplified = {}
        for i, (node, deps) in enumerate(graph.items()):
            if i >= max_nodes:
                break
            simplified[node] = {k: v for j, (k, v) in enumerate(deps.items()) if j < 5 and "ERROR" not in k}
        return simplified

    def _create_layout(self, graph):
        layout = {}
        if not graph:
            return layout

        root = next(iter(graph.keys()))
        levels = {root: 0}
        queue = deque([root])

        while queue:
            node = queue.popleft()
            if node in graph:
                for child in graph[node]:
                    if child not in levels:
                        levels[child] = levels[node] + 1
                        queue.append(child)

        for level in set(levels.values()):
            level_nodes = [n for n, l in levels.items() if l == level]
            for i, node in enumerate(level_nodes):
                x = 100 + i * 200
                y = 100 + level * 120
                layout[node] = (x, y)

        return layout

    def _generate_svg_content(self, graph, layout, title):
        width, height = 800, 600
        if layout:
            max_x = max(x for x, y in layout.values()) + 150
            max_y = max(y for x, y in layout.values()) + 150
            width, height = max(800, max_x), max(600, max_y)

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '  .node { fill: #e3f2fd; stroke: #1565c0; stroke-width: 2; rx: 5; }',
            '  .node-text { font-family: Arial; font-size: 12px; fill: #0d47a1; }',
            '  .edge { stroke: #666; stroke-width: 2; fill: none; }',
            '  .title { font-family: Arial; font-size: 16px; fill: #333; }',
            '</style>',
            f'<text x="20" y="30" class="title">{title}</text>',
        ]

        for source, deps in graph.items():
            if source in layout:
                for target in deps:
                    if target in layout:
                        lines.extend(self._create_arrow(layout[source], layout[target]))

        for node, (x, y) in layout.items():
            name = node.split('@')[0] if '@' in node else node
            lines.append(f'<rect x="{x - 40}" y="{y - 15}" width="80" height="30" class="node"/>')
            lines.append(f'<text x="{x}" y="{y + 5}" class="node-text" text-anchor="middle">{name}</text>')

        lines.append('</svg>')
        return '\n'.join(lines)

    def _create_arrow(self, start, end):
        x1, y1 = start
        x2, y2 = end

        dx, dy = x2 - x1, y2 - y1
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return []

        dx, dy = dx / length * 30, dy / length * 30
        x1, y1 = x1 + dx, y1 + dy
        x2, y2 = x2 - dx, y2 - dy

        return [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>']

    def _generate_plantuml_code(self, graph, title):
        lines = ["@startuml", f"title {title}", "skinparam monochrome true", ""]

        nodes = set()
        for package, deps in graph.items():
            nodes.add(package)
            nodes.update(deps.keys())

        for node in nodes:
            if "ERROR" not in node:
                name = node.split('@')[0] if '@' in node else node
                lines.append(f'rectangle "{name}"')

        lines.append("")

        for package, deps in graph.items():
            for dep, version in deps.items():
                if "ERROR" not in dep:
                    p_name = package.split('@')[0] if '@' in package else package
                    d_name = dep.split('@')[0] if '@' in dep else dep
                    lines.append(f'"{p_name}" --> "{d_name}"')

        lines.extend(["", "@enduml"])
        return "\n".join(lines)

    def _generate_text_diagram(self, graph, title):
        lines = [f"=== {title} ===", ""]

        for i, (package, deps) in enumerate(graph.items()):
            if i >= 10:
                lines.append(f"... и еще {len(graph) - 10} пакетов")
                break

            p_name = package.split('@')[0] if '@' in package else package
            lines.append(f" {p_name}")

            if deps and "ERROR" not in next(iter(deps.keys()), ""):
                for j, (dep, version) in enumerate(deps.items()):
                    if j >= 5:
                        lines.append(f"    └── ... и еще {len(deps) - 5} зависимостей")
                        break
                    d_name = dep.split('@')[0] if '@' in dep else dep
                    lines.append(f"    └── {d_name}: {version}")
            elif "ERROR" in deps:
                lines.append(f"    └──  {deps['ERROR']}")
            else:
                lines.append("    └── (нет зависимостей)")
            lines.append("")

        lines.append(f"Всего пакетов: {len(graph)}")
        return "\n".join(lines)
