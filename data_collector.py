import json
import urllib.request
import urllib.error
from urllib.parse import urljoin
from errors import NetworkError, PackageDataError, PackageNotFoundError


class NPMDataCollector:
    """Сборщик данных о зависимостях npm пакетов"""

    def __init__(self, repository_url):
        self.repository_url = repository_url.rstrip('/')
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        """Определяет базовый URL для API npm репозитория"""
        if self.repository_url == 'https://registry.npmjs.org':
            return 'https://registry.npmjs.org'
        elif 'registry.npmjs.org' in self.repository_url:
            return self.repository_url
        else:
            # Для кастомных репозиториев предполагаем структуру npm registry
            return urljoin(self.repository_url, '/')

    def get_package_dependencies(self, package_name, version=None):
        """
        Получает прямые зависимости пакета

        Args:
            package_name: Имя пакета
            version: Версия пакета (опционально)

        Returns:
            dict: Словарь с зависимостями {имя_пакета: версия}
        """
        try:
            # Получаем информацию о пакете
            package_data = self._fetch_package_data(package_name)

            # Определяем нужную версию
            target_version = self._resolve_version(package_data, version)

            # Извлекаем зависимости
            dependencies = self._extract_dependencies(package_data, target_version)

            return dependencies

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise PackageNotFoundError(f"Пакет '{package_name}' не найден в репозитории")
            else:
                raise NetworkError(f"HTTP ошибка при получении данных: {e.code}")
        except urllib.error.URLError as e:
            raise NetworkError(f"Ошибка подключения к репозиторию: {e.reason}")
        except (KeyError, ValueError) as e:
            raise PackageDataError(f"Ошибка разбора данных пакета: {e}")

    def _fetch_package_data(self, package_name):
        """Получает данные о пакете из npm registry"""
        url = f"{self.base_url}/{package_name}"

        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
                else:
                    raise NetworkError(f"Ошибка HTTP {response.status}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise PackageNotFoundError(f"Пакет '{package_name}' не найден")
            raise

    def _resolve_version(self, package_data, version_spec=None):
        """Определяет конкретную версию пакета"""
        versions = package_data.get('versions', {})

        if not versions:
            raise PackageDataError("Пакет не имеет версий")

        if version_spec:
            # Ищем точное соответствие версии
            if version_spec in versions:
                return version_spec
            else:
                # Пытаемся найти подходящую версию по семантическому versioning
                matching_version = self._find_matching_version(versions, version_spec)
                if not matching_version:
                    raise PackageDataError(
                        f"Версия '{version_spec}' не найдена для пакета '{package_data.get('name', 'unknown')}'. Доступные версии: {', '.join(list(versions.keys())[:5])}...")
                return matching_version
        else:
            # Используем latest версию
            dist_tags = package_data.get('dist-tags', {})
            latest_version = dist_tags.get('latest')
            if latest_version and latest_version in versions:
                return latest_version
            else:
                # Берем последнюю версию по дате
                return sorted(versions.keys(), key=self._parse_version)[-1]

    def _find_matching_version(self, versions, version_spec):
        """Находит версию, соответствующую спецификации"""
        available_versions = list(versions.keys())

        # Простая логика для демонстрации
        # В реальной системе нужно использовать семантический versioning

        # Проверяем точное совпадение
        if version_spec in available_versions:
            return version_spec

        # Проверяем префикс (например, "1.0" для "1.0.0")
        for version in available_versions:
            if version.startswith(version_spec):
                return version

        # Если ничего не нашли, возвращаем None
        return None

    def _parse_version(self, version_str):
        """Парсит версию для сравнения"""
        # Упрощенный парсинг версий
        version_str = version_str.strip('v')
        parts = version_str.split('.')

        # Преобразуем части версии в числа
        numeric_parts = []
        for part in parts:
            # Убираем нечисловые суффиксы
            numeric_part = ''
            for char in part:
                if char.isdigit():
                    numeric_part += char
                else:
                    break
            numeric_parts.append(int(numeric_part) if numeric_part else 0)

        # Дополняем нулями до 3 частей
        while len(numeric_parts) < 3:
            numeric_parts.append(0)

        return numeric_parts

    def _extract_dependencies(self, package_data, version):
        """Извлекает зависимости для конкретной версии"""
        version_data = package_data['versions'][version]

        dependencies = {}

        # Основные зависимости
        deps = version_data.get('dependencies', {})
        dependencies.update(deps)

        # Dev зависимости (опционально)
        dev_deps = version_data.get('devDependencies', {})
        dependencies.update(dev_deps)

        # Peer зависимости (опционально)
        peer_deps = version_data.get('peerDependencies', {})
        dependencies.update(peer_deps)

        return dependencies

    def filter_dependencies(self, dependencies, filter_substring):
        """Фильтрует зависимости по подстроке"""
        if not filter_substring:
            return dependencies

        filtered = {}
        for package, version in dependencies.items():
            if filter_substring.lower() in package.lower():
                filtered[package] = version

        return filtered