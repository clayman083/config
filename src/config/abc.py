from abc import ABC, abstractmethod
from typing import Dict, Generic, Iterable, Optional, TypeVar, Union


VT = Union[
    str, int, float, bool, "Config", Dict[str, Union[str, int, float, bool]]
]
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

    def get_value(self) -> Optional[FT]:
        return self.value

    @abstractmethod
    def normalize(self, value: VT) -> FT:
        pass  # pragma: no cover

    def validate(self, value: FT) -> bool:
        return True

    def load_from_dict(self, raw: RawConfig) -> Optional[FT]:
        normalized = None

        if self.key and self.key in raw:
            normalized = self.normalize(raw[self.key])
            self.validate(normalized)

        return normalized


class ValueProvider(ABC):
    @abstractmethod
    def load(self, field: Field) -> Optional[str]:
        pass  # pragma: no cover


class BaseConfig(type):
    def __new__(cls, name, bases, attrs):
        fields: Dict[str, Field] = {}

        for base_cls in bases:
            for field_name, field in base_cls.__fields__.items():
                if field_name not in attrs:
                    attrs[field_name] = field

        for field_name, field in iter(attrs.items()):
            if isinstance(field, Field):
                if not field.key:
                    field.key = field_name

                if not field.env:
                    field.env = field_name.upper()

                fields[field_name] = field

        for field_name in iter(fields.keys()):
            del attrs[field_name]

        attrs["__fields__"] = fields

        return super(BaseConfig, cls).__new__(cls, name, bases, attrs)


class Config(metaclass=BaseConfig):
    __dict__: Dict[str, Optional[VT]]
    __fields__: Dict[str, Field]

    def __init__(self, defaults: Optional[RawConfig] = None) -> None:
        for field_name, field in iter(self.__fields__.items()):
            self.__dict__[field_name] = field.get_value()

        if defaults:
            self.load_from_dict(defaults)

    def __getattr__(self, item: str) -> Optional[VT]:
        return self.__dict__[item]

    def __setattr__(self, name: str, value: Optional[VT]) -> None:
        if name in self.__fields__:
            field = self.__fields__.get(name)

            if field:
                normalized = field.normalize(value)  # type: ignore
                field.validate(normalized)

                self.__dict__[name] = normalized

    def load(self, providers: Iterable[ValueProvider]) -> None:
        for field_name, field in iter(self.__fields__.items()):
            for provider in providers:
                value = provider.load(field)

                setattr(self, field_name, value)

    def load_from_dict(self, raw: RawConfig) -> None:
        for field_name, field in iter(self.__fields__.items()):
            value = field.load_from_dict(raw)
            if value:
                setattr(self, field_name, value)
