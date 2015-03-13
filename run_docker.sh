#!/bin/bash
docker build -t subterraneman ./

docker run -it -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.Xauthority:/home/developer/.Xauthority -v /dev/snd:/dev/snd --privileged --net=host subterraneman
