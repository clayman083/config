import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union


T = TypeVar("T")

RawConfig = Dict[str, Union[str, int, bool]]


class InvalidField(Exception):
    def __init__(self, value):
        self._value = value


class Field(ABC, Generic[T]):
    def __init__(
        self,
        *,
        default: Optional[T] = None,
        env: Optional[str] = None,
        key: Optional[str] = None
    ) -> None:
        self.env = env
        self.key = key
        self.value: Optional[T] = default

    def __get__(self, obj, objtype) -> Optional[T]:
        return self.value

    def __set__(self, obj, value):
        self._set_value(value)

    def _set_value(self, value):
        normalized = self.normalize(value)
        self.validate(normalized)
        self.value = normalized

    @abstractmethod
    def normalize(self, value: Any) -> T:
        pass  # pragma: no cover

    def validate(self, value: T) -> bool:
        return True

    def load_from_dict(self, raw: RawConfig) -> None:
        if self.key and self.key in raw:
            self._set_value(raw[self.key])

    def load_from_env(self) -> None:
        if self.env and self.env in os.environ:
            self._set_value(os.environ[self.env])


class BaseConfig(type):
    def __new__(cls, name, bases, attrs):
        fields: Dict[str, Field] = {}

        for name, field in iter(attrs.items()):
            if isinstance(field, Field):
                if not field.key:
                    field.key = name

                if not field.env:
                    field.env = name.upper()

                fields[name] = field

        attrs["__fields__"] = fields

        return super(BaseConfig, cls).__new__(cls, name, bases, attrs)


class Config(metaclass=BaseConfig):
    __fields__: Dict[str, Field]

    def __init__(self, defaults: Optional[RawConfig] = None):
        if defaults:
            self.load_from_dict(defaults)

    def load_from_dict(self, raw: RawConfig) -> None:
        for field in iter(self.__fields__.values()):
            field.load_from_dict(raw)

    def load_from_env(self) -> None:
        for field in iter(self.__fields__.values()):
            field.load_from_env()


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


class NestedField(Field[Config]):
    def __init__(self, cls: Type[Config], *, key: Optional[str] = None):
        self.config_cls = cls
        self.config = cls()
        self.env = None
        self.key = key

    def __get__(self, obj, objtype) -> Config:
        return self.config

    def load_from_dict(self, raw: Any) -> None:
        if self.key and self.key in raw:
            self.config.load_from_dict(raw[self.key])

    def load_from_env(self) -> None:
        self.config.load_from_env()

    def normalize(self, value: Any) -> "Config":
        if isinstance(value, Config):
            return value
        elif isinstance(value, dict):
            return self.config_cls(value)
        else:
            raise InvalidField(value)


class ConsulConfig(Config):
    host = StrField(default="localhost", env="CONSUL_HOST")
    port = IntField(default=8500, env="CONSUL_PORT")


class PostgresConfig(Config):
    host = StrField(default="localhost", env="POSTGRES_HOST")
    port = IntField(default=5432, env="POSTGRES_PORT")
    user = StrField(default="postgres", env="POSTGRES_USER")
    password = StrField(default="postgres", env="POSTGRES_PASSWORD")
    database = StrField(default="postgres", env="POSTGRES_DATABASE")
