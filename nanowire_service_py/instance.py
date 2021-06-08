from typing import Tuple, Union
import psycopg2
from .types import Environment
from .utils import wait_for_port
from .worker import WorkerSpec


class Instance:
    env: Environment

    def __init__(self, env: Environment) -> None:
        self.conn = psycopg2.connect(
            env.POSTGRES_URL, options=f"-c search_path={env.POSTGRES_SCHEMA}"
        )
        self.env = env

    def subscriptions(self):
        return [
            {
                "topic": self.env.DAPR_APP_ID,
                "route": "/subscription",
                "pubsubname": self.env.PUB_SUB,
            }
        ]

    def register(self) -> Tuple[str, str]:
        cur = self.conn.cursor()
        cur.execute(
            """
            insert into workers (tag)
            values (%s)
            on conflict (tag) do update set tag = EXCLUDED.tag
            returning id, tag
        """,
            [self.env.DAPR_APP_ID + self.env.WORKER_SUFFIX],
        )
        (_id, tag) = cur.fetchone()
        cur.execute(
            """
            insert into worker_connections (worker_id, task_distributor_id)
            values (%s, %s)
            on conflict do nothing
        """,
            [_id, self.env.TASK_DISTRIBUTOR_ID],
        )
        self.conn.commit()
        cur.close()
        return (_id, self.env.TASK_DISTRIBUTOR_ID)

    @property
    def log_level(self) -> Union[str, int]:
        return self.env.LOG_LEVEL

    def wait_for_dapr(self) -> None:
        if not self.env.NO_WAIT:
            wait_for_port(self.env.DAPR_HTTP_PORT)

    def setup(self) -> WorkerSpec:
        (_id, distributor) = self.register()
        pending_endpoint = "http://localhost:{}/v1.0/publish/{}/pending".format(
            self.env.DAPR_HTTP_PORT, self.env.PUB_SUB
        )
        return (self.conn, _id, distributor, pending_endpoint)


__all__ = ["Instance"]
