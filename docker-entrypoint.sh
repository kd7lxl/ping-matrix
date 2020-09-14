#!/bin/sh

mkdir -p /tmp/.ssh
cp -R /tmp/.ssh /root/.ssh
chmod 700 /root/.ssh
chmod 644 /root/.ssh/id_dsa.pub
chmod 600 /root/.ssh/id_dsa
chmod 644 /root/.ssh/id_rsa.pub
chmod 600 /root/.ssh/id_rsa
touch /root/.ssh/known_hosts

exec "$@"
