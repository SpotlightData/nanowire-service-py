import logging
import json
import traceback
from typing import Any, Dict, Tuple
from fastapi import Response
from pydantic import ValidationError

from .utils import RuntimeError
from .worker import Worker, WorkerSpec

class Handler:
    worker: Worker
    logger: logging.Logger

    def __init__(self, spec: WorkerSpec, log_level: int = logging.DEBUG) -> None:
        self.worker = Worker(spec)
        self.logger = self.configure_logging(log_level)

    def configure_logging(self, log_level):
        logger = logging.getLogger("Handler")
        logger.setLevel(log_level)
        # Format for our loglines
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        # Setup console logging
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # # Setup file logging as well
        # fh = logging.FileHandler(LOG_FILENAME)
        # fh.setLevel(logging.DEBUG)
        # fh.setFormatter(formatter)
        # logger.addHandler(fh)
        return logger

    def validate_args(self, args: Any) -> Any:
        raise TypeError("Implement validate_args on Handler class")

    def handle_body(self, args: Any, meta: Any) -> Tuple[Dict[str, Any], Any]:
        raise TypeError("Implement handle_body on Handler class")

    def handle_request(self, task_id: str, response: Response) -> None:
        self.logger.debug("Task request received")
        task = self.worker.get_task(task_id)
        if task is None:
            self.logger.warn("Task was not found, already processed?")
            return
        self.worker.start_tracking()
        (args, meta) = task
        try:
            self.logger.debug("Received task from database [%s]", task_id)
            args = self.validate_args(args)
            (result, meta) = self.handle_body(args, meta)
            # self.worker.finish_task(task_id, result, meta)
            self.logger.debug("Task finished [%s]", task_id)
        except ValidationError as e:
            self.logger.warn("Failed to validate arguments: %s", repr(e))
            self.worker.stop_tracking()
            # NOTE: is there a way to extract json without parsing?
            self.worker.fail_task(task_id, json.loads(e.json()), meta)
            # Return normal response so dapr doesn't retry
            return
        except RuntimeError as e:
            self.logger.warn("Failed via RuntimeError: %s", repr(e))
            self.worker.stop_tracking()
            # NOTE: is there a way to extract json without parsing?
            self.worker.fail_task(task_id, {"exception": repr(e), "errors": e.errors }, meta)
            # Return normal response so dapr doesn't retry
            return
        except Exception as e:
            # Unknown exections should cause dapr to retry
            self.worker.stop_tracking()
            self.logger.error(e)
            response.status_code = 500
            return

__all__ = ["Handler"]
