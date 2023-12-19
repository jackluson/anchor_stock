#!/bin/sh
docker build --force-rm -t anchor_stock -f Dockerfile .

# docker build --force-rm -t myimage .
# docker rmi $(docker images -a | grep "<none>" | awk '$1=="<none>" {print $3}')
# docker image prune
