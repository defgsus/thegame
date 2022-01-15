import threading
import queue
import time
from typing import Callable, Optional, Any, Tuple, Dict


class Worker:

    _instances = dict()

    VERBOSE = False

    @classmethod
    def instance(cls, id: str) -> "Worker":
        if id not in cls._instances:
            worker = Worker(id)
            worker.start()
            cls._instances[id] = worker
        return cls._instances[id]

    @classmethod
    def stop_all(cls):
        for worker in cls._instances.values():
            worker.stop()

    def __init__(self, id: str):
        self.id = id
        self._queue = queue.Queue()
        self._results = dict()
        self._thread: Optional[threading.Thread] = None
        self._stop = False

    def __del__(self):
        if self.is_running:
            self.stop()

    def log(self, *args):
        if self.VERBOSE:
            print(f"Worker {self.id}: {threading.current_thread().name}:", *args)

    @property
    def is_running(self):
        return self._thread and self._thread.is_alive()

    def start(self):
        self.log("start")
        if self._thread is not None:
            raise RuntimeError(f"Worker already started")
        self._thread = threading.Thread(target=self._thread_loop)
        self._stop = False
        self._thread.start()

    def stop(self):
        self.log("stop")
        if self.is_running:
            self._queue.put_nowait("STOP")
            self._stop = True
            self._thread.join()

        self._thread = None

    def request(self, id: str, func: Callable, extra: Optional[Any] = None):
        self.log("request", id, func)
        self._queue.put_nowait((id, func, extra))

    def pop_result(self, id: str) -> Optional[Dict[str, Any]]:
        if id in self._results:
            self.log("pop result", id)
            result = self._results.pop(id)
            return {
                "result": result[0],
                "extra": result[1],
            }
        return None

    def _thread_loop(self):
        threading.current_thread().name = f"{self.id}-thread"
        while not self._stop:
            try:
                self.log("wait for work")
                work = self._queue.get(True, timeout=10)
                if work == "STOP":
                    break
            except queue.Empty:
                continue

            self.log("working", work[0])
            self._results[work[0]] = (work[1](), work[2])
            self.log("finished", work[0])
