from pathlib import Path


class InvalidField(Exception):
    def __init__(self, value) -> None:
        self.value = value


class ConfigFileError(Exception):
    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path


class ConfigNotFound(ConfigFileError):
    pass


class BrokenConfig(ConfigFileError):
    pass


class UnknownConfigFormat(ConfigFileError):
    pass
