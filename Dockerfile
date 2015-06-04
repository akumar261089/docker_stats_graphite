# Docker image containing the Diamond collector
#
# VERSION               0.0.1
FROM      ubuntu:14.04
MAINTAINER Abhinav Kumar <akumar261089@gmail.com>

# Install dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y python-setuptools make pbuilder python-mock python-configobj python-support cdbs git python-psutil

RUN git clone https://github.com/docker/docker-py.git

#install docker-py
WORKDIR /docker-py
RUN python setup.py install

ADD main.py /main.py
ADD start.sh /start.sh

#cleanup
RUN apt-get autoremove -y git python-setuptools make pbuilder python-mock && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf  /docker-py

#startup scr


#configure diamond with env
RUN chmod +x /main.py
RUN chmod +x /start.sh

#start
ENTRYPOINT /start.sh
