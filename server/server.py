#!/usr/bin/env python3
"""Runs a webserver that serves the ping matrix API and UI"""
import http.server
import json
import socketserver
import pathlib
import os

PORT = 8000


pings = [
    {"src": "baldi", "dst": "westin", "latency_ms": 12},
    {"src": "baldi", "dst": "gold", "latency_ms": 9},
    {"src": "westin", "dst": "baldi", "latency_ms": 11},
    {"src": "gold", "dst": "baldi", "latency_ms": 8},
]


class PingMatrixHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Implements the /pings API and returns files from the ui directory when the path does not match an API endpoint."""

    def do_GET(self):
        if self.path == "/pings":
            # TODO: handle POST
            return self.list_pings()
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def list_pings(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(pings), "utf8"))
        return


def serve():
    with socketserver.TCPServer(("", PORT), PingMatrixHttpRequestHandler) as httpd:
        print("Server started at localhost:" + str(PORT))
        httpd.serve_forever()


if __name__ == "__main__":
    # TODO: parse command line args
    os.chdir(os.path.join(pathlib.Path(__file__).parent.absolute(), "ui"))
    serve()
