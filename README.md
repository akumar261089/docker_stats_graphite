# docker_stats_graphite
Python Script to monitor Docker stats on Graphite server

Data recieved from docker stats API is pushed to carbon server.


Start Command:

main.py  -s Graphite_SERVER -p GRAPHITE_PORT -e PREFIX -n HOSTNAME


-default values

** carbon_server = 'localhost'**
** carbon_port = 2003**
** HOSTNAME = localhost**
** PREFIX = dummy**

** Option '-h' for help **

