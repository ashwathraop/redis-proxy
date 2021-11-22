.PHONY: help

help: ## Display help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

build: ## Build the container images. 
	docker-compose build

run: ## Run containers.
	docker-compose up -d

stop: ## Stop docker containers.
	docker-compose down -v

test: ## Run Tests. Runs within docker containers.
	docker-compose run server sh runtest.sh
	docker-compose down
