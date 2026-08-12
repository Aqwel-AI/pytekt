import time

class RuntimeTracker:
    def __init__(self):
        self.requests = []

    def start(self):
        return time.time()

    def end(self, start_time):
        duration = time.time() - start_time
        self.requests.append(duration)

    def stats(self):
        if not self.requests:
            return {"avg": 0, "count": 0}

        return {
            "avg": sum(self.requests) / len(self.requests),
            "count": len(self.requests),
            "max": max(self.requests)
        }

tracker = RuntimeTracker()