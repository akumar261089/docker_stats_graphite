# docker_stats_graphite
Python Script to monitor Docker stats on Graphite server

Data recieved from docker stats API is pushed to carbon server.


Start Command:

main.py -s "graphite server" -p "carbon port" -e "prefix"

-default values
 carbon_server = 'localhost'
 carbon_port = 2003

Option '-h' for help

