from typing import Tuple, Union, Any
import psycopg2
from .types import Environment
from .utils import wait_for_port


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

    def register(self) -> Tuple[str, int]:
        cur = self.conn.cursor()
        cur.execute(
            """
            insert into workers (tag, name)
            values (%s, %s)
            returning id
        """,
            [self.env.DAPR_APP_ID, self.env.SERVICE_ID],
        )
        (worker_id) = cur.fetchone()
        cur.close()
        cur = self.conn.cursor()
        cur.execute(
            "select value from configuration where key = 'heartbeat_interval_s'"
        )
        results = cur.fetchone()
        if results is None or len(results) == 0:
            raise Exception(
                'Could not find "heartbeat_interval_s" in configuration'
            )
        timeout = int(results[0])
        cur.close()
        self.conn.commit()
        return (worker_id, timeout)

    @property
    def log_level(self) -> Union[str, int]:
        return self.env.LOG_LEVEL

    def wait_for_dapr(self) -> None:
        if not self.env.NO_WAIT:
            wait_for_port(self.env.DAPR_HTTP_PORT)

    def setup(self) -> Tuple[Any, str, int, str]:
        (worker_id, timeout) = self.register()
        pending_endpoint = "http://localhost:{}/v1.0/publish/{}/pending".format(
            self.env.DAPR_HTTP_PORT, self.env.SCHEDULER_PUB_SUB
        )
        return (self.conn, worker_id, timeout, pending_endpoint)


__all__ = ["Instance"]
