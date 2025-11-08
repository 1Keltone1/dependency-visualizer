class DependencyVisualizerError(Exception):
    pass

class ConfigError(DependencyVisualizerError):
    pass

class ValidationError(DependencyVisualizerError):
    pass

class PackageNotFoundError(DependencyVisualizerError):
    pass

class NetworkError(DependencyVisualizerError):
    pass

class PackageDataError(DependencyVisualizerError):
    pass

class CyclicDependencyError(DependencyVisualizerError):
    pass