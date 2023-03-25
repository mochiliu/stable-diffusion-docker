FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-runtime

# Instal basic utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends nano tmux git wget unzip bzip2 sudo && \
    apt-get install -y libsm6 libxext6 imagemagick libsndfile1-dev && \
    conda install -y -c conda-forge x264=='1!161.3030' ffmpeg=4.3.2 && \
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
    python -m pip install -U openai-whisper && \
    python -m pip install pygsheets
COPY ./dry_run_for_downloading_models.py /workspace/stable-diffusion/dry_run_for_downloading_models.py
RUN python /workspace/stable-diffusion/dry_run_for_downloading_models.py
COPY start.sh start_jupyter.sh /workspace/
#CMD ./start.sh
CMD ./start_jupyter.sh
