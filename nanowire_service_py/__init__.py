"""Wrapper for interacting with Nanowire platform"""
from typing import Callable, Dict
from logging import Logger

from .executor import Executor
from .types import *
from .worker import *
from .instance import *
from .utils import *
from .handler import *


def create(env: Dict[str, str], make_handler: HandlerFactory) -> Executor:
    # Always handled by the library, pass environment directly
    parsed_env = Environment(**env)
    instance = Instance(parsed_env)
    instance.wait_for_dapr()
    # Inherit worker specifications and logs from instance
    return Executor(not parsed_env.NO_PUBLISH, make_handler, instance)
