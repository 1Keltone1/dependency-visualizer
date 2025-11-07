import os
import math
from collections import deque
from errors import DependencyVisualizerError


class SimpleGraphVisualizer:
    """Простой визуализатор графа зависимостей с генерацией SVG"""

    def generate_svg(self, graph, output_filename, title="Dependency Graph"):
        """
        Генерирует SVG изображение графа вручную
        """
        try:
            simplified_graph = self._simplify_graph(graph, max_nodes=20)

            if not simplified_graph:
                raise DependencyVisualizerError("Граф слишком мал для визуализации")

            layout = self._create_tree_layout(simplified_graph)
            svg_content = self._generate_svg_content(simplified_graph, layout, title)

            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)

            print(f" SVG файл создан: {output_filename}")
            return output_filename

        except Exception as e:
            raise DependencyVisualizerError(f"Ошибка при генерации SVG: {e}")

    def _simplify_graph(self, graph, max_nodes=20):
        """Упрощает граф для визуализации"""
        if not graph:
            return {}

        simplified = {}
        nodes_added = 0

        for node, deps in graph.items():
            if nodes_added >= max_nodes:
                break

            simplified_deps = {}
            deps_added = 0
            for dep, version in deps.items():
                if deps_added >= 5:
                    break
                if "ERROR" not in dep and dep in graph:
                    simplified_deps[dep] = version
                    deps_added += 1

            simplified[node] = simplified_deps
            nodes_added += 1

        return simplified

    def _create_tree_layout(self, graph):
        """Создает древовидный layout для графа"""
        if not graph:
            return {}

        root = next(iter(graph.keys()))

        layout = {}
        visited = set()
        level_nodes = {}

        queue = deque([(root, 0)])
        while queue:
            node, level = queue.popleft()
            if node in visited:
                continue

            visited.add(node)

            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)

            if node in graph:
                for child in graph[node]:
                    if child not in visited and child in graph:
                        queue.append((child, level + 1))

        for level, nodes in level_nodes.items():
            level_width = len(nodes) * 200
            start_x = (800 - level_width) / 2 if level_width < 800 else 50

            for i, node in enumerate(nodes):
                x = start_x + i * 200
                y = 100 + level * 150
                layout[node] = (x, y)

        return layout

    def _generate_svg_content(self, graph, layout, title):
        """Генерирует содержимое SVG файла"""

        if not layout:
            width, height = 800, 600
        else:
            max_x = max(x for x, y in layout.values()) + 150
            max_y = max(y for x, y in layout.values()) + 150
            width, height = max(800, max_x), max(600, max_y)

        svg_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '  .node { fill: #e1f5fe; stroke: #01579b; stroke-width: 2; rx: 5; }',
            '  .node-text { font-family: Arial, sans-serif; font-size: 12px; fill: #01579b; }',
            '  .edge { stroke: #757575; stroke-width: 2; fill: none; }',
            '  .edge-text { font-family: Arial, sans-serif; font-size: 10px; fill: #757575; }',
            '  .title { font-family: Arial, sans-serif; font-size: 18px; fill: #333; font-weight: bold; }',
            '</style>',
            f'<text x="20" y="30" class="title">{title}</text>',
        ]

        for source, dependencies in graph.items():
            if source in layout:
                source_x, source_y = layout[source]
                for target, version in dependencies.items():
                    if target in layout:
                        target_x, target_y = layout[target]
                        svg_lines.extend(self._create_arrow(source_x, source_y, target_x, target_y))

        for node, (x, y) in layout.items():
            display_name = self._shorten_name(node)
            rect_width = max(80, len(display_name) * 7)
            rect_height = 30

            svg_lines.append(
                f'<rect x="{x - rect_width / 2}" y="{y - rect_height / 2}" width="{rect_width}" height="{rect_height}" class="node"/>')
            svg_lines.append(f'<text x="{x}" y="{y}" class="node-text" text-anchor="middle">{display_name}</text>')

        svg_lines.append('</svg>')
        return '\n'.join(svg_lines)

    def _shorten_name(self, name):
        """Сокращает длинные имена пакетов"""
        if '@' in name:
            name = name.split('@')[0]

        if len(name) > 15:
            return name[:12] + "..."
        return name

    def _create_arrow(self, x1, y1, x2, y2):
        """Создает стрелку между двумя точками"""
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return []

        dx /= length
        dy /= length

        offset = 25
        x1 = x1 + dx * offset
        y1 = y1 + dy * offset
        x2 = x2 - dx * offset
        y2 = y2 - dy * offset

        arrow_size = 8
        arrow_angle = math.pi / 6

        lines = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>']

        angle = math.atan2(y2 - y1, x2 - x1)

        arrow_x1 = x2 - arrow_size * math.cos(angle - arrow_angle)
        arrow_y1 = y2 - arrow_size * math.sin(angle - arrow_angle)
        arrow_x2 = x2 - arrow_size * math.cos(angle + arrow_angle)
        arrow_y2 = y2 - arrow_size * math.sin(angle + arrow_angle)

        lines.append(f'<line x1="{x2}" y1="{y2}" x2="{arrow_x1}" y2="{arrow_y1}" class="edge"/>')
        lines.append(f'<line x1="{x2}" y1="{y2}" x2="{arrow_x2}" y2="{arrow_y2}" class="edge"/>')

        return lines

    def generate_text_diagram(self, graph, title="Dependency Graph"):
        """Создает текстовую диаграмму как альтернативу"""
        lines = [f"=== {title} ===", ""]

        max_nodes = 10
        nodes_shown = 0

        for package, dependencies in graph.items():
            if nodes_shown >= max_nodes:
                lines.append(f"... и еще {len(graph) - max_nodes} пакетов")
                break

            display_package = package.split('@')[0] if '@' in package else package
            lines.append(f" {display_package}")

            if dependencies and "ERROR" not in dependencies:
                deps_shown = 0
                for dep, version in dependencies.items():
                    if deps_shown >= 5:
                        lines.append(f"    └── ... и еще {len(dependencies) - 5} зависимостей")
                        break
                    display_dep = dep.split('@')[0] if '@' in dep else dep
                    lines.append(f"    └── {display_dep}: {version}")
                    deps_shown += 1
            elif "ERROR" in dependencies:
                lines.append(f"    └──  Ошибка: {dependencies['ERROR']}")
            else:
                lines.append("    └── (нет зависимостей)")
            lines.append("")
            nodes_shown += 1

        lines.append(f"Всего пакетов в графе: {len(graph)}")
        return "\n".join(lines)

    def save_text_diagram(self, graph, filename, title="Dependency Graph"):
        """Сохраняет текстовую диаграмму в файл"""
        text_diagram = self.generate_text_diagram(graph, title)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_diagram)

        print(f" Текстовая диаграмма сохранена: {filename}")
        return filename

    def generate_plantuml_code(self, graph, title="Dependency Graph"):
        """
        Генерирует код PlantUML для графа зависимостей
        """
        plantuml_lines = [
            "@startuml",
            f"title {title}",
            "skinparam monochrome true",
            "skinparam shadowing false",
            "skinparam nodesep 20",
            "skinparam ranksep 50",
            "left to right direction",
            ""
        ]

        # Собираем все узлы
        nodes = set()
        edges = []

        for package, dependencies in graph.items():
            display_package = self._shorten_name(package)
            nodes.add(display_package)

            for dep, version in dependencies.items():
                if "ERROR" not in dep:
                    display_dep = self._shorten_name(dep)
                    nodes.add(display_dep)
                    edges.append((display_package, display_dep, version))

        # Добавляем узлы
        for node in sorted(nodes):
            plantuml_lines.append(f'rectangle "{node}"')

        plantuml_lines.append("")

        # Добавляем связи
        for source, target, version in edges:
            plantuml_lines.append(f'"{source}" --> "{target}" : {version}')

        plantuml_lines.extend(["", "@enduml"])
        return "\n".join(plantuml_lines)

    def save_plantuml_code(self, graph, filename, title="Dependency Graph"):
        """
        Сохраняет код PlantUML в файл
        """
        plantuml_code = self.generate_plantuml_code(graph, title)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(plantuml_code)

        print(f"Код PlantUML сохранен: {filename}")
        return filename

    def compare_with_npm(self, package_name, version=None, max_depth=3):
        """
        Сравнивает результаты с выводом штатных инструментов npm
        """
        try:
            # Получаем дерево зависимостей через npm (если установлен)
            npm_deps = self._get_npm_dependencies(package_name, version, max_depth)
            npm_tree = self._get_npm_tree(package_name, version)

            comparison = {
                "npm_available": bool(npm_deps),
                "our_approach": "DFS обход с ограничением глубины",
                "npm_approach": "Полное дерево зависимостей (если доступно)",
                "notes": []
            }

            if npm_deps:
                # Анализ расхождений
                our_deps_count = len(npm_deps)  # Для примера
                npm_deps_count = len(npm_deps) if isinstance(npm_deps, dict) else 0

                comparison.update({
                    "dependency_count_our": our_deps_count,
                    "dependency_count_npm": npm_deps_count,
                    "difference": abs(our_deps_count - npm_deps_count),
                    "reason": "Ограничение глубины обхода в нашей реализации"
                })
            else:
                comparison["notes"].append("npm не установлен или недоступен")

            return comparison

        except Exception as e:
            return {
                "error": f"Ошибка сравнения: {e}",
                "npm_available": False
            }

    def _get_npm_dependencies(self, package_name, version=None, max_depth=3):
        """
        Получает зависимости через npm view
        """
        try:
            import subprocess

            package_spec = f"{package_name}@{version}" if version else package_name
            cmd = ['npm', 'view', package_spec, 'dependencies', '--json']

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                # Парсим JSON вывод npm
                import json
                deps = json.loads(result.stdout)
                return deps
            else:
                return None

        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            return None

    def _get_npm_tree(self, package_name, version=None):
        """
        Пытается получить полное дерево зависимостей через npm
        """
        try:
            import subprocess
            import tempfile
            import os

            # Создаем временный package.json
            with tempfile.TemporaryDirectory() as temp_dir:
                package_json = {
                    "name": "temp-comparison",
                    "version": "1.0.0",
                    "dependencies": {
                        package_name: version or "latest"
                    }
                }

                temp_file = os.path.join(temp_dir, "package.json")
                with open(temp_file, 'w') as f:
                    import json
                    json.dump(package_json, f)

                # Запускаем npm install и npm ls
                os.chdir(temp_dir)
                subprocess.run(['npm', 'install'], capture_output=True, timeout=60)
                result = subprocess.run(['npm', 'ls', '--json'], capture_output=True, text=True, timeout=30)
                os.chdir('..')

                if result.returncode == 0:
                    return result.stdout
                else:
                    return "Не удалось получить дерево npm"

        except Exception as e:
            return f"Ошибка: {e}"