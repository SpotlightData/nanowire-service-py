"""Wrapper for interacting with Nanowire platform"""
from nanowire_service_py.executor import Executor
from typing import Dict
from .types import *
from .worker import *
from .instance import *
from .utils import *
from .handler import *


def create(env: Dict[str, str], handler: BaseHandler) -> Executor:
    # Always handled by the library, pass environment directly 
    instance = Instance(Environment(**env))
    instance.wait_for_dapr()
    # Inherit worker specifications and logs from instance
    return Executor(handler, instance)