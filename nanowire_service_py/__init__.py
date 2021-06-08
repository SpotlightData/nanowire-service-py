"""Wrapper for interacting with Nanowire platform"""
from typing import Callable, Dict
from logging import Logger

from .executor import Executor
from .types import *
from .worker import *
from .instance import *
from .utils import *
from .handler import *


def create(
    env: Dict[str, str], make_handler: Callable[[Logger], BaseHandler]
) -> Executor:
    # Always handled by the library, pass environment directly
    instance = Instance(Environment(**env))
    instance.wait_for_dapr()
    # Inherit worker specifications and logs from instance
    return Executor(make_handler, instance)
