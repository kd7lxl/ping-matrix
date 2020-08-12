from dataclasses import dataclass

# TODO: tsdb (or other persistent storage) support


@dataclass
class Ping:
    src: str
    dst: str
    latency_ms: int  # could change this to float if desired


class StorageInterface:
    """defines the interface for implementing storage handlers for the ping server"""

    def list(self) -> list:
        """returns all the latest ping result for each src-dst pair"""
        pass

    def set(self, ping: Ping):
        """stores a ping result"""
        pass


class InMemoryStorage(StorageInterface):
    """a ping storage handler that stores pings in an in-memory dictionary"""

    def __init__(self):
        self.pings = {}

    def list(self):
        return list(self.pings.values())

    def set(self, ping):
        self.pings[ping.src + ping.dst] = ping
