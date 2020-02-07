class InvalidField(Exception):
    def __init__(self, value):
        self._value = value


class ImproperlyConfigured(Exception):
    def __init__(self, message) -> None:
        self._message = message

    @property
    def message(self) -> str:
        return self._message  # pragma: no cover
