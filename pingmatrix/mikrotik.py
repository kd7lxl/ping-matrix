import os.path
import sys

from paramiko import MissingHostKeyPolicy, SSHClient

from storage import Ping


def printerr(*args):
    print(*args, file=sys.stderr)


class AllowAnythingPolicy(MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return


class PingError(Exception):
    pass


class SSHPingAgent(object):
    connection_cache = {}

    def __init__(self, hostname, port=222, timeout=10.0):
        self.hostname = hostname
        if not self.connection_cache.get(hostname):
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
            ssh.set_missing_host_key_policy(AllowAnythingPolicy())
            ssh.connect(
                self.hostname,
                port=port,
                username=os.environ.get("SSH_USER"),
                timeout=timeout,
            )
            self.connection_cache[hostname] = ssh
        self.ssh = self.connection_cache[hostname]

    def ping(self, dst, count=8) -> Ping:
        stdin, stdout, stderr = self.ssh.exec_command(
            "/ping {} count={}".format(dst, count)
        )

        output = stdout.read().decode("utf8")
        err = stderr.read().decode("utf8")
        exit_code = stdout.channel.recv_exit_status()

        stdin.close()
        stdout.close()
        stderr.close()

        if exit_code != 0:
            printerr(output)
            printerr(err)
            raise PingError(exit_code)

        fields = self._parse_summary(output)
        printerr(fields)
        return Ping(self.hostname, dst, int(fields.get("avg-rtt", "-1").rstrip("ms")))

    def _parse_summary(self, output) -> dict:
        # Mikrotik ping output will look something like this:
        # SEQ HOST                                     SIZE TTL TIME  STATUS
        # 0 44.24.241.145                              56  60 26ms
        # 1 44.24.241.145                              56  60 17ms
        # 2 44.24.241.145                              56  60 28ms
        # 3 44.24.241.145                              56  60 24ms
        # 4 44.24.241.145                              56  60 24ms
        # 5 44.24.241.145                              56  60 21ms
        # 6 44.24.241.145                              56  60 24ms
        # 7 44.24.241.145                              56  60 27ms
        # sent=8 received=8 packet-loss=0% min-rtt=17ms avg-rtt=23ms max-rtt=28ms
        #
        # second to last line will be the summary, starting with whitespace then "sent="
        summary_line = output.splitlines()[-2]
        try:
            return {k: v for k, v in [x.split("=") for x in summary_line.split()]}
        except ValueError as e:
            printerr(output)
            printerr(e)
            return {}


if __name__ == "__main__":
    ping = SSHPingAgent("r1.baldi.hamwan.net").ping("r1.snodem.hamwan.net", count=1)
    print(ping)
