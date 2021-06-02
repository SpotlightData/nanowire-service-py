import time
import socket
import pandas as pd
import io
import requests
from contextlib import contextmanager
from typing import Any

def wait_for_port(port: int, host: str ='localhost', wait_time: float=1.0, timeout: float=20.0) -> None:
    """Wait until a port starts accepting TCP connections.
    Args:
        port (int): Port number.
        host (str): Host address on which the port should exist.
        timeout (float): In seconds. How long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(wait_time)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
                                   'connections.'.format(port, host)) from ex

@contextmanager
def with_dataframe(url: str) -> Any:
    response = requests.get(url).content
    df = pd.read_csv(io.StringIO(response.decode('utf-8')))
    try:
        yield df
    finally:
        df.iloc[0:0]

__all__ = ["wait_for_port", "with_dataframe"]
