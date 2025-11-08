import json
import urllib.request
import urllib.error
from errors import NetworkError, PackageDataError, PackageNotFoundError


class NPMDataCollector:
    def __init__(self, repository_url, test_mode=False):
        self.repository_url = repository_url
        self.test_mode = test_mode

    def get_package_dependencies(self, package_name, version=None):
        if self.test_mode:
            return self._get_test_dependencies(package_name)

        try:
            url = f"https://registry.npmjs.org/{package_name}"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))

            if version and version in data.get('versions', {}):
                target_version = version
            else:
                target_version = data.get('dist-tags', {}).get('latest',
                                                               sorted(data.get('versions', {}).keys())[-1])

            version_data = data['versions'][target_version]

            dependencies = {}
            dependencies.update(version_data.get('dependencies', {}))
            dependencies.update(version_data.get('devDependencies', {}))
            dependencies.update(version_data.get('peerDependencies', {}))

            return dependencies

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise PackageNotFoundError(f"Пакет '{package_name}' не найден")
            raise NetworkError(f"HTTP ошибка {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise NetworkError(f"Ошибка сети: {e.reason}")
        except Exception as e:
            raise PackageDataError(f"Ошибка обработки данных: {e}")

    def _get_test_dependencies(self, package_name):
        try:
            with open(self.repository_url, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if package_name in data:
                return data[package_name].get('dependencies', {})
            else:
                raise PackageNotFoundError(f"Пакет '{package_name}' не найден в тестовом репозитории")

        except FileNotFoundError:
            raise PackageNotFoundError(f"Файл не найден: {self.repository_url}")
        except json.JSONDecodeError:
            raise PackageDataError("Ошибка чтения JSON файла")

    def filter_dependencies(self, dependencies, filter_substring):
        if not filter_substring:
            return dependencies

        filtered = {}
        for package, version in dependencies.items():
            if filter_substring.lower() not in package.lower():
                filtered[package] = version

        return filtered