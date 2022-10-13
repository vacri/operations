#!/bin/bash
# because I can't be bothered typing it every time...
if [ -z "$1" ]; then
    echo "usage: $0 DOCKER_CONTAINER_ID"
    echo "  gets you a root bash shell in the container (if it has /bin/bash)"
    echo "'docker' 'exec' '-ti' '-u root' ID /bin/bash"
    exit 0
fi

docker exec -ti -u root $@ /bin/sh
