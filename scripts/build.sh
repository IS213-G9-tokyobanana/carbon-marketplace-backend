#!/bin/bash

cd go-app

aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 424432388155.dkr.ecr.ap-southeast-1.amazonaws.com
docker build -t go-app --platform linux/amd64 .
docker tag go-app:latest 424432388155.dkr.ecr.ap-southeast-1.amazonaws.com/go-app:latest
docker push 424432388155.dkr.ecr.ap-southeast-1.amazonaws.com/go-app:latest
