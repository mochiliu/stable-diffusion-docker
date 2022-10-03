# stable-diffusion-docker

Repo for playing around with dockerized stable diffusion.
Assumes sd-v1-4.ckpt file is in /models/ directory.
I have two gpus, so you might have to change "device=1" to "device=0" in Makefile, and your own password for the jupyter_notebook_config.json
To use, run:
make build
make start

open up the jupter notebook from link in terminal, and navigate to /mnt/ for the various notebooks.

Notebook adapted from: https://github.com/deforum/stable-diffusion
