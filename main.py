#!/usr/bin/env python

import platform
import socket
import time
import subprocess
import json
import sys
import getopt



DELAY = 15  # secs
previous_cpu = {}
previous_system_cpu = {}
cpu_usage_percent = 0.0


def send_msg(message, CARBON_SERVER, CARBON_PORT):
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
        lines_temp = [
            'test.docker.server.%s.number-of-dockers %d %d' % (HOSTNAME, number_of_docker, timestamp),
            'test.docker.server.%s.%s.memory-usage %d %d' % (HOSTNAME, instance, memory_usage, timestamp),
            'test.docker.server.%s.%s.memory-limit %d %d' % (HOSTNAME, instance, memory_limit, timestamp),
            'test.docker.server.%s.%s.memory-usage-percent %f %d' % (HOSTNAME, instance, memory_percent, timestamp),
            'test.docker.server.%s.%s.cpu-usage-percent %f %d' % (HOSTNAME, instance, cpu_usage_percent, timestamp),
            'test.docker.server.%s.%s.network-rx-bytes %d %d' % (HOSTNAME, instance, network_rx, timestamp),
            'test.docker.server.%s.%s.network-tx-bytes %d %d' % (HOSTNAME, instance, network_tx, timestamp),
            'test.docker.server.%s.%s.blkio_stats %d %d' % (HOSTNAME, instance, blkio_stats, timestamp)
            ]
        lines.extend(lines_temp)

    return lines

def main(argv):
   CARBON_SERVER = 'localhost'
   CARBON_PORT = 2003
   try:
      opts, args = getopt.getopt(argv,"hs:p:",["c_server=","c_port="])
   except getopt.GetoptError:
      print 'main.py -s <graphite server> -p <carbon port>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'main.py -s <graphite server> -p <carbon port>'
         sys.exit()
      elif opt in ("-s", "--c_server"):
         CARBON_SERVER = arg
      elif opt in ("-p", "--c_port"):
         CARBON_PORT = int(arg)

   while True:
        lines = get_dockerdata()
        message = '\n'.join(lines) + '\n'
        send_msg(message, CARBON_SERVER, CARBON_PORT)   
        time.sleep(DELAY)



    


if __name__ == '__main__':
    main(sys.argv[1:])
    
