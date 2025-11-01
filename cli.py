import argparse
import sys
from config import Config
from errors import ValidationError, ConfigError


class CommandLineInterface:
    def __init__(self):
        self.parser = self._setup_parser()

    def _setup_parser(self):
        """Настройка парсера аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей пакетов',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  # Основной режим - построение графа зависимостей
  python main.py --package requests --repo-url https://pypi.org --version 2.25.1

  # Режим обратных зависимостей
  python main.py --package D --repo-url test_graph.json --test-mode --reverse-deps --root-package A

  # Тестовый режим с фильтрацией
  python main.py --package numpy --repo-url ./test_repo --test-mode --output deps.svg
            """
        )

        # Обязательные параметры
        parser.add_argument(
            '--package',
            '--package-name',
            dest='package_name',
            required=True,
            help='Имя анализируемого пакета (обязательно)'
        )

        parser.add_argument(
            '--repo-url',
            '--repository-url',
            dest='repository_url',
            required=True,
            help='URL репозитория или путь к файлу тестового репозитория (обязательно)'
        )

        # Опциональные параметры
        parser.add_argument(
            '--test-mode',
            '--test-repo-mode',
            dest='test_repo_mode',
            action='store_true',
            default=False,
            help='Режим работы с тестовым репозиторием (по умолчанию: False)'
        )

        parser.add_argument(
            '--version',
            '--package-version',
            dest='package_version',
            help='Версия пакета'
        )

        parser.add_argument(
            '--output',
            '--output-filename',
            dest='output_filename',
            default='dependency_graph.png',
            help='Имя сгенерированного файла с изображением графа (по умолчанию: dependency_graph.png)'
        )

        parser.add_argument(
            '--filter',
            '--filter-substring',
            dest='filter_substring',
            help='Подстрока для фильтрации пакетов'
        )

        # Новые параметры для этапа 4
        parser.add_argument(
            '--reverse-deps',
            '--reverse-dependencies',
            dest='reverse_dependencies',
            action='store_true',
            default=False,
            help='Режим поиска обратных зависимостей (только для этапа 4)'
        )

        parser.add_argument(
            '--root-package',
            dest='root_package',
            help='Корневой пакет для начала обхода при поиске обратных зависимостей'
        )

        return parser

    def parse_arguments(self):
        """Разбор аргументов командной строки и создание конфигурации"""
        try:
            args = self.parser.parse_args()

            config = Config()
            config.package_name = args.package_name
            config.repository_url = args.repository_url
            config.test_repo_mode = args.test_repo_mode
            config.package_version = args.package_version
            config.output_filename = args.output_filename
            config.filter_substring = args.filter_substring
            config.reverse_dependencies = args.reverse_dependencies
            config.root_package = args.root_package

            # Валидация конфигурации
            config.validate()

            return config

        except argparse.ArgumentError as e:
            raise ConfigError(f"Ошибка в аргументах командной строки: {e}")
        except SystemExit:
            # argparse вызывает sys.exit() при --help или ошибках
            raise ConfigError("Прервано пользователем")