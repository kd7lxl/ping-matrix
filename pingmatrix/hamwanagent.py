#!/usr/bin/env python3
"Iterates over all HamWAN hosts and submits ping stats to the server"
import queue
import requests
import socket
import threading
from time import sleep

from client import PingClient
import mikrotik


class HamWANAgent(object):
    def __init__(self, hosts_url="https://encrypted.hamwan.org/host/ansible.json"):
        self.hosts_url = hosts_url
        self.get_hosts()

    def get_hosts(self):
        r = requests.get(self.hosts_url)
        r.raise_for_status()
        resp = r.json()
        self.hosts = frozenset(resp.get("mikrotik")).intersection(resp.get("HamWAN"))

    def run_once(self, delay=0, threads=30):
        """Pings each host from each host. Returns when complete.

        Connects to `threads` hosts in parallel, but only executes one ping at a time on each source host.
        There is no locking for destinations, so many hosts may be pinging the same host concurrently (TODO potential improvement).
        """
        q = queue.Queue()

        def worker():
            while True:
                src = q.get()
                for dst in self.hosts:
                    if src == dst:
                        continue
                    print("pinging {} -> {}".format(src, dst))
                    try:
                        ping = mikrotik.SSHPingAgent(src).ping(dst)
                    except mikrotik.PingError as err:
                        print("error: {}", err)
                        # TODO: support collecting error messages with server
                        continue
                    except socket.error as err:
                        break
                    print(ping)
                    PingClient().post(ping)
                    sleep(delay)
                q.task_done()

        for _ in range(threads):
            threading.Thread(target=worker, daemon=True).start()
        for src in self.hosts:
            q.put(src)
        q.join()

    def run(self, delay=0):
        while True:
            try:
                self.run_once(delay)
                self.get_hosts()
            except (KeyboardInterrupt, SystemExit):
                return


if __name__ == "__main__":
    HamWANAgent().run_once()
