import json
from typing import Any, Dict, Optional, Tuple, TypeVar, Generic, Union
from time import time, sleep

class Worker:
    worker_id: str
    heartbeat_timeout: int

    def __init__(self, conn: Any, worker_id: str, heartbeat_timeout: int) -> None:
        self.conn = conn
        self.worker_id = worker_id
        self.heartbeat_timeout = heartbeat_timeout

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
            from get_task(%s::uuid, %s::uuid);
        """,
            [self.worker_id, task_id],
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

    def fail_task(
        self, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]
    ) -> None:
        cur = self.task_done("fail", task_id, result, meta)
        self.conn.commit()
        cur.close()

    def heartbeat(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            update workers
            set last_alive = now()
            where id = %s
        """,
            [self.worker_id],
        )
        self.conn.commit()
        cur.close()
        sleep(self.heartbeat_timeout)
        self.heartbeat()

    # Advanced usage
    def branch(path_uuid: str, parent_path_uuid: str, meta: Dict[str, Any] = None):
        cur = self.conn.cursor()
        cur.execute("""
            select branch_path(%s::uuid, %s::uuid, %s, %s::jsonb)
        """, [path_uuid, parent_path_uuid, self.worker_id, meta if meta else None])
        self.conn.commit()
        cur.close()

    def create_workflow_instance(workflow_uuid: str, path_uuid: str, parent: Optional[str] = None):
        cur = self.conn.cursor()
        cur.execute("""
            select create_workflow_instance(%s::uuid, %s::uuid, %s)
        """, [workflow_uuid, path_uuid, parent])
        self.conn.commit()
        cur.close()

    def create_workflow_tasks(
        path_uuid: str,
        max_attemps: int,
        args: Dict[str, Any],
        meta: Dict[str, Any],
        parent: Optional[str] = None,
        child_id: Optional[str] = None
    ):
        cur = self.conn.cursor()
        cur.execute("""
            select create_workflow_tasks(
                %s::uuid,
                %s::int,
                %s::jsonb,
                %s::jsonb,
                %s,
                %s
            )
        """, [
            path_uuid,
            max_attemps,
            json.dumps(args),
            json.dumps(meta),
            parent,
            child_id
        ])
        self.conn.commit()
        cur.close()

__all__ = ["Worker"]
