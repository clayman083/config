from pathlib import Path
from typing import List

import ujson

from config.abc import Config, ValueProvider
from config.exceptions import (
    BrokenConfig,
    ConfigNotFound,
    InvalidField,
    UnknownConfigFormat,
)
from config.fields import BoolField, FloatField, IntField, NestedField, StrField
from config.providers import EnvValueProvider, FileValueProvider


__all__ = (
    "BoolField",
    "IntField",
    "NestedField",
    "StrField",
    "FloatField",
    "Config",
    "BrokenConfig",
    "ConfigNotFound",
    "InvalidField",
    "UnknownConfigFormat",
    "EnvValueProvider",
    "FileValueProvider",
)


def load(config: Config, providers: List[ValueProvider]) -> None:
    for field_name, field in iter(config.__fields__.items()):
        if isinstance(field, (NestedField,)):
            load(field.config, providers)
        else:
            for provider in providers:
                value = provider.load(field)
                if value:
                    setattr(config, field_name, value)


def load_from_file(config: Config, path: Path, silent: bool = False) -> None:
    if not path.exists():
        raise ConfigNotFound(path)

    try:
        with path.open() as fp:
            raw = fp.read()
    except IOError:
        if not silent:
            raise ConfigNotFound(path)
    else:
        if path.suffix == ".json":
            try:
                config_data = ujson.loads(raw)
            except ValueError:
                raise BrokenConfig(path)
        else:
            raise UnknownConfigFormat(path)

        config.load_from_dict(config_data)


class ConsulConfig(Config):
    host = StrField(default="localhost", env="CONSUL_HOST")
    port = IntField(default=8500, env="CONSUL_PORT")


class VaultConfig(Config):
    host = StrField(default="localhost", env="VAULT_HOST")
    port = IntField(default=3000, env="VAULT_PORT")
    token = StrField(env="VAULT_TOKEN")


class PostgresConfig(Config):
    host = StrField(default="localhost", env="POSTGRES_HOST")
    port = IntField(default=5432, env="POSTGRES_PORT")
    user = StrField(default="postgres", env="POSTGRES_USER")
    password = StrField(default="postgres", env="POSTGRES_PASSWORD")
    database = StrField(default="postgres", env="POSTGRES_DATABASE")
    min_pool_size = IntField(default=1, env="POSTGRES_MIN_POOL_SIZE")
    max_pool_size = IntField(default=2, env="POSTGRES_MAX_POOL_SIZE")
