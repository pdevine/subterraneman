FROM ubuntu:12.04
MAINTAINER pdevine
RUN apt-get update
RUN apt-get build-dep -y python-pygame
RUN apt-get install -y python-pygame

RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    chown ${uid}:${gid} -R /home/developer

COPY run_game.py subterraneman/run_game.py
COPY data/* subterraneman/data/
COPY lib/*.py subterraneman/lib/
COPY levels/* subterraneman/levels/

USER developer
ENV HOME /home/developer

CMD cd /subterraneman && python run_game.py
