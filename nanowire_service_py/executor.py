import logging
import json
import traceback
import threading
import requests
from time import time, sleep

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from pydantic import ValidationError

from .utils import RuntimeError
from .worker import Worker
from .handler import BaseHandler, HandlerFactory
from .collection import UsageCollection
from .instance import Instance


class Executor:
    worker: Worker
    logger: logging.Logger
    handler: BaseHandler
    # Us
    subscriptions: List[Dict[str, str]]
    # Resource tracking
    collection: UsageCollection
    started: float
    pending_endpoint: str
    should_publish: bool

    def __init__(
        self,
        should_publish: bool,
        make_handler: HandlerFactory,
        instance: Instance,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.should_publish = should_publish

        (
            conn,
            worker_id,
            heartbeat_timeout,
            pending_endpoint,
        ) = instance.setup()
        # Worker details
        self.pending_endpoint = pending_endpoint
        self.worker = Worker(conn, worker_id, heartbeat_timeout)
        #
        self.subscriptions = instance.subscriptions()
        if logger:
            self.logger = logger
        else:
            self.logger = self.configure_logging(instance.log_level)
        self.handler = make_handler(self.logger, self.worker)
        # Resource tracking
        self.collection = UsageCollection()
        self.started = time()

    def start_tracking(self) -> None:
        self.collection.start_collection()
        self.started = time()

    def stop_tracking(self) -> None:
        """
        Should only be used when handling failure.
        Otherwise finish() method should be used
        """
        self.collection.finish_collection()

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

    def heartbeat(self) -> None:
        th = threading.Thread(target=self.worker.heartbeat)
        th.daemon = True
        th.start()

    def handle_request(self, task_id: str) -> int:
        """
        Returned status code should be passed to the used server implementation
        """
        self.logger.debug("Task request received [%s]", task_id)
        task = self.worker.get_task(task_id)
        if task is None:
            self.logger.warning("Task was not found, already processed?")
            return 200
        self.start_tracking()
        (org_args, org_meta) = task
        try:
            self.logger.debug("Received task from database [%s]", task_id)
            args = self.handler.validate_args(org_args, task_id)
            meta = self.handler.validate_meta(org_meta, task_id)
            (result, meta) = self.handler.handle_body(args, meta, task_id)
            # Finish the task
            [max_mem, max_cpu] = self.collection.finish_collection()
            time_taken = round(time() - self.started, 2)
            self.worker.finish_task(
                task_id,
                {
                    **result,
                    "max_cpu": max_cpu,
                    "max_mem": max_mem,
                    "time_taken": time_taken,
                },
                meta,
            )

            self.logger.debug("Task finished [%s]", task_id)
            # Publish for rest of workflow to
            if self.should_publish:
                requests.post(self.pending_endpoint, json={"id": task_id})
                self.logger.debug(
                    "Published pending to %s", self.pending_endpoint
                )
            else:
                self.logger.debug("Skipping publishing")

            return 200
        except ValidationError as e:
            self.logger.warning("Failed to validate arguments: %s", repr(e))
            self.stop_tracking()
            # NOTE: is there a way to extract json without parsing?
            self.worker.fail_task(task_id, json.loads(e.json()), org_meta)
            # Return normal response so dapr doesn't retry
            return 200
        except RuntimeError as e:
            self.logger.warning("Failed via RuntimeError: %s", repr(e))
            self.stop_tracking()
            self.worker.fail_task(
                task_id, {"exception": repr(e), "errors": e.errors}, org_meta
            )
            # Return normal response so dapr doesn't retry
            return 200
        except Exception as e:
            self.logger.error("Failed via Exception: %s", repr(e))
            traceback.print_exc()
            # Unknown exections should cause dapr to retry
            self.stop_tracking()
            self.logger.error(e)
            return 500


__all__ = ["Executor"]
