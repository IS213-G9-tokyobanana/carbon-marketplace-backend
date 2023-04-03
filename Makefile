.PHONY: clean-pyc

help:
	@echo "    init"
	@echo "        Initializes project requirements"
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    dev"
	@echo "        Runs application in Docker and execs into shell within container in dev mode."
	@echo "    stop"
	@echo "        Stops application in dev mode"
	@echo "    prune-all"
	@echo "        Prunes all docker containers, images, volumes, and networks"

init:
	@./scripts/init

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@rm -rf test-results

dev:
	@./scripts/dev

stop:
	@docker-compose -f ./docker-compose.yaml --env-file .env down

prune-all:
	@docker system prune -a --volumes

manifest:
	@./scripts/gen-manifest
