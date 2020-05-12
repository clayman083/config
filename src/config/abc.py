from abc import ABC, abstractmethod
from typing import Dict, Generic, Optional, TypeVar, Union

VT = Union[str, int, float, bool, "Config"]
FT = TypeVar("FT", bound="VT")

RawConfig = Dict[str, VT]


class Field(ABC, Generic[FT]):
    def __init__(
        self,
        *,
        default: Optional[FT] = None,
        key: Optional[str] = None,
        env: Optional[str] = None,
        path: Optional[str] = None,
        consul_path: Optional[str] = None,
        vault_path: Optional[str] = None,
        readonly: bool = False,
    ) -> None:
        self.env = env
        self.key = key
        self.path = path
        self.consul_path = consul_path
        self.vault_path = vault_path
        self.readonly = readonly
        self.value: Optional[FT] = default

    def __get__(self, obj, objtype) -> Optional[FT]:
        return self.value

    def __set__(self, obj, value: FT) -> None:
        self._set_value(value)

    def _set_value(self, value: VT) -> None:
        if not self.readonly:
            normalized = self.normalize(value)
            self.validate(normalized)
            self.value = normalized

    @abstractmethod
    def normalize(self, value: VT) -> FT:
        pass  # pragma: no cover

    def validate(self, value: FT) -> bool:
        return True

    def load_from_dict(self, raw: RawConfig) -> None:
        if self.key and self.key in raw:
            self._set_value(raw[self.key])


class ValueProvider(ABC):
    @abstractmethod
    def load(self, field: Field) -> Optional[str]:
        pass


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

    def load(self, providers) -> None:
        for field in iter(self.__fields__.values()):
            for provider in providers:
                provider.load(field)

    def load_from_dict(self, raw: RawConfig) -> None:
        for field in iter(self.__fields__.values()):
            field.load_from_dict(raw)
