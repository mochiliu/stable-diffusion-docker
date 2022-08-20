PHONY: build start help
.DEFAULT_GOAL:= help

help:  ## describe make commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build:  ## build image
	@docker build -t stable-diffusion .

start:  ## start containerized gpu research
	@docker run --rm --gpus 'device=1' -p 8888:8888 -v /home/mochi/github/stable-diffusion-docker/:/workspace/ -it stable-diffusion
