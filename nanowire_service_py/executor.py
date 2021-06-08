import logging
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pydantic import ValidationError

from .utils import RuntimeError
from .worker import Worker, WorkerSpec
from .handler import BaseHandler
from .instance import Instance


class Executor:
    worker: Worker
    logger: logging.Logger
    handler: BaseHandler
    # Us
    subscriptions: List[Dict[str, str]]

    def __init__(
        self,
        make_handler: Callable[[logging.Logger], BaseHandler],
        instance: Instance,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.worker = Worker(instance.setup())
        self.subscriptions = instance.subscriptions()
        if logger:
            self.logger = logger
        else:
            self.logger = self.configure_logging(instance.log_level)
        self.handler = make_handler(self.logger)

    def configure_logging(self, log_level: Union[str, int]) -> logging.Logger:
        if isinstance(log_level, str):
            log_level = log_level.upper()

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

    def handle_request(self, task_id: str) -> int:
        """
        Returned status code should be passed to the used server implementation
        """
        self.logger.debug("Task request received")
        task = self.worker.get_task(task_id)
        if task is None:
            self.logger.warning("Task was not found, already processed?")
            return 200
        self.worker.start_tracking()
        (args, meta) = task
        try:
            self.logger.debug("Received task from database [%s]", task_id)
            args = self.handler.validate_args(args, task_id)
            (result, meta) = self.handler.handle_body(args, meta, task_id)
            # Finish the task
            self.worker.finish(task_id, result, meta)
            self.logger.debug("Task finished [%s]", task_id)
            self.logger.debug(
                "Published pending to %s", self.worker.pending_endpoint
            )
            return 200
        except ValidationError as e:
            self.logger.warning("Failed to validate arguments: %s", repr(e))
            self.worker.stop_tracking()
            # NOTE: is there a way to extract json without parsing?
            self.worker.fail_task(task_id, json.loads(e.json()), meta)
            # Return normal response so dapr doesn't retry
            return 200
        except RuntimeError as e:
            self.logger.warning("Failed via RuntimeError: %s", repr(e))
            self.worker.stop_tracking()
            self.worker.fail_task(
                task_id, {"exception": repr(e), "errors": e.errors}, meta
            )
            # Return normal response so dapr doesn't retry
            return 200
        except Exception as e:
            # Unknown exections should cause dapr to retry
            self.worker.stop_tracking()
            self.logger.error(e)
            return 500


__all__ = ["Executor"]
