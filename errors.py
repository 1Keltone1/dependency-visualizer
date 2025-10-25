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