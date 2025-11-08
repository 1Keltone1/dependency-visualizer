from collections import deque
from errors import CyclicDependencyError


class DependencyGraphBuilder:
    def __init__(self, data_collector):
        self.data_collector = data_collector

    def build_dependency_graph(self, root_package, root_version=None, filter_substring=None, max_depth=3):
        if max_depth is None:
            max_depth = 3

        visited = set()
        graph = {}
        stack = [(root_package, root_version, 0)]

        print(f" Максимальная глубина обхода: {max_depth}")

        while stack:
            current_package, current_version, depth = stack.pop()

            if depth >= max_depth:
                continue

            package_key = f"{current_package}@{current_version}" if current_version else current_package

            if package_key in visited:
                continue

            visited.add(package_key)

            try:
                dependencies = self.data_collector.get_package_dependencies(current_package, current_version)

                if filter_substring:
                    dependencies = self.data_collector.filter_dependencies(dependencies, filter_substring)

                graph[package_key] = dependencies

                for dep_package, dep_version in dependencies.items():
                    if "ERROR" not in dep_package:
                        stack.append((dep_package, dep_version, depth + 1))

            except Exception as e:
                graph[package_key] = {"ERROR": str(e)}

        return graph

    def find_reverse_dependencies(self, target_package, root_package, root_version=None, filter_substring=None,
                                  max_depth=3):
        if max_depth is None:
            max_depth = 3

        graph = self.build_dependency_graph(root_package, root_version, filter_substring, max_depth)

        reverse_deps = []
        target_name = target_package.split('@')[0]

        for package, dependencies in graph.items():
            for dep in dependencies:
                if "ERROR" not in dep:
                    dep_name = dep.split('@')[0]
                    if dep_name == target_name:
                        reverse_deps.append(package)
                        break

        return reverse_deps

    def get_graph_statistics(self, graph):
        if not graph:
            return {
                "total_packages": 0,
                "total_dependencies": 0,
                "max_depth": 0,
                "has_cycles": False
            }

        total_deps = sum(1 for deps in graph.values() for dep in deps if "ERROR" not in dep)

        depths = {}
        max_depth = 0

        if graph:
            root = next(iter(graph.keys()))
            depths[root] = 0

            stack = [(root, 0)]
            while stack:
                node, depth = stack.pop()
                max_depth = max(max_depth, depth)

                if node in graph:
                    for dep in graph[node]:
                        if "ERROR" not in dep and dep not in depths:
                            depths[dep] = depth + 1
                            stack.append((dep, depth + 1))

        return {
            "total_packages": len(graph),
            "total_dependencies": total_deps,
            "max_depth": max_depth,
            "has_cycles": self._check_cycles(graph)
        }

    def _check_cycles(self, graph):
        def has_cycle(node, visited, recursion_stack):
            visited.add(node)
            recursion_stack.add(node)

            if node in graph:
                for neighbor in graph[node]:
                    if "ERROR" not in neighbor:
                        if neighbor not in visited:
                            if has_cycle(neighbor, visited, recursion_stack):
                                return True
                        elif neighbor in recursion_stack:
                            return True

            recursion_stack.remove(node)
            return False

        visited = set()
        for node in graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return True
        return False
