from config.base import Config, Field
from config.exceptions import ImproperlyConfigured, InvalidField
from config.fields import BoolField, FloatField, IntField, NestedField, StrField


__all__ = [
    "Config",
    "BoolField",
    "Field",
    "FloatField",
    "IntField",
    "NestedField",
    "StrField",
    "InvalidField",
    "ImproperlyConfigured",
]


class ConsulConfig(Config):
    host = StrField(default="localhost", env="CONSUL_HOST")
    port = IntField(default=8500, env="CONSUL_PORT")


class VaultConfig(Config):
    host = StrField(default="localhost", env="VAULT_HOST")
    port = IntField(default=3000, env="VAULT_PORT")
    token = StrField(default="", env="VAULT_TOKEN")


class PostgresConfig(Config):
    host = StrField(default="localhost", env="POSTGRES_HOST")
    port = IntField(default=5432, env="POSTGRES_PORT")
    user = StrField(default="postgres", env="POSTGRES_USER")
    password = StrField(default="postgres", env="POSTGRES_PASSWORD")
    database = StrField(default="postgres", env="POSTGRES_DATABASE")
