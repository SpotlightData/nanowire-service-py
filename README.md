# nanowire-service-py

<div align="center">

[![Build status](https://github.com/SpotlightData/nanowire-service-py/workflows/build/badge.svg?branch=master&event=push)](https://github.com/SpotlightData/nanowire-service-py/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/nanowire-service-py.svg)](https://pypi.org/project/nanowire-service-py/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/SpotlightData/nanowire-service-py/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/SpotlightData/nanowire-service-py/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/SpotlightData/nanowire-service-py/releases)
[![License](https://img.shields.io/github/license/SpotlightData/nanowire-service-py)](https://github.com/SpotlightData/nanowire-service-py/blob/master/LICENSE)

Wrapper for interacting with Nanowire platform

</div>

## Usage

Install the library via `pip install nanowire-service-py`, or by adding it to requirements file and running `pip install -r requirements.txt`

This library is designed for tight integration with Nanowire platform (created by Spotlight Data).

The library does not have a hardcode requirement for a specific web server, so a another framework like django or flask could be utilised, however, I'd recommend using [fastapi](https://fastapi.tiangolo.com/) due to it's simplicity and speed

### Environment

The following environment variables need to be supplied:

```python
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
    # Whether the service should publish to schduler
    # This shouldn't be done if we have an "executor" worker
    NO_PUBLISH: bool = False

    LOG_LEVEL: Union[str, int] = "DEBUG"
    # Postgres connection details
    POSTGRES_URL: str
    POSTGRES_SCHEMA: str
    # Utilised for healthchecks and identifying the pod
    SERVICE_ID: str = str(uuid.uuid4())
```

This will be verified on service startup.

### Entrypoint

The primary code logic should be placed in a sub-class of `BaseHandler`. User is expected to implement `validate_args` as well as `handle_body` methods:

```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Response

from pydantic import BaseModel, validator
from typing import Any, List, Optional

import pandas as pd

from nanowire_service_py import BaseHandler, create, TaskBody
from toolbox import ClusterTool

load_dotenv()

allowed_methods = ["HDBSCAN", "DBSCAN"]
# pydantic used to verify function body
class Arguments(BaseModel):
    contentUrl: str
    textCol: str
    indexCol: str
    clusterSize: float = 0.2
    nLabels: int = 10
    method: str = "DBSCAN"
    customStops: Optional[List[str]] = []
    maxVocab: int = 5000
    memSave: bool = False
    withAnomalous: bool = False

    @validator('method')
    def method_check(cls, method):
        if method not in allowed_methods:
            raise ValueError("Method has to be one of: {}, received: {}".format(",".join(allowed_methods), method))
        return method

# Our custom handler
class MyHandler(BaseHandler):
    def __init__(self, *args):
        super().__init__(*args)
        self.cluster_tool = ClusterTool(self.logger)

    def validate_args(self, args: Any, task_id: str) -> Arguments:
        return Arguments(**args)

    def handle_body(self, args: Arguments, meta: Any, task_id: str):
        df = pd.read_csv(args.contentUrl, dtype='unicode')

        if args.textCol not in df.columns:
            raise RuntimeError("Could not find text column '{}' in CSV".format(args.textCol), { "origin": "CSV"})

        if args.indexCol not in df.columns:
            raise RuntimeError("Could not find index column '{}' in CSV".format(args.indexCol), { "origin": "CSV"})

        result = self.cluster_tool.main(df, args)
        return (result, meta)

# Always handled by the library, pass environment directly
executor = create(os.environ, MyHandler)

app = FastAPI()

# Let's DAPR know which topics should be subscribed to
@app.get("/dapr/subscribe")
def subscribe():
    return executor.subscriptions

# Primary endpoint, where request will be delivered to
# TaskBody type here verifies the post body
@app.post("/subscription")
def subscription(body: TaskBody, response: Response):
    status = executor.handle_request(body.data.id)
    response.status_code = status
    # Return empty body so dapr doesn't freak out
    return {}

# Start heartbeat thread, which will periodically send updates to database
executor.heartbeat()
```

Assuming the filename is `main.py` the server can then be started via `uvicorn main:app`

### Handling failure

The primary validation happens within `validate_args` function by `pydantic` models. This is where anything related to input should be checked.

If at any point you want the current task to fail, raise `RuntimeError`. This will indicate the library, that we should fail and not retry again. For example:

- CSV missing columns or having incorrect text format
- Not enough data passed

Anything else that raises unexpected exception should be retried automatically.

## Versioning

Versioning is based on [semver](https://semver.org/), however, it primarily applies to the `create` function exposed by the package.
If you're using any of the internal system parts, make sure to validate before updating the version.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md)

## 🛡 License

[![License](https://img.shields.io/github/license/SpotlightData/nanowire-service-py)](https://github.com/SpotlightData/nanowire-service-py/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/SpotlightData/nanowire-service-py/blob/master/LICENSE) for more details.

## Credits

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template).
