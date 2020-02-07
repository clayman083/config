from typing import Optional, Type, Union

from config.base import Config, Field, RawConfig
from config.exceptions import ImproperlyConfigured, InvalidField


class BoolField(Field[bool]):
    def normalize(self, value: str) -> bool:
        if isinstance(value, bool):
            return value
        else:
            return str(value).lower() in ["true", "1", "yes"]


class IntField(Field[int]):
    def normalize(self, value: str) -> int:
        if isinstance(value, int):
            return value
        else:
            try:
                return int(value)
            except ValueError:
                raise InvalidField(value)


class FloatField(Field[float]):
    def normalize(self, value: str) -> float:
        if isinstance(value, float):
            return value
        else:
            try:
                return float(value)
            except ValueError:
                raise InvalidField(value)


class StrField(Field[str]):
    def normalize(self, value: str) -> str:
        return value


class NestedField(Field[Config]):
    def __init__(self, cls: Type[Config], *, key: Optional[str] = None):
        self.config_cls = cls
        self.config = cls()
        self.env = None
        self.key = key

    def __get__(self, obj, objtype) -> Config:
        return self.config

    def load_from_dict(self, raw: RawConfig) -> None:
        if self.key and self.key in raw:
            subconfig = raw[self.key]
            if isinstance(subconfig, dict):
                self.config.load_from_dict(subconfig)
            else:
                raise ImproperlyConfigured(
                    f"'{self.key}' section should be dict"
                )

    def load_from_env(self) -> None:
        self.config.load_from_env()

    def normalize(self, value: Union[str, Config, RawConfig]) -> "Config":
        if isinstance(value, Config):
            return value
        elif isinstance(value, dict):
            return self.config_cls(value)
        else:
            raise InvalidField(value)
