#!/usr/bin/env python3
"""Runs a webserver that serves the ping matrix API and UI"""
import http.server
from ipaddress import ip_address, ip_network
import json
import socketserver
import pathlib
import os

from storage import InMemoryStorage, Ping, StorageInterface

PORT = 8000


pings = [
    {"src": "baldi", "dst": "westin", "latency_ms": 12},
    {"src": "baldi", "dst": "gold", "latency_ms": 9},
    {"src": "westin", "dst": "baldi", "latency_ms": 11},
    {"src": "gold", "dst": "baldi", "latency_ms": 8},
]


class PingEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Ping):
            return obj.__dict__
        # Base class default() raises TypeError:
        return json.JSONEncoder.default(self, obj)


class AllowSourceAuth(http.server.BaseHTTPRequestHandler):
    """Mixin to add allowlist authorization capablility to an HTTPRequestHandler.
    The handler must call authorize() explicitly -- it does not default to auth on all endpoints!"""

    allowed_sources = [ip_network("127.0.0.0/8")]

    def authorize(self):
        """Simple allowlist authorization"""
        host = ip_address(self.client_address[0])
        for network in self.allowed_sources:
            if host in network:
                return True
        self.send_error(403)
        return

    @classmethod
    def allow_source(cls, network: str):
        """Adds an address/network to the allowlist"""
        cls.allowed_sources.append(ip_network(network))


class PingMatrixHttpRequestHandler(
    http.server.SimpleHTTPRequestHandler, AllowSourceAuth
):
    """Implements the /pings API and serves files from the ui directory when the path does not match an API endpoint."""

    storage_handler = InMemoryStorage()

    def do_GET(self):
        if self.path == "/pings":
            return self.list_pings()
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/pings":
            return self.add_ping()
        self.send_error(501)
        return

    def list_pings(self):
        """Lists all the latest ping results"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            bytes(
                json.dumps({"pings": self.storage_handler.list()}, cls=PingEncoder),
                "utf8",
            )
        )
        return

    def add_ping(self):
        """Stores a ping result from the ping agent"""
        if not self.authorize():
            return
        if self.headers.get("content-type", "application/json") != "application/json":
            self.send_error(400, "only application/json is accepted")
            return
        length = int(self.headers.get("content-length"))
        payload = self.rfile.read(length)
        try:
            ping = Ping(**json.loads(payload))
        except TypeError as err:
            self.send_error(400, explain=str(err))
            return
        self.storage_handler.set(ping)
        self.send_error(201)
        return

    @classmethod
    def register_storage_handler(cls, storage_handler: StorageInterface):
        cls.storage_handler = storage_handler


def serve():
    with socketserver.TCPServer(("", PORT), PingMatrixHttpRequestHandler) as httpd:
        print("Server started at localhost:" + str(PORT))
        httpd.serve_forever()


if __name__ == "__main__":
    # TODO: parse command line args
    os.chdir(os.path.join(pathlib.Path(__file__).parent.absolute(), "ui"))
    serve()
