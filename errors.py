class DependencyVisualizerError(Exception):
    """Базовое исключение для приложения"""
    pass

class ConfigError(DependencyVisualizerError):
    """Ошибка конфигурации"""
    pass

class PackageNotFoundError(DependencyVisualizerError):
    """Пакет не найден"""
    pass

class RepositoryError(DependencyVisualizerError):
    """Ошибка работы с репозиторием"""
    pass

class ValidationError(DependencyVisualizerError):
    """Ошибка валидации параметров"""
    pass

class NetworkError(DependencyVisualizerError):
    """Ошибка сетевого запроса"""
    pass

class PackageDataError(DependencyVisualizerError):
    """Ошибка получения данных о пакете"""
    pass

class GraphError(DependencyVisualizerError):
    """Ошибка построения графа"""
    pass

class CyclicDependencyError(GraphError):
    """Обнаружены циклические зависимости"""
    pass