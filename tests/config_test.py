import os  # noqa: F401

import pytest  # type: ignore

import config


class TestBoolField:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        "payload, expected",
        (
            (True, True),
            ("1", True),
            ("True", True),
            ("yes", True),
            (None, False),
            ("no", False),
            ("None", False),
        ),
    )
    def test_normalize(self, payload, expected):
        field = config.BoolField(default=False)
        normalized = field.normalize(payload)
        assert normalized is expected


class TestIntField:
    @pytest.mark.unit
    @pytest.mark.parametrize("payload", (5432, "5432"))
    def test_normalize(self, payload):
        field = config.IntField(default=0)
        normalized = field.normalize(payload)
        assert normalized == 5432

    @pytest.mark.unit
    @pytest.mark.parametrize("payload", ("foo", "abc123"))
    def test_normalize_failed(self, payload):
        field = config.IntField(default=0)
        with pytest.raises(config.InvalidField):
            field.normalize(payload)


class TestFloatField:
    @pytest.mark.unit
    @pytest.mark.parametrize("payload", (3.14, "3.14"))
    def test_normalize(self, payload):
        field = config.FloatField(default=0.0)
        normalized = field.normalize(payload)
        assert normalized == 3.14

    @pytest.mark.unit
    @pytest.mark.parametrize("payload", ("foo", "abc123"))
    def test_normalize_failed(self, payload):
        field = config.FloatField(default=0.0)
        with pytest.raises(config.InvalidField):
            field.normalize(payload)


@pytest.mark.unit
class TestConfig:
    @pytest.mark.unit
    def test_set_defaults(self):
        class TestConf(config.Config):
            debug = config.BoolField(default=False)

        conf = TestConf({"debug": True})

        assert conf.debug is True

    # @pytest.mark.unit
    # def test_load_from_env(self):
    #     class TestConf(config.Config):
    #         debug = config.BoolField(default=False, env="DEBUG")

    #     with mock.patch.dict("os.environ", {"DEBUG": "True"}):
    #         conf = TestConf()
    #         conf.load_from_env()

    #         assert conf.debug is True

    @pytest.mark.unit
    def test_load_from_dict(self):
        class TestConf(config.Config):
            debug = config.BoolField(default=False)
            secret_key = config.StrField()

        conf = TestConf()
        conf.load_from_dict({"debug": "True", "secret_key": "top_secret"})

        assert conf.debug is True
        assert conf.secret_key == "top_secret"


class TestConfigWithNested:
    @pytest.fixture(scope="function")
    def conf(self):
        class ConsulConfig(config.Config):
            host = config.StrField(default="localhost", env="CONSUL_HOST")
            port = config.IntField(default=8500, env="CONSUL_PORT")

        class TestConf(config.Config):
            consul = config.NestedField(ConsulConfig)

        return TestConf

    @pytest.mark.unit
    def test_set_defaults(self, conf):
        test_config = conf(
            {"consul": {"host": "consul.service.consul", "port": "8500"}}
        )

        assert test_config.consul.host == "consul.service.consul"
        assert test_config.consul.port == 8500

    # @pytest.mark.unit
    # def test_load_from_env(self, conf):
    #     with mock.patch.dict(
    #         "os.environ", {"CONSUL_HOST": "consul.service.consul"}
    #     ):
    #         test_config = conf()
    #         test_config.load_from_env()

    #         assert conf.consul.host == "consul.service.consul"
    #         assert conf.consul.port == 8500

    @pytest.mark.unit
    def test_load_from_dict(self, conf):
        test_config = conf()
        test_config.load_from_dict(
            {"consul": {"host": "consul.service.consul", "port": "8500"}}
        )

        assert test_config.consul.host == "consul.service.consul"
        assert test_config.consul.port == 8500

    @pytest.mark.unit
    def test_load_multiple_from_dict(self, conf):
        class ServiceConfig(config.Config):
            host = config.StrField()
            backend = config.StrField()

        class ServicesConfig(config.Config):
            bar = config.NestedField[ServiceConfig](ServiceConfig)
            baz = config.NestedField[ServiceConfig](ServiceConfig)

        class AppConfig(config.Config):
            foo = config.NestedField[ServiceConfig](ServiceConfig)
            services = config.NestedField[ServicesConfig](ServicesConfig)

        test_config = AppConfig()
        test_config.load_from_dict(
            {
                "foo": {"host": "foo.example.com", "backend": "127.0.0.1:5001"},
                "services": {
                    "bar": {
                        "host": "bar.example.com",
                        "backend": "127.0.0.1:5002",
                    },
                    "baz": {
                        "host": "baz.example.com",
                        "backend": "127.0.0.1:5003",
                    },
                },
            }
        )

        assert test_config.foo.host == "foo.example.com"
        assert test_config.services.bar.host == "bar.example.com"
        assert test_config.services.baz.host == "baz.example.com"


class TestConfigInheritance:
    @pytest.fixture(scope="function")
    def conf(self):
        class ConsulConfig(config.Config):
            host = config.StrField(default="localhost", env="CONSUL_HOST")
            port = config.IntField(default=8500, env="CONSUL_PORT")

        return ConsulConfig

    @pytest.mark.unit
    def test_inherit_fields_from_base(self, conf):
        class CustomConsulConfig(conf):
            dc = config.StrField(default="dc", env="CONSUL_DC")

        consul_config = CustomConsulConfig(
            {"host": "consul.service.consul", "port": "8500", "dc": "dc1"}
        )

        assert consul_config.host == "consul.service.consul"
        assert consul_config.port == 8500
        assert consul_config.dc == "dc1"

    @pytest.mark.unit
    def test_rewrite_fields_from_base(self, conf):
        class CustomConsulConfig(conf):
            host = config.StrField(default="consul.service.consul")

        consul_config = CustomConsulConfig()

        assert consul_config.host == "consul.service.consul"
        assert consul_config.port == 8500
