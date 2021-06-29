import uuid
from typing import Union
from pydantic import BaseModel


class Environment(BaseModel):
    # Dapr spect
    DAPR_HTTP_PORT: int
    DAPR_APP_ID: str
    PUB_SUB: str
    # Where /pending requests get made
    SCHEDULER_PUB_SUB: str
    # Dapr related properties
    # Whether we should wait for DAPR server to be active before loading
    NO_WAIT: bool = False
    NO_PUBLISH: bool = False

    LOG_LEVEL: Union[str, int] = "DEBUG"
    # Postgres connection details
    POSTGRES_URL: str
    POSTGRES_SCHEMA: str
    # Utilised for healthchecks and identifying the pod
    SERVICE_ID: str = str(uuid.uuid4())


class TaskBodyData(BaseModel):
    id: str


class TaskBody(BaseModel):
    id: str
    data: TaskBodyData


__all__ = ["Environment", "TaskBodyData", "TaskBody"]
