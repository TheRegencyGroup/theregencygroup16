#!/bin/sh
docker-compose up --exit-code-from web-ci-test --abort-on-container-exit web-ci-test
docker-compose down -v
