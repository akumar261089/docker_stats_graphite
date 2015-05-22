#!/usr/bin/env python

import platform
import socket
import time
import subprocess
import json

CARBON_SERVER = 'localhost'
CARBON_PORT = 2003
DELAY = 15  # secs

def get_dockerdata():
    HOSTNAME = socket.gethostname()
    timestamp = int(time.time())
    stat_data = {}   
    lines = []
    dockers = subprocess.Popen("sudo docker ps|grep -v 'NAMES'|awk '{ print $NF }'|tr '\n' ' ' ", shell=True, stdout=subprocess.PIPE).stdout.read()
    dockers_list = dockers.split()
    number_of_docker= len(dockers_list)
    for instance in dockers_list:
        cmd = "echo 'GET /containers/" + instance + "/stats HTTP/1.0\r\n'  | nc -U /var/run/docker.sock | head -5 | tail -1"
        stat_data[instance] = json.loads(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read())
        lines_temp = [
            'rocket.test.docker.server.%s.%s.memory-usage %d %d' % (HOSTNAME, instance, stat_data[instance]["memory_stats"]["usage"], timestamp),
            'rocket.test.docker.server.%s.%s.system-cpu-usage %d %d' % (HOSTNAME, instance, stat_data[instance]["cpu_stats"]["system_cpu_usage"] timestamp),
            'rocket.test.docker.server.%s.%s.network-rx-bytes %d %d' % (HOSTNAME, instance, stat_data[instance]["network"]["rx_bytes"], timestamp),
            'rocket.test.docker.server.%s.%s.network-tx-bytes %d %d' % (HOSTNAME, instance, stat_data[instance]["network"]["tx_bytes"], timestamp),
            'rocket.test.docker.server.%s.%s.blkio_stats %d %d' % (HOSTNAME, instance, stat_data[instance]["blkio_stats"]["io_serviced_recursive"][0]["value"], timestamp),

            ]
        lines.extend(lines_temp)

    return lines


def send_msg(message):
    print 'sending message:\n%s' % message
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    sock.close()


if __name__ == '__main__':
   
   
    while True:
        lines = get_dockerdata()
        message = '\n'.join(lines) + '\n'
        send_msg(message)
        time.sleep(DELAY)