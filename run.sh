#!/bin/bash
# Experiment entrypoint — called by CER inside the Singularity container.
#
# Environment variables set by CER:
#   CER_COMMIT      - full git commit hash
#   WANDB_PROJECT   - W&B project name (from cer.yaml)
#   WANDB_RUN_NAME  - cer-<commit_short>
#   WANDB_TAGS      - commit hash (for querying via `cer results`)

set -euo pipefail

# Install Python dependencies not baked into the container
pip install -q -r requirements.txt 2>/dev/null || true

python train.py
