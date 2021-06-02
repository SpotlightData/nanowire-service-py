import json
from typing import Any, Dict, Optional, Tuple, TypeVar, Generic

WorkerSpec =  Tuple[Any, str, str]

class Worker:
    worker_id: str
    distributor_id: str

    def __init__(self, spec: WorkerSpec) -> None:
        (conn, worker_id, distributor_id) = spec
        self.conn = conn
        self.worker_id = worker_id
        self.distributor_id = distributor_id

    # Allow user to cast it on their end
    def get_task(self, task_id: str) -> Optional[Tuple[Any, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            select args, meta
            from get_task($1::uuid, $2::uuid, $3::uuid);
        """, [self.distributor_id, self.worker_id, task_id])
        row = cur.fetchone()
        self.conn.commit()
        cur.close()
        if row:
            return (row[0], row[1])
        return None

    def task_done(self, mode: str, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]) -> None:
        cur = self.conn.cursor()
        cur.execute("select ${}_task($1::uuid, $2::jsonb, $3::jsonb)".format(mode), [task_id, json.dumps(result), json.dumps(meta)])
        self.conn.commit()
        cur.close()

    def finish_task(self, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]) -> None:
        self.task_done('finish', task_id, result, meta)

    def fail_task(self, task_id: str, result: Dict[str, Any], meta: Dict[str, Any]) -> None:
        self.task_done('fail', task_id, result, meta)

__all__ = ["WorkerSpec", "Worker"]
