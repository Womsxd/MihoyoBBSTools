#!/bin/bash
docker_name="mihoyo-bbs"
docker restart ${docker_name}
docker logs -f ${docker_name}