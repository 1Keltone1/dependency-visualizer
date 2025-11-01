import argparse
import os
import sys
from urllib.parse import urlparse
from errors import ValidationError, ConfigError


class Config:
    def __init__(self):
        self.package_name = None
        self.repository_url = None
        self.test_repo_mode = False
        self.package_version = None
        self.output_filename = "dependency_graph.png"
        self.filter_substring = None

    def validate(self):
        """Валидация конфигурации"""
        errors = []

        if not self.package_name:
            errors.append("Имя пакета обязательно для указания")

        if not self.repository_url:
            errors.append("URL репозитория или путь к файлу обязателен")
        else:
            if self.test_repo_mode:
                # В тестовом режиме проверяем существование файла
                if not os.path.exists(self.repository_url):
                    errors.append(f"Файл тестового репозитория не найден: {self.repository_url}")
            else:
                # В обычном режиме проверяем URL
                parsed_url = urlparse(self.repository_url)
                if not (parsed_url.scheme in ['http', 'https', 'file'] or os.path.exists(self.repository_url)):
                    errors.append(f"Некорректный URL или путь к файлу: {self.repository_url}")

        if self.output_filename:
            if not self.output_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
                errors.append("Имя файла должно иметь расширение изображения (.png, .jpg, .jpeg, .svg)")

        if errors:
            raise ValidationError("\n".join(errors))

    def __str__(self):
        """Строковое представление конфигурации"""
        return f"""Конфигурация приложения:
- Имя анализируемого пакета: {self.package_name}
- URL репозитория/путь к файлу: {self.repository_url}
- Режим тестового репозитория: {self.test_repo_mode}
- Версия пакета: {self.package_version}
- Имя файла с изображением: {self.output_filename}
- Подстрока для фильтрации: {self.filter_substring}"""