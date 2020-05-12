from typing import Any, Generic, Optional, Type, TypeVar

from config.abc import Config, Field
from config.exceptions import InvalidField


class BoolField(Field[bool]):
    def normalize(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        else:
            return str(value).lower() in ["true", "1", "yes"]


class IntField(Field[int]):
    def normalize(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        else:
            try:
                return int(value)
            except ValueError:
                raise InvalidField(value)


class FloatField(Field[float]):
    def normalize(self, value: Any) -> float:
        if isinstance(value, float):
            return value
        else:
            try:
                return float(value)
            except ValueError:
                raise InvalidField(value)


class StrField(Field[str]):
    def normalize(self, value: Any) -> str:
        return str(value)


C = TypeVar("C", bound="Config")


class NestedField(Field[Config], Generic[C]):
    def __init__(
        self, cls: Type[C], *, key: Optional[str] = None, **kwargs
    ) -> None:
        super().__init__(key=key, **kwargs)

        self.config_cls = cls
        self.config = cls()

    def __get__(self, obj, objtype) -> C:
        return self.config

    def load_from_dict(self, raw: Any) -> None:
        if self.key and self.key in raw:
            value = raw[self.key]
            if isinstance(value, Config):
                self._set_value(value)
            else:
                self.config.load_from_dict(raw[self.key])

    def normalize(self, value: Any) -> Config:
        if isinstance(value, Config):
            return value
        elif isinstance(value, dict):
            return self.config_cls(value)
        else:
            raise InvalidField(value)
