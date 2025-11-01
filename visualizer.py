import os
import subprocess
import tempfile
from errors import DependencyVisualizerError


class GraphVisualizer:
    """Визуализатор графа зависимостей с использованием PlantUML"""

    def __init__(self):
        self.plantuml_jar = self._find_plantuml()

    def _find_plantuml(self):
        """Пытается найти PlantUML JAR файл"""
        # Проверяем возможные пути
        possible_paths = [
            'plantuml.jar',
            '/usr/share/plantuml/plantuml.jar',
            '/opt/plantuml/plantuml.jar',
            './plantuml.jar'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Если не нашли, будем использовать онлайн-версию
        return None

    def generate_plantuml_code(self, graph, title="Dependency Graph"):
        """
        Генерирует код PlantUML для графа зависимостей

        Args:
            graph: Граф зависимостей в формате {пакет: {зависимости}}
            title: Заголовок диаграммы

        Returns:
            str: Код PlantUML
        """
        plantuml_code = ["@startuml", f"title {title}", "skinparam monochrome true", ""]

        # Собираем все узлы и связи
        nodes = set()
        edges = []

        for package, dependencies in graph.items():
            nodes.add(package)
            for dep, version in dependencies.items():
                if "ERROR" not in dep:  # Пропускаем ошибки
                    nodes.add(dep)
                    edges.append((package, dep, version))

        # Добавляем узлы
        for node in sorted(nodes):
            plantuml_code.append(f'rectangle "{node}"')

        plantuml_code.append("")

        # Добавляем связи
        for source, target, version in edges:
            plantuml_code.append(f'"{source}" --> "{target}" : {version}')

        plantuml_code.extend(["", "@enduml"])

        return "\n".join(plantuml_code)

    def generate_svg(self, graph, output_filename, title="Dependency Graph"):
        """
        Генерирует SVG изображение графа

        Args:
            graph: Граф зависимостей
            output_filename: Имя выходного файла
            title: Заголовок диаграммы

        Returns:
            str: Путь к созданному файлу
        """
        plantuml_code = self.generate_plantuml_code(graph, title)

        # Создаем временный файл для PlantUML кода
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
            f.write(plantuml_code)
            temp_file = f.name

        try:
            if self.plantuml_jar and os.path.exists(self.plantuml_jar):
                # Используем локальный PlantUML
                return self._generate_svg_local(temp_file, output_filename)
            else:
                # Используем онлайн PlantUML
                return self._generate_svg_online(plantuml_code, output_filename)
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def _generate_svg_local(self, plantuml_file, output_filename):
        """Генерирует SVG используя локальный PlantUML"""
        try:
            cmd = ['java', '-jar', self.plantuml_jar, '-tsvg', plantuml_file, '-o', os.path.dirname(output_filename)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise DependencyVisualizerError(f"Ошибка PlantUML: {result.stderr}")

            # PlantUML создает файл с тем же именем но с другим расширением
            base_name = os.path.splitext(os.path.basename(plantuml_file))[0]
            generated_svg = os.path.join(os.path.dirname(output_filename), base_name + '.svg')

            # Переименовываем в нужное имя
            if os.path.exists(generated_svg):
                os.rename(generated_svg, output_filename)

            if not os.path.exists(output_filename):
                raise DependencyVisualizerError("Не удалось создать SVG файл")

            return output_filename

        except subprocess.TimeoutExpired:
            raise DependencyVisualizerError("Таймаут при генерации SVG")
        except Exception as e:
            raise DependencyVisualizerError(f"Ошибка при локальной генерации SVG: {e}")

    def _generate_svg_online(self, plantuml_code, output_filename):
        """Генерирует SVG используя онлайн PlantUML сервер"""
        try:
            import urllib.request
            import urllib.parse

            # Кодируем PlantUML код для URL
            encoded = self._encode_plantuml(plantuml_code)
            url = f"http://www.plantuml.com/plantuml/svg/{encoded}"

            # Скачиваем SVG
            with urllib.request.urlopen(url) as response:
                svg_data = response.read()

            # Сохраняем в файл
            with open(output_filename, 'wb') as f:
                f.write(svg_data)

            return output_filename

        except Exception as e:
            raise DependencyVisualizerError(f"Ошибка при онлайн генерации SVG: {e}. Установите PlantUML локально.")

    def _encode_plantuml(self, text):
        """Кодирует текст для PlantUML онлайн"""
        import zlib
        import base64

        # Compress the text
        compressed = zlib.compress(text.encode('utf-8'))
        # Encode in base64
        encoded = base64.b64encode(compressed).decode('ascii')
        # Re-encode in PlantUML format
        result = ""
        for i in range(0, len(encoded), 3):
            block = encoded[i:i + 3]
            if len(block) == 3:
                result += block
            else:
                result += block + "=" * (3 - len(block))

        return result

    def save_plantuml_code(self, graph, filename, title="Dependency Graph"):
        """
        Сохраняет код PlantUML в файл

        Args:
            graph: Граф зависимостей
            filename: Имя файла для сохранения
            title: Заголовок диаграммы
        """
        plantuml_code = self.generate_plantuml_code(graph, title)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(plantuml_code)

        return filename

    def compare_with_npm(self, package_name, version=None):
        """
        Сравнивает результаты с выводом штатных инструментов npm

        Args:
            package_name: Имя пакета
            version: Версия пакета

        Returns:
            dict: Результаты сравнения
        """
        try:
            # Получаем дерево зависимостей через npm
            npm_tree = self._get_npm_dependency_tree(package_name, version)
            # Здесь можно добавить сравнение с нашим графом

            return {
                "npm_tree": npm_tree,
                "comparison": "Сравнение требует установленного npm и дополнительной реализации"
            }

        except Exception as e:
            return {
                "error": f"Не удалось получить данные npm: {e}",
                "note": "Убедитесь, что npm установлен и пакет доступен"
            }

    def _get_npm_dependency_tree(self, package_name, version=None):
        """Получает дерево зависимостей через npm"""
        try:
            package_spec = f"{package_name}@{version}" if version else package_name
            cmd = ['npm', 'view', package_spec, 'dependencies', '--json']

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            else:
                return "Не удалось получить зависимости через npm"

        except FileNotFoundError:
            return "npm не установлен"
        except subprocess.TimeoutExpired:
            return "Таймаут при запросе к npm"
        except Exception as e:
            return f"Ошибка: {e}"