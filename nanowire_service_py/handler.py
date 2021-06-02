from typing import Tuple
import psycopg2
from .env import Environment
from .wait_for_port import wait_for_port
from .worker import WorkerSpec

class Handler:
    env: Environment

    def __init__(self, env: Environment) -> None:
        self.conn = psycopg2.connect(env.POSTGRES_URL, options=f'-c search_path={env.POSTGRES_SCHEMA}')
        self.env = env

    def subscriptions(self):
        return { "topic": self.env.DAPR_APP_ID, "route": "/subscription", "pubsubname": self.env.PUB_SUB }

    def register(self) -> Tuple[str, str]:
        cur = self.conn.cursor()
        cur.execute("""
            insert into workers (tag)
            values ($1)
            on conflict (tag) do update set tag = EXCLUDED.tag
            returning id, tag
        """, [self.env.DAPR_APP_ID + self.env.WORKER_SUFFIX])
        (_id, tag) = cur.fetchone()
        cur.execute("""
            insert into worker_connections (worker_id, task_distributor_id)
            values ($1, $2)
            on conflict do nothing
        """, [_id, self.env.TASK_DISTRIBUTOR_ID])
        self.conn.commit()
        cur.close()
        return (_id, self.env.TASK_DISTRIBUTOR_ID)


    def setup(self) -> WorkerSpec:
        """
            - Wait until DAPR port is available
            - Register the worker
            Returns spec, which can be passed to worker
        """
        wait_for_port(self.env.DAPR_HTTP_PORT)
        (_id, distributor) = self.register()
        return (self.conn, _id, distributor)




