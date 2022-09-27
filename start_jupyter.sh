#!/bin/bash
jupyter notebook --port=9999 --ip 0.0.0.0 --no-browser --allow-root --config './jupyter_notebook_config.json'
