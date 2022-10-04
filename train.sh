#!/bin/bash
python /workspace/Dreambooth-SD-optimized/main.py --base /worspace/Dreambooth-SD-optimized/configs/stable-diffusion/v1-finetune_unfrozen.yaml -t --actual_resume /workspace/mnt/models/sd-v1-4-full-ema.ckpt -n pontch --gpus 0, --data_root /workspace/mnt/outputs/training_images/ --reg_data_root /workspace/mnt/outputs/regularization_images/samples/ --class_word dog

