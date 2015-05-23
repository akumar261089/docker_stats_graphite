# docker_stats_graphite
Python Script to monitor Docker stats on Graphite server

Data recieved from docker stats API is pushed to carbon server.


Start Command:

main.py -carbon_server <graphite server> -carbon_port <carbon port>

-default values
 carbon_server = 'localhost'
 carbon_port = 2003

Option '-h' for help

