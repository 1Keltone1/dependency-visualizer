import json
import os
from errors import PackageNotFoundError, PackageDataError


class TestRepository:
    """Тестовый репозиторий для работы с файлами описания графов"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.graph_data = self._load_graph_data()

    def _load_graph_data(self):
        """Загружает данные графа из файла"""
        if not os.path.exists(self.file_path):
            raise PackageNotFoundError(f"Файл тестового репозитория не найден: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise PackageDataError(f"Ошибка чтения файла тестового репозитория: {e}")

    def get_package_dependencies(self, package_name, version=None):
        """Получает зависимости пакета из тестового репозитория"""
        if package_name not in self.graph_data:
            raise PackageNotFoundError(f"Пакет '{package_name}' не найден в тестовом репозитории")

        return self.graph_data[package_name].get('dependencies', {})

    def filter_dependencies(self, dependencies, filter_substring):
        """Фильтрует зависимости по подстроке"""
        if not filter_substring:
            return dependencies

        filtered = {}
        for package, version in dependencies.items():
            if filter_substring.lower() not in package.lower():
                filtered[package] = version

        return filtered