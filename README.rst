config
======
.. image:: https://travis-ci.com/clayman083/config.svg?branch=master
    :target: https://travis-ci.com/clayman083/config

Framework agnostic configuration for apps and microservices .


Installation
------------

    $ pip install https://github.com/clayman083/config.git#v0.2.4


Usage
-----

The library allows us load application configuration from various sources,
such as environment variables, separate files with credentials and various config files.

A trivial usage example:

.. code:: python

    import click
    import config

    class AppConfig(config.Config):
        consul = config.NestedField[config.ConsulConfig](config.ConsulConfig)
        debug = config.BoolField(default=False)


    @click.group()
    @click.option("--debug", default=False, is_flag=True)
    @click.option("--conf-dir", default=None)
    @click.pass_context
    def cli(ctx, conf_dir: str = None, debug: bool = False) -> None:
        consul_config = config.ConsulConfig()
        config.load(consul_config, providers=[config.EnvValueProvider()])

        cfg = AppConfig(defaults={"consul": consul_config, "debug": debug})

        if conf_dir:
            conf_path = Path(conf_dir)
        else:
            conf_path = Path.cwd()

        config.load_from_file(config, path=conf_path / "config.json")
        config.load(cfg, providers=[
            config.FileValueProvider(conf_path),
            config.EnvValueProvider()
        ])

        print("Debug:", cfg.debug)
        print("Consul host:", cfg.consul.host)


TODO
----

- [ ] Add value provider to load config parts from Consul.
- [ ] Add value provider to load credentials from Vault.


Developing
----------

Install for local development::

    $ poetry install

Run tests with::

    $ tox


License
-------

``config`` is offered under the MIT license.
