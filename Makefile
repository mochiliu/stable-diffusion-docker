PHONY: build start help
.DEFAULT_GOAL:= help
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

help:  ## describe make commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build:  ## build image
	@docker build -t dream-booth .

start:  ## start containerized gpu research
	@docker run --rm --gpus 'device=0' -p 9999:9999 -v $(ROOT_DIR)/:/workspace/mnt/ -it dream-booth
