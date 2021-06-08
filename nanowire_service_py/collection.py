import os
import psutil
import threading
from queue import Queue
import time
from typing import Any


class UsageCollection:
    cpus_queue: Any
    mem_queue: Any

    def __init__(self):
        # CPUs are collected in % usage
        self.cpus_queue = Queue()
        # memory queue is in MB
        self.mem_queue = Queue()
        self.running = False

    def collection_thread(self):

        self.running = True
        while self.running:
            self.cpus_queue.put_nowait(psutil.cpu_percent())
            self.mem_queue.put_nowait(
                psutil.Process(os.getpid()).memory_info().rss / 1e6
            )
            time.sleep(0.01)

    def finish_collection(self):
        self.running = False

        cpus = []
        mems = []
        while True:
            try:
                cpus.append(self.cpus_queue.get_nowait())
                mems.append(self.mem_queue.get_nowait())
            except:
                break
        if len(mems) > 0:
            max_mem = max(mems)
            max_cpu = max(cpus)
        else:
            max_mem = psutil.Process(os.getpid()).memory_info().rss / 1e6
            max_cpu = psutil.cpu_percent()

        return [max_mem, max_cpu]

    def start_collection(self):
        threading.Thread(target=self.collection_thread).start()


__all__ = ["UsageCollection"]
