import http.client
import json

from server import PingEncoder
from storage import Ping

pings = [
    {"src": "baldi", "dst": "westin", "latency_ms": 12},
    {"src": "baldi", "dst": "gold", "latency_ms": 9},
    {"src": "westin", "dst": "baldi", "latency_ms": 11},
    {"src": "gold", "dst": "baldi", "latency_ms": 8},
]


class PingClient(object):
    def __init__(self, address="localhost", port=8000):
        self.address = address
        self.port = port

    def _request(self, method, path="/pings", body=None):
        conn = http.client.HTTPConnection(self.address, self.port)
        conn.request(method, path, body)
        return conn.getresponse()

    def get(self):
        print(self._request("GET").read())

    def post(self, ping: Ping):
        print(self._request("POST", body=json.dumps(ping, cls=PingEncoder)).read())


if __name__ == "__main__":
    PingClient().post(Ping(**pings[0]))
    # PingClient().get()
