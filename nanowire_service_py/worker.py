import json
from typing import Any, Dict, Optional, Tuple, TypeVar, Generic, Union, List
from time import time, sleep
from pydantic import BaseModel, Json

from .utils import RuntimeError


class Workflow(BaseModel):
    id: str
    name: str


class Path(BaseModel):
    path_uuid: str
    instance_uuid: str
    parent_uuid: Optional[str]
    meta: Optional[Any]
    finished: Optional[str]
    branched: bool
    workflow_uuid: str


class Worker:
    worker_id: str
    heartbeat_timeout: int

    def __init__(
        self, conn: Any, worker_id: str, heartbeat_timeout: int
    ) -> None:
        self.conn = conn
        self.worker_id = worker_id
        self.heartbeat_timeout = heartbeat_timeout

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
    def plugin_instance(self, task_id: str) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                select pi.plugin_instance_id
                from active_queue as aq
                join path_instances pi on aq.instance_uuid = pi.uuid
                where aq.id = %s;
            """,
                [task_id],
            )
            instance: int = cur.fetchone()[0]
            return instance

    def branch(
        self,
        path_uuid: str,
        parent_path_uuid: str,
        parent_id: int,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            select branch_path(%s::uuid, %s::uuid, %s, %s::jsonb)
        """,
            [path_uuid, parent_path_uuid, parent_id, meta if meta else None],
        )
        self.conn.commit()
        cur.close()

    def create_workflow_instance(
        self, workflow_uuid: str, path_uuid: str, parent: Optional[int] = None
    ) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            select create_workflow_instance(%s::uuid, %s::uuid, %s)
        """,
            [workflow_uuid, path_uuid, parent],
        )
        self.conn.commit()
        cur.close()

    def create_workflow_tasks(
        self,
        path_uuid: str,
        max_attemps: int,
        args: Dict[str, Any],
        meta: Dict[str, Any],
        parent: Optional[int] = None,
        child_id: Optional[int] = None,
    ) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            select create_workflow_tasks(
                %s::uuid,
                %s::int,
                %s::jsonb,
                %s::jsonb,
                %s,
                %s
            )
        """,
            [
                path_uuid,
                max_attemps,
                json.dumps(args),
                json.dumps(meta),
                parent,
                child_id,
            ],
        )
        self.conn.commit()
        cur.close()

    def workflows(self) -> List[Workflow]:
        cur = self.conn.cursor()
        cur.execute("select id, name from workflows")
        results = [Workflow(id=row[0], name=row[1]) for row in cur.fetchall()]
        cur.close()
        return results

    def create_path(
        self,
        path_uuid: str,
        instance_uuid: str,
        workflow_uuid: str,
        meta: Dict[str, Any],
    ) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                insert into paths (path_uuid, instance_uuid, workflow_uuid, meta)
                values (%s, %s, %s, %s::jsonb);
            """,
                [path_uuid, instance_uuid, workflow_uuid, json.dumps(meta)],
            )
            self.conn.commit()

    def close_path(
        self,
        path_uuid: str,
        parent_id: Optional[int] = None,
        workflow_uuid: Optional[str] = None,
    ) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "select close_path(%s::uuid, %s::int, %s::uuid)",
                [path_uuid, parent_id, workflow_uuid],
            )
            self.conn.commit()

    def path_uuid(self, task_id: str) -> str:
        with self.conn.cursor() as cur:
            rows = cur.execute(
                """
                select path_uuid
                from active_queue aq
                join path_instances pi
                    on pi.uuid = sq.instance_uuid
                where aq.id = %s
                limit 1
            """,
                [task_id],
            ).fetchone()
            if rows is None:
                raise RuntimeError(
                    "Could not find path for the task", {"task_id": task_id}
                )
            return str(rows[0])

    def query(self, query: str, args: List[Any]) -> Any:
        with self.conn.cursor() as cur:
            cur.execute(query, args)
            rows = cur.fetchall()
            cols = [column[0] for column in cur.description]
            return [{cols[i]: col for i, col in enumerate(row)} for row in rows]

    def path(
        self,
        path_uuid: Optional[str] = None,
        task_id: Optional[str] = None,
        with_parent: bool = False,
    ) -> Tuple[Path, Optional[Path]]:
        if not path_uuid and not task_id:
            raise TypeError(
                "Expected either path_uuid or task_id to be provided"
            )

        path = None
        parent = None
        cols = {}
        if task_id:
            cols = self.query(
                """
                select p.*
                from active_queue aq
                join path_instances pi
                    on pi.uuid = aq.instance_uuid
                join paths p
                    on p.path_uuid = pi.path_uuid
                where aq.id = %s
                limit 1
            """,
                [task_id],
            )[0]
        else:
            cols = self.query(
                """
                select *
                from paths
                where path_uuid = %s
                limit 1
            """,
                [path_uuid],
            )[0]
        # END
        path = Path(**cols)

        if with_parent:
            cols = self.query(
                """
                select *
                from paths
                where path_uuid = %s
                limit 1
            """,
                [path.parent_uuid],
            )[0]
            parent = Path(**cols)

        return (path, parent)


__all__ = ["Worker"]
