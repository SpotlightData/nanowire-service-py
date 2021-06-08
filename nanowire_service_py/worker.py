import json
from typing import Any, Dict, Optional, Tuple, TypeVar, Generic
from time import time
from .collection import UsageCollection
import requests

WorkerSpec = Tuple[Any, str, str, str]


class Worker:
    worker_id: str
    distributor_id: str
    pending_endpoint: str
    collection: UsageCollection
    started: float

    def __init__(self, spec: WorkerSpec) -> None:
        (conn, worker_id, distributor_id, pending_endpoint) = spec
        self.conn = conn
        self.worker_id = worker_id
        self.distributor_id = distributor_id
        self.pending_endpoint = pending_endpoint
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

    def finish(
        self, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]
    ) -> None:
        [max_mem, max_cpu] = self.collection.finish_collection()
        time_taken = round(time() - self.started, 2)
        self.finish_task(
            task_id,
            {
                **result,
                "max_cpu": max_cpu,
                "max_mem": max_mem,
                "time_taken": time_taken,
            },
            meta,
        )

    # Allow user to cast it on their end
    def get_task(self, task_id: str) -> Optional[Tuple[Any, Any]]:
        cur = self.conn.cursor()
        cur.execute(
            """
            select args, meta
            from get_task(%s::uuid, %s::uuid, %s::uuid);
        """,
            [self.distributor_id, self.worker_id, task_id],
        )
        row = cur.fetchone()
        self.conn.commit()
        cur.close()
        if row:
            return (row[0], row[1])
        return None

    def task_done(
        self,
        mode: str,
        task_id: str,
        result: Dict[str, Any],
        meta: Dict[str, Any],
    ) -> Any:
        cur = self.conn.cursor()
        cur.execute(
            "select {}_task(%s::uuid, %s::jsonb, %s::jsonb)".format(mode),
            [task_id, json.dumps(result), json.dumps(meta)],
        )
        return cur

    def finish_task(
        self, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]
    ) -> None:
        cur = self.task_done("finish", task_id, result, meta)
        self.conn.commit()
        cur.close()
        requests.post(self.pending_endpoint, json={"id": task_id})

    def fail_task(
        self, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]
    ) -> None:
        cur = self.task_done("fail", task_id, result, meta)
        self.conn.commit()
        cur.close()


__all__ = ["WorkerSpec", "Worker"]
