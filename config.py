import os
from urllib.parse import urlparse
from errors import ValidationError


class Config:
    def __init__(self):
        self.package_name = None
        self.repository_url = None
        self.test_repo_mode = False
        self.package_version = None
        self.output_filename = "dependencies.svg"
        self.filter_substring = None
        self.reverse_dependencies = False
        self.root_package = None
        self.max_depth = 3

    def validate(self):
        errors = []

        if not self.package_name:
            errors.append("Укажите имя пакета (--package)")

        if not self.repository_url:
            errors.append("Укажите репозиторий (--repo-url)")
        elif self.test_repo_mode:
            if not os.path.exists(self.repository_url):
                errors.append(f"Файл не найден: {self.repository_url}")
        else:
            parsed = urlparse(self.repository_url)
            if not (parsed.scheme in ['http', 'https'] or os.path.exists(self.repository_url)):
                errors.append(f"Некорректный URL: {self.repository_url}")

        if self.output_filename:
            allowed = ('.svg', '.puml', '.txt', '.png', '.jpg', '.jpeg')
            has_allowed_extension = any(self.output_filename.lower().endswith(ext) for ext in allowed)

            if not has_allowed_extension:
                if '.' not in self.output_filename:
                    self.output_filename += '.svg'
                    print(f"💡 Расширение не указано, используется: {self.output_filename}")
                else:
                    errors.append(f"Разрешены расширения: {', '.join(allowed)}")

        if self.reverse_dependencies and not self.root_package:
            errors.append("Для обратных зависимостей укажите --root-package")

        if hasattr(self, 'max_depth') and self.max_depth <= 0:
            errors.append("Глубина обхода должна быть положительным числом")

        if errors:
            raise ValidationError("\n".join(errors))