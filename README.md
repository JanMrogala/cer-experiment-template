# CER Experiment Template

Template repository for GPU experiments managed by [Cluster Experiment Runner (CER)](https://github.com/JanMrogala/cluster-experiment-runner).

## What's inside

| File | Purpose |
|------|---------|
| `run.sh` | Entrypoint script called by CER. Customize this. |
| `train.py` | Example training script with W&B logging |
| `experiment.def` | Singularity container definition (PyTorch + common ML libs) |
| `requirements.txt` | Extra pip dependencies installed at runtime |

## Setup

### 1. Create your experiment repo from this template

Click **"Use this template"** on GitHub, or:

```bash
gh repo create my-experiment --template JanMrogala/cer-experiment-template --private --clone
```

### 2. Build the container on the cluster (one-time)

```bash
# Copy the def file
scp experiment.def cluster:/path/to/containers/

# Build on cluster (requires proot or fakeroot)
ssh cluster "module load LUMI/23.09 partition/G systools/23.09 && \
    singularity build /path/to/containers/experiment.sif /path/to/containers/experiment.def"
```

Or build locally with [Apptainer](https://apptainer.org/) and upload:

```bash
apptainer build experiment.sif experiment.def
scp experiment.sif cluster:/path/to/containers/
```

### 3. Configure CER

In your CER installation, set `cer.yaml`:

```yaml
cluster:
  repo_url: "git@github.com:you/my-experiment.git"

container:
  image: "/path/to/containers/experiment.sif"

experiment:
  entrypoint: "bash run.sh"
```

### 4. Run experiments

```bash
# Edit code
vim train.py

# Commit and push
git add -A && git commit -m "try higher learning rate"
git push

# Start the MCP server (in a separate terminal)
cer-mcp

# Or use the CLI directly:
cer submit $(git rev-parse HEAD)
cer status <job_id>
cer results <job_id>
cer results <job_id> --history    # full metric history
```

## Customizing

### Different entrypoint

Edit `run.sh` to run whatever you need:

```bash
# Multi-step pipeline
bash scripts/preprocess.sh
python train.py "$@"
python evaluate.py

# Or call a module
python -m mypackage.train "$@"
```

### Additional system dependencies

Edit `experiment.def`, add packages to the `%post` section, and rebuild the container.

### Additional pip dependencies

Add to `requirements.txt` — installed automatically at job start. For faster startup, add frequently-used packages to `experiment.def` instead.

## Environment variables

CER sets these automatically in every job:

| Variable | Value | Example |
|----------|-------|---------|
| `CER_COMMIT` | Full commit hash | `a1b2c3d4e5f6...` |
| `WANDB_PROJECT` | W&B project name | `my-project` |
| `WANDB_RUN_NAME` | Auto-generated run name | `cer-a1b2c3d4` |
| `WANDB_TAGS` | Commit hash (for querying) | `a1b2c3d4e5f6...` |
| `WANDB_API_KEY` | W&B API key | (from cer.yaml) |
