FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime

# Instal basic utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends nano tmux git wget unzip bzip2 sudo ca-certificates && \
    apt-get install -y ffmpeg libsm6 libxext6 imagemagick && \
    apt-get clean

COPY ./requirements.txt /requirements.txt

RUN python -m pip install -r /requirements.txt

#RUN git clone https://github.com/openai/CLIP
## RUN git clone https://github.com/facebookresearch/SLIP.git
#RUN git clone https://github.com/crowsonkb/guided-diffusion
#RUN git clone https://github.com/assafshocher/ResizeRight.git
#RUN git clone https://github.com/CompVis/latent-diffusion.git
#RUN git clone https://github.com/CompVis/taming-transformers
#RUN python -m pip install -e /CLIP
#RUN python -m pip install -e /guided-diffusion
#RUN python -m pip install -e ./taming-transformers
