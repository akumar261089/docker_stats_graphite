#!/usr/bin/env python

import platform
import socket
import time
import subprocess
import json

CARBON_SERVER = '52.64.105.167'
CARBON_PORT = 2003
DELAY = 15  # secs
previous_cpu = {}
previous_system_cpu = {}
cpu_usage_percent = 0.0


def send_msg(message):
    print 'sending message:\n%s' % message
    sock = socket.socket()
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    sock.close()



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
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
        stat_data[instance] = json.loads(out)
        memory_limit = float(stat_data[instance]["memory_stats"]["limit"])
        memory_usage = float(stat_data[instance]["memory_stats"]["usage"])
        memory_percent = (memory_usage / memory_limit)*100.0
        if not(instance in previous_cpu):
            cpu_usage_percent = 0.0
        else:
            cpu_delta = float( stat_data[instance]["cpu_stats"]["cpu_usage"]["total_usage"] - previous_cpu[instance])
            system_delta = float(stat_data[instance]["cpu_stats"]["system_cpu_usage"] - previous_system_cpu[instance])
            cpu_usage_percent = float(cpu_delta / system_delta) * float(len(stat_data[instance]["cpu_stats"]["cpu_usage"]["percpu_usage"])) * 100.0

        network_rx = float(stat_data[instance]["network"]["rx_bytes"])
        network_tx = float(stat_data[instance]["network"]["tx_bytes"])
        blkio_stats = stat_data[instance]["blkio_stats"]["io_serviced_recursive"][0]["value"]
        previous_cpu[instance] = float(stat_data[instance]["cpu_stats"]["cpu_usage"]["total_usage"])
        previous_system_cpu[instance] = float(stat_data[instance]["cpu_stats"]["system_cpu_usage"])
        lines = [
            'rocket.test.docker.server.%s.%s.memory-usage %d %d' % (HOSTNAME, instance, memory_usage, timestamp),
            'rocket.test.docker.server.%s.%s.memory-limit %d %d' % (HOSTNAME, instance, memory_limit, timestamp),
            'rocket.test.docker.server.%s.%s.memory-usage-percent %f %d' % (HOSTNAME, instance, memory_percent, timestamp),
            'rocket.test.docker.server.%s.%s.cpu-usage-percent %f %d' % (HOSTNAME, instance, cpu_usage_percent, timestamp),
            'rocket.test.docker.server.%s.%s.network-rx-bytes %d %d' % (HOSTNAME, instance, network_rx, timestamp),
            'rocket.test.docker.server.%s.%s.network-tx-bytes %d %d' % (HOSTNAME, instance, network_tx, timestamp),
            'rocket.test.docker.server.%s.%s.blkio_stats %d %d' % (HOSTNAME, instance, blkio_stats, timestamp)
            ]
        message = '\n'.join(lines) + '\n'
        send_msg(message)


if __name__ == '__main__':


    while True:
        get_dockerdata()
        time.sleep(DELAY)
