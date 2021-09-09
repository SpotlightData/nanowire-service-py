import json
from nanowire_service_py import Logger, ServiceClient, Worker, PluginOutput  # type: ignore

with open("./data/task.json") as f:
    task = json.loads(f.read())


class MockService(ServiceClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.data = []

    def publish(self, endpoint, data):
        self.data.append((endpoint, data))


class MockWorker(Worker):
    def execute(self, task):
        return PluginOutput()


class MockFailedWorker(Worker):
    def execute(self, task):
        raise Exception("test")


def test_success():
    log = Logger()
    worker = MockWorker(log)
    env = {
        "DAPR_APP_ID": "",
        "PUB_SUB": "",
        "OUTPUT_PUB_SUB": "",
        "PYTHON_ENV": "development",
    }
    client = MockService(env, log, worker)
    client.handle_request(task)
    called = [e[0] for e in client.data]
    assert called == ["finished", "logs"]


def test_failure():
    log = Logger()
    worker = MockFailedWorker(log)
    env = {
        "DAPR_APP_ID": "",
        "PUB_SUB": "",
        "OUTPUT_PUB_SUB": "",
        "PYTHON_ENV": "development",
    }
    client = MockService(env, log, worker)
    client.handle_request(task)
    called = [e[0] for e in client.data]
    assert called == ["failed", "logs"]
