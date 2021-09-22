from typing import Any, Dict, Optional, List, Literal, Union
from pydantic import BaseModel, ValidationError


class DaprRequestBody(BaseModel):
    id: str
    data: Any


class Path(BaseModel):
    uuid: str
    instance: str
    parent: Optional[str]
    meta: Dict[str, Any]
    state: Dict[str, Any]
    workflow: str
    branched: bool


class OrderedInstance(BaseModel):
    id: int
    workflow: str
    plugin: str
    default_args: Dict[str, Any]
    meta: Dict[str, Any]
    parent: int


class Task(BaseModel):
    uuid: str
    # args, meta should be implemented by user
    args: Any
    meta: Any
    children: Optional[List[OrderedInstance]] = []
    path: Path
    current: OrderedInstance


class ChildAction(BaseModel):
    parent: int
    child: int
    plugin: str
    args: Any
    meta: Any


class BaseActions(BaseModel):
    child: List[ChildAction] = []


class BranchAction(BaseModel):
    inherit: bool = False
    #
    uuid: str
    meta: Dict[str, Any] = {}
    state: Dict[str, Any] = {}

    actions: BaseActions


class PathUpdate(BaseModel):
    state: Dict[str, Any]
    meta: Dict[str, Any]


class Actions(BaseActions):
    close: bool = False
    branch: List[BranchAction] = []
    path_update: Optional[PathUpdate]


class PluginOutput(BaseModel):
    output: Any
    actions: Actions = Actions()


class TaskOutput(PluginOutput):
    uuid: str
    started: str
    finished: str
    plugin_id: int


class Environment(BaseModel):
    DAPR_APP_ID: str
    PUB_SUB: str
    # Where /finished|failed requests get made
    OUTPUT_PUB_SUB: str
    PYTHON_ENV: Literal["production", "development"] = "production"


class MultiInput(BaseModel):
    id: int
    plugin: str
    value: Any


class GroupedInput(BaseModel):
    plugin: str
    args: Any
    meta: Any


class MultiInputTask(Task):
    args: Dict[str, MultiInput]
    meta: Dict[str, MultiInput]


class MultiOrSingleInputTask(Task):
    args: Union[Dict[str, MultiInput], Dict[str, Any]]
    meta: Union[Dict[str, MultiInput], Dict[str, Any]]
