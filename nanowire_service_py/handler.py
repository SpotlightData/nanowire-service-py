from logging import Logger, log
from typing import Any, Dict, Tuple


class BaseHandler:
    logger: Logger

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def validate_args(self, args: Any, task_id: str) -> Any:
        raise TypeError("Implement validate_args on Handler class")

    def handle_body(
        self, args: Any, meta: Any, task_id: str
    ) -> Tuple[Dict[str, Any], Any]:
        raise TypeError("Implement handle_body on Handler class")


__all__ = ["BaseHandler"]
