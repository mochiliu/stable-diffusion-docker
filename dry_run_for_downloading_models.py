import sys
sys.path.append('/workspace/stable-diffusion')

from omegaconf import OmegaConf
from ldm.util import instantiate_from_config

config = OmegaConf.load('/workspace/stable-diffusion/configs/stable-diffusion/v1-inference.yaml')
model = instantiate_from_config(config.model)
