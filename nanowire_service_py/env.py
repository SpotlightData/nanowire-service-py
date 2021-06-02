from pydantic import BaseModel

class Environment(BaseModel):
    # Dapr spect
    DAPR_HTTP_PORT: int
    DAPR_APP_ID: str
    PUB_SUB: str
    # Server
    PORT: int = 5000
    # Postgres connection details
    POSTGRES_URL: str
    POSTGRES_SCHEMA: str
    # Might be used in the future, when we want to differentiate
    # between scaled pods
    WORKER_SUFFIX: str = ""
    # TODO: remove in the future
    TASK_DISTRIBUTOR_ID: str = '62eba219-1ef0-4069-affa-86b892d026f8'

__all__ = ["Environment"]
