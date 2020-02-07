import os
from abc import ABC, abstractmethod
from typing import Dict, Generic, Mapping, Optional, TypeVar, Union


T = TypeVar("T")

RawConfig = Dict[str, Union[bool, int, str, Mapping]]


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
    def normalize(self, value: str) -> T:
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

        for base_cls in bases:
            for field_name, field in base_cls.__fields__.items():
                if field_name not in attrs:
                    attrs[field_name] = field

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
