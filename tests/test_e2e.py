from os import CLD_EXITED
import pytest


from pytest_mock import MockerFixture
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from nanowire_service_py import create, BaseHandler, RuntimeError

service_id = "my_service"
heartbeat = 1
mock_env = {
    "DAPR_HTTP_PORT": "4040",
    "DAPR_APP_ID": "mock",
    "PUB_SUB": "mock-sub",
    "NO_WAIT": "True",
    "LOG_LEVEL": "DEBUG",
    "POSTGRES_URL": "mock-url",
    "POSTGRES_SCHEMA": "mock-schema",
    "SCHEDULER_PUB_SUB": "mocked-sub",
    "SERVICE_ID": service_id
}


class MockArguments(BaseModel):
    name: str
    value: str
    size: int


"""
    Users are expected to only use the high level function
    This makes things easier for us as we 
"""


def test_create(mocker: MockerFixture) -> None:
    mock_args = {"name": "mock", "value": "mocked", "size": 0}
    mock_meta = {"name": "mocked-name"}
    mock_output = {"mock": True}
    worker_id = "mock-id"
    task_ids = {k: k for k in ["validation", "runtime", "exception", "ok"]}

    base_checks = {
        "conn_created": False,
        "worker_created": False,
        "config_retrieved": False,
        "published_pending": False,
    }
    # Validate all tasks went through
    task_checks = {k: False for k in task_ids.keys()}
    checks = {**base_checks, **task_checks}

    class MockHandler(BaseHandler):
        def validate_args(self, args: Any, task_id: str) -> MockArguments:
            copy = args.copy()
            if task_id == task_ids["validation"]:
                # Mess with arguments on purpose
                copy["size"] = "test"
                checks["valitation"] = True
            return MockArguments(**copy)

        def handle_body(
            self, args: Any, meta: Any, task_id: str
        ) -> Tuple[Dict[str, Any], Any]:
            assert isinstance(args, MockArguments)
            assert meta == mock_meta

            if task_id == task_ids["runtime"]:
                raise RuntimeError("Failed", {})
            if task_id == task_ids["exception"]:
                checks[task_id] = True
                raise Exception("Failed")

            return (mock_output, meta)

    class MockCursor:
        last_request: Optional[str]

        def __init__(self) -> None:
            self.last_request = None

        def execute(self, query: Any, args: List[Any] = None) -> None:
            if "insert into workers (tag, name)" in query:
                assert args == [mock_env["DAPR_APP_ID"], mock_env["SERVICE_ID"]]
                checks["worker_created"] = True
            elif "select value from configuration" in query:
                checks["config_retrieved"] = True
                self.last_request = "config"
            elif "fail_task" in query:
                # task_id is passed as 0
                checks[args[0]] = True
            elif "finish_task" in query:
                checks[task_ids["ok"]] = True

        def fetchone(self):
            if self.last_request == "config":
                self.last_request = None
                return (str(heartbeat))
            return (mock_args, mock_meta)

        def close(self) -> None:
            pass

    class MockedConn:
        def __init__(self, url: str, options: str) -> None:
            assert url == mock_env["POSTGRES_URL"]
            assert options == "-c search_path={}".format(
                mock_env["POSTGRES_SCHEMA"]
            )
            checks["conn_created"] = True

        def cursor(self) -> MockCursor:
            return MockCursor()

        def commit(self) -> None:
            pass

    def mocked_request(endpoint: str, json: Dict[str, str]) -> None:
        assert endpoint == "http://localhost:{}/v1.0/publish/{}/pending".format(
            mock_env["DAPR_HTTP_PORT"], mock_env["SCHEDULER_PUB_SUB"]
        )
        assert json["id"] in task_ids
        checks["published_pending"] = True

    # Prepare mocks
    mocker.patch("psycopg2.connect", new=MockedConn)
    mocker.patch("requests.post", new=mocked_request)

    executor = create(mock_env, MockHandler)
    assert executor.subscriptions == [
        {
            "topic": mock_env["DAPR_APP_ID"],
            "route": "/subscription",
            "pubsubname": mock_env["PUB_SUB"],
        }
    ]

    assert executor.handle_request(task_ids["validation"]) == 200
    assert executor.handle_request(task_ids["runtime"]) == 200
    assert executor.handle_request(task_ids["exception"]) == 500
    assert executor.handle_request(task_ids["ok"]) == 200

    # executor.handle_request(TASK_ID)

    assert checks == {k: True for k in checks.keys()}
