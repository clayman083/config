from typing import List

from config.abc import Config, ValueProvider
from config.exceptions import InvalidField
from config.fields import BoolField, FloatField, IntField, NestedField, StrField
from config.providers import EnvValueProvider, FileValueProvider


__all__ = (
    "BoolField",
    "IntField",
    "NestedField",
    "StrField",
    "FloatField",
    "Config",
    "InvalidField",
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
