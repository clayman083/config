import os
from pathlib import Path
from typing import Optional

from config.abc import Field, ValueProvider


class EnvValueProvider(ValueProvider):
    def load(self, field: Field) -> Optional[str]:
        value = None

        if field.env and field.env in os.environ:
            value = os.environ[field.env]

        return value


class FileValueProvider(ValueProvider):
    def __init__(self, conf_dir) -> None:
        self.conf_dir = Path(conf_dir)

    def load(self, field: Field) -> Optional[str]:
        value = None

        if field.path:
            try:
                with (self.conf_dir / field.path).open() as fp:
                    value = fp.read()
            except IOError as e:
                raise e

        return value
