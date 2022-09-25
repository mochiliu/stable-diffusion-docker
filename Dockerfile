FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-runtime

# Instal basic utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends nano tmux git wget unzip bzip2 sudo && \
    apt-get install -y libsm6 libxext6 imagemagick && \
    conda install -y -c conda-forge ffmpeg && \
    apt-get clean

COPY ./requirements.txt /requirements.txt
RUN python -m pip install -r /requirements.txt && \
    git clone https://github.com/mochiliu/stable-diffusion && \
    cd stable-diffusion && \
    python -m pip install -e git+https://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers && \
    python -m pip install -e git+https://github.com/openai/CLIP.git@main#egg=clip && \
    git clone https://github.com/crowsonkb/k-diffusion.git src/k-diffusion && \
    python -m pip install src/k-diffusion && \
    git clone https://github.com/shariqfarooq123/AdaBins && \
    git clone https://github.com/isl-org/MiDaS && \
    git clone https://github.com/MSFTserver/pytorch3d-lite && \
    python -m pip install git+https://github.com/openai/whisper.git
COPY ./dry_run_for_downloading_models.py /workspace/stable-diffusion/dry_run_for_downloading_models.py
RUN python /workspace/stable-diffusion/dry_run_for_downloading_models.py
COPY start_jupyter.sh jupyter_notebook_config.json /workspace/
CMD /workspace/start_jupyter.sh
