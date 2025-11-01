from collections import deque
from errors import CyclicDependencyError, GraphError


class DependencyGraphBuilder:
    """Построитель графа зависимостей с использованием DFS без рекурсии"""

    def __init__(self, data_collector):
        self.data_collector = data_collector
        self.visited = set()
        self.graph = {}
        self.depth_limit = 10  # Ограничение глубины для избежания бесконечных циклов

    def build_dependency_graph(self, root_package, root_version=None, filter_substring=None, max_depth=10):
        """
        Строит граф зависимостей с использованием DFS без рекурсии

        Args:
            root_package: Корневой пакет
            root_version: Версия корневого пакета
            filter_substring: Подстрока для фильтрации пакетов
            max_depth: Максимальная глубина обхода

        Returns:
            dict: Граф зависимостей в формате {пакет: {зависимости}}
        """
        self.depth_limit = max_depth
        self.visited = set()
        self.graph = {}

        stack = [(root_package, root_version, 0)]  # (package, version, depth)

        while stack:
            current_package, current_version, depth = stack.pop()

            # Пропускаем если превышена глубина или пакет уже посещен
            if depth > self.depth_limit:
                continue

            package_key = f"{current_package}@{current_version}" if current_version else current_package

            if package_key in self.visited:
                continue

            self.visited.add(package_key)

            try:
                # Получаем зависимости текущего пакета
                dependencies = self.data_collector.get_package_dependencies(
                    current_package, current_version
                )

                # Применяем фильтр (исключаем пакеты, содержащие подстроку)
                if filter_substring:
                    dependencies = self.data_collector.filter_dependencies(
                        dependencies, filter_substring
                    )

                # Сохраняем в граф
                self.graph[package_key] = dependencies

                # Добавляем зависимости в стек для дальнейшего обхода
                for dep_package, dep_version in dependencies.items():
                    dep_key = f"{dep_package}@{dep_version}"

                    # Проверяем циклические зависимости
                    if self._has_cycle(package_key, dep_package):
                        raise CyclicDependencyError(
                            f"Обнаружена циклическая зависимость: {package_key} -> {dep_package}"
                        )

                    stack.append((dep_package, dep_version, depth + 1))

            except Exception as e:
                # Пропускаем пакеты с ошибками, но продолжаем обход
                self.graph[package_key] = {"ERROR": str(e)}
                continue

        return self.graph

    def find_reverse_dependencies(self, target_package, root_package, root_version=None, filter_substring=None,
                                  max_depth=10):
        """
        Находит обратные зависимости для заданного пакета

        Args:
            target_package: Пакет, для которого ищем обратные зависимости
            root_package: Корневой пакет для начала обхода
            root_version: Версия корневого пакета
            filter_substring: Подстрока для фильтрации пакетов
            max_depth: Максимальная глубина обхода

        Returns:
            list: Список пакетов, которые зависят от target_package
        """
        # Сначала строим полный граф зависимостей
        full_graph = self.build_dependency_graph(
            root_package, root_version, filter_substring, max_depth
        )

        # Ищем обратные зависимости
        reverse_deps = []

        for package, dependencies in full_graph.items():
            # Проверяем каждый пакет в графе на наличие зависимости от target_package
            for dep_package in dependencies.keys():
                dep_name = dep_package.split('@')[0] if '@' in dep_package else dep_package
                if dep_name == target_package:
                    reverse_deps.append(package)
                    break

        return reverse_deps

    def _has_cycle(self, current_package, next_package):
        """
        Проверяет наличие циклических зависимостей

        Args:
            current_package: Текущий пакет
            next_package: Следующий пакет для проверки

        Returns:
            bool: True если обнаружен цикл
        """
        # Простая проверка - если следующий пакет уже есть в графе как зависимость
        for package, deps in self.graph.items():
            if next_package in deps and current_package in self._get_all_dependencies(package):
                return True
        return False

    def _get_all_dependencies(self, package):
        """Рекурсивно получает все зависимости пакета"""
        all_deps = set()
        stack = [package]

        while stack:
            current = stack.pop()
            if current in self.graph:
                for dep in self.graph[current]:
                    if dep not in all_deps:
                        all_deps.add(dep)
                        stack.append(dep)

        return all_deps

    def get_graph_statistics(self):
        """Возвращает статистику графа"""
        total_packages = len(self.graph)
        total_dependencies = sum(len(deps) for deps in self.graph.values())

        return {
            "total_packages": total_packages,
            "total_dependencies": total_dependencies,
            "max_depth": self._calculate_max_depth(),
            "has_cycles": self._check_for_cycles()
        }

    def _calculate_max_depth(self):
        """Вычисляет максимальную глубину графа"""
        if not self.graph:
            return 0

        depths = {}
        root = next(iter(self.graph.keys()))
        depths[root] = 0
        max_depth = 0

        stack = [root]
        while stack:
            current = stack.pop()
            current_depth = depths[current]
            max_depth = max(max_depth, current_depth)

            if current in self.graph:
                for dep in self.graph[current]:
                    if dep not in depths:
                        depths[dep] = current_depth + 1
                        stack.append(dep)

        return max_depth

    def _check_for_cycles(self):
        """Проверяет наличие циклов в графе"""
        visited = set()
        recursion_stack = set()

        def has_cycle_util(node):
            if node not in self.graph:
                return False

            visited.add(node)
            recursion_stack.add(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True

            recursion_stack.remove(node)
            return False

        for node in self.graph:
            if node not in visited:
                if has_cycle_util(node):
                    return True

        return False