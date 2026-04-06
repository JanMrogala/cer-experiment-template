#!/bin/bash
# Experiment entrypoint — called by CER inside the Singularity container.
#
# Environment variables set by CER:
#   CER_COMMIT      - full git commit hash
#   WANDB_PROJECT   - W&B project name (from cer.yaml)
#   WANDB_RUN_NAME  - cer-<commit_short>
#   WANDB_TAGS      - commit hash (for querying via `cer results`)
#
# Customize this script for your experiment. Examples:
#   python train.py
#   python -m mypackage.train
#   bash scripts/preprocess.sh && python train.py

set -euo pipefail

python train.py
