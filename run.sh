#!/bin/bash
# Experiment entrypoint — called by CER with config args.
#
# CER translates:
#   cer submit <commit> --config lr=0.001 --config epochs=10
# into:
#   bash run.sh --lr 0.001 --epochs 10
#
# Environment variables set by CER:
#   CER_COMMIT      - full git commit hash
#   CER_CONFIG      - JSON string of config overrides
#   WANDB_PROJECT   - W&B project name (from cer.yaml)
#   WANDB_RUN_NAME  - cer-<commit_short>
#   WANDB_TAGS      - commit hash (for querying via `cer results`)
#
# Customize this script for your experiment. Examples:
#   python train.py "$@"
#   python -m mypackage.train "$@"
#   bash scripts/preprocess.sh && python train.py "$@"

set -euo pipefail

python train.py "$@"
