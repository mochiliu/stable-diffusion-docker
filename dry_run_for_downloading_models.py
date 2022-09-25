import sys
sys.path.extend([
    '/workspace/stable-diffusion',
    '/workspace/stable-diffusion/pytorch3d-lite',
    '/workspace/stable-diffusion/AdaBins',
    '/workspace/stable-diffusion/MiDaS',
])

from omegaconf import OmegaConf
from ldm.util import instantiate_from_config

config = OmegaConf.load('/workspace/stable-diffusion/configs/stable-diffusion/v1-inference.yaml')
model = instantiate_from_config(config.model)

import whisper
model = whisper.load_model("medium.en")
