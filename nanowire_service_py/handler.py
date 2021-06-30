from logging import Logger, log
from typing import Any, Dict, Tuple, Callable, Optional

from .worker import Worker


class BaseHandler:
    logger: Logger
    worker: Optional[Worker]

    def __init__(self, logger: Logger, worker: Optional[Worker] = None) -> None:
        self.logger = logger
        # For advanced usage, when we need direct access
        self.worker = worker

    def validate_args(self, args: Any, task_id: str) -> Any:
        raise TypeError("Implement validate_args on Handler class")

    def validate_meta(self, meta: Any, task_id: str) -> Any:
        return meta

    def handle_body(
        self, args: Any, meta: Any, task_id: str
    ) -> Tuple[Dict[str, Any], Any]:
        raise TypeError("Implement handle_body on Handler class")


HandlerFactory = Callable[[Logger, Worker], BaseHandler]

__all__ = ["BaseHandler", "HandlerFactory"]
