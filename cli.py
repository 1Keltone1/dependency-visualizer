import argparse
from config import Config
from errors import ConfigError


class CommandLineInterface:
    def __init__(self):
        self.parser = self._setup_parser()

    def _setup_parser(self):
        parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей npm пакетов',
            epilog="""
Примеры использования:
  # Тестовый режим
  python main.py --package A --repo-url test_graph.json --test-mode --output test.puml

  # Реальный пакет
  python main.py --package react --repo-url https://registry.npmjs.org --output deps.svg

  # С ограничением глубины
  python main.py --package express --repo-url https://registry.npmjs.org --output express.puml --max-depth 2

  # Обратные зависимости
  python main.py --package chalk --repo-url https://registry.npmjs.org --reverse-deps --root-package express --output reverse.txt

  # С фильтрацией
  python main.py --package webpack --repo-url https://registry.npmjs.org --filter "loader" --output filtered.puml
            """
        )

        parser.add_argument('--package', required=True, help='Имя пакета')
        parser.add_argument('--repo-url', required=True, help='URL репозитория или путь к файлу')
        parser.add_argument('--test-mode', action='store_true', help='Тестовый режим')
        parser.add_argument('--version', help='Версия пакета')
        parser.add_argument('--output', default='dependencies.svg', help='Выходной файл')
        parser.add_argument('--filter', help='Фильтр пакетов')
        parser.add_argument('--reverse-deps', action='store_true', help='Обратные зависимости')
        parser.add_argument('--root-package', help='Корневой пакет для обратных зависимостей')
        parser.add_argument('--max-depth', type=int, default=3, help='Максимальная глубина обхода')

        return parser

    def parse_arguments(self):
        try:
            args = self.parser.parse_args()

            config = Config()
            config.package_name = args.package
            config.repository_url = args.repo_url
            config.test_repo_mode = args.test_mode
            config.package_version = args.version
            config.output_filename = args.output
            config.filter_substring = args.filter
            config.reverse_dependencies = args.reverse_deps
            config.root_package = args.root_package
            config.max_depth = args.max_depth

            config.validate()
            return config

        except SystemExit:
            raise ConfigError("Прервано")