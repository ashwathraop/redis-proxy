.PHONY: all test 

all: build

.DEFAULT_GOAL := build

build: ## Build the container images. 
	docker-compose build

run: ## Run containers.
	docker-compose up -d

stop: ## Stop docker containers.
	docker-compose down -v

test: ## Run Tests. Runs within docker containers.
	docker-compose run server sh runtest.sh
	docker-compose down
