# CER Experiment Template

Run GPU experiments on a remote SLURM cluster from inside a sandboxed container. Submit, monitor, and query results through the CER MCP server — no direct SSH access needed.

## How It Works

```
┌─────────────────────────────────────────────┐
│  Apptainer Container (local)                │
│                                             │
│  Agent ──► ./cer submit <hash>              │
│         ──► ./cer results <job_id>          │
│         ──► edits code + configs/config.yaml│
│                     │                       │
│                     │ localhost:8000         │
└─────────────────────┼───────────────────────┘
                      │
┌─────────────────────┼───────────────────────┐
│  Host               ▼                       │
│              cer-mcp (MCP server)           │
│                     │                       │
│                     │ SSH                    │
│                     ▼                       │
│              SLURM cluster (LUMI)           │
│              └─ Singularity container       │
│              └─ git clone + checkout        │
│              └─ W&B logging                 │
└─────────────────────────────────────────────┘
```

- **Agent** runs inside the container, can only reach the MCP server on localhost
- **MCP server** runs on the host, has SSH access and manages the database
- **Cluster** receives jobs via SSH, runs experiments in Singularity, logs to W&B
- **W&B** stores metrics, configs, and artifact files for reproducibility

## Quick Start

### 1. Build the container

```bash
apptainer build experiment.sif experiment.def
```

### 2. Start the MCP server (on the host)

```bash
cer-mcp
```

### 3. Enter the container

```bash
apptainer exec --nv --bind .:/workspace --pwd /workspace experiment.sif bash
```

### 4. Create a workspace and run an experiment

```bash
./cer workspace create agent-001
cd workspaces/agent-001

# Edit configs/config.yaml (change hyperparameters)
# Edit model.py, train.py (change architecture, training logic)

git add -A && git commit -m "experiment: describe changes"
git push origin agent-001

./cer submit $(git rev-parse HEAD)
./cer status <job_id>
./cer results <job_id>
```

### 5. Reset when done

```bash
cd ../..
./cer workspace reset agent-001
```

## Commands

All commands go through `./cer`, which connects to the MCP server on the host.

### Workspace Management

| Command | Description |
|---------|-------------|
| `./cer workspace create <name>` | Create a workspace (git worktree + branch from main) |
| `./cer workspace list` | List all active workspaces |
| `./cer workspace reset <name>` | Delete local/remote branch and recreate from latest main |

### Experiment Lifecycle

| Command | Description |
|---------|-------------|
| `./cer submit <commit_hash>` | Submit experiment to the cluster |
| `./cer status <job_id>` | Check SLURM job status (returns JSON) |
| `./cer cancel <job_id>` | Cancel a running job |
| `./cer list` | List all tracked experiments |

### Results

| Command | Description |
|---------|-------------|
| `./cer results <job_id>` | W&B summary metrics (JSON) |
| `./cer results <job_id> --history` | Full training history |
| `./cer results <job_id> --history --key train_loss --key val_loss` | Filter specific metrics |

All output is JSON for easy parsing.

## Configuration

### Hydra Config (`configs/config.yaml`)

The agent modifies this file to change experiment hyperparameters:

```yaml
model:
  hidden_dim: 128
  num_layers: 2
  dropout: 0.1
  lr: 1e-3

training:
  max_epochs: 10
  batch_size: 64

save_artifacts:
  - "configs/config.yaml"
  - "model.py"
  - "train.py"
```

- The full Hydra config is automatically logged to W&B on every run
- Files listed in `save_artifacts` are saved as W&B artifacts, preserving them after workspace cleanup

### CER Config (`~/.config/cer/cer.yaml`)

Configured on the host (not inside the container). Controls cluster connection, SLURM settings, and W&B credentials. See `cer.yaml.example` in the CER repo.

## File Structure

```
├── cer                  # CLI client (calls MCP server)
├── configs/
│   └── config.yaml      # Hydra config (agent edits this)
├── experiment.def       # Singularity container definition
├── model.py             # Model code (agent edits this)
├── train.py             # Training script (Hydra + W&B)
├── run.sh               # Entrypoint called by CER on the cluster
├── requirements.txt     # Extra pip deps (installed at runtime)
└── workspaces/          # Agent worktrees (gitignored)
    ├── agent-001/
    ├── agent-002/
    └── ...
```

## Agent Workflow

A typical autoresearch loop:

1. **Create workspace**: `./cer workspace create agent-001`
2. **Edit code**: modify `configs/config.yaml`, `model.py`, `train.py`
3. **Commit & push**: `git add -A && git commit -m "..." && git push origin agent-001`
4. **Submit**: `./cer submit $(git rev-parse HEAD)`
5. **Wait & check**: `./cer status <job_id>` (repeat until COMPLETED)
6. **Analyze**: `./cer results <job_id> --history` — parse JSON, decide next step
7. **Iterate**: go back to step 2 with new changes based on results
8. **Reset**: `./cer workspace reset agent-001` when starting a new experiment line

Multiple agents can run this loop in parallel, each in their own workspace.

## Environment Variables

Set automatically by CER in every cluster job:

| Variable | Description |
|----------|-------------|
| `CER_COMMIT` | Full git commit hash |
| `WANDB_PROJECT` | W&B project name |
| `WANDB_RUN_NAME` | `cer-<commit_short>` |
| `WANDB_TAGS` | Commit hash (used to find the run via `./cer results`) |
| `WANDB_API_KEY` | W&B API key |

## Training Script Integration

Your training script must include W&B logging and artifact saving for CER to track results. Here are the required snippets:

### 1. Imports and Hydra entry point

```python
import hydra
import wandb
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    ...
```

### 2. Initialize W&B

Call this at the start of training. CER sets `WANDB_PROJECT`, `WANDB_RUN_NAME`, `WANDB_TAGS`, and `WANDB_API_KEY` as environment variables — `wandb.init` picks them up automatically. Pass the full Hydra config so every hyperparameter is logged:

```python
wandb.init(
    project=cfg.wandb.project,
    entity=cfg.wandb.entity,
    config=OmegaConf.to_container(cfg, resolve=True),
)
```

### 3. Log metrics

Log metrics with `wandb.log()` during training. Use `/` to group them (e.g. `train/loss`, `val/acc`). These are what `./cer results` returns:

```python
wandb.log({
    "epoch": epoch,
    "train/loss": train_loss,
    "val/loss": val_loss,
    "val/acc": val_acc,
})
```

### 4. Save artifacts

Files listed in `save_artifacts` in `configs/config.yaml` are saved as W&B artifacts. This preserves your code and config after the workspace is cleaned up:

```python
if "save_artifacts" in cfg:
    artifact = wandb.Artifact(f"experiment-{wandb.run.id}", type="code")
    for path in cfg.save_artifacts:
        try:
            artifact.add_file(path)
        except Exception as e:
            print(f"Warning: could not save {path}: {e}")
    wandb.log_artifact(artifact)
```

Add any files you want preserved to `save_artifacts` in the config:

```yaml
save_artifacts:
  - "configs/config.yaml"
  - "model.py"
  - "train.py"
```

### 5. Finish W&B

Always call `wandb.finish()` at the end so the run is marked complete:

```python
wandb.finish()
```

### Minimal complete example

```python
import hydra
import wandb
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    wandb.init(
        project=cfg.wandb.project,
        entity=cfg.wandb.entity,
        config=OmegaConf.to_container(cfg, resolve=True),
    )

    for epoch in range(cfg.training.max_epochs):
        train_loss, val_loss = your_training_step(epoch)
        wandb.log({"epoch": epoch, "train/loss": train_loss, "val/loss": val_loss})

    # Save code as W&B artifact
    if "save_artifacts" in cfg:
        artifact = wandb.Artifact(f"experiment-{wandb.run.id}", type="code")
        for path in cfg.save_artifacts:
            try:
                artifact.add_file(path)
            except Exception as e:
                print(f"Warning: could not save {path}: {e}")
        wandb.log_artifact(artifact)

    wandb.finish()

if __name__ == "__main__":
    main()
```

## Rebuilding the Container

Only rebuild when `experiment.def` changes (new system packages or pip deps). Code changes are picked up automatically via the bind-mounted workspace.

```bash
apptainer build --force experiment.sif experiment.def
```

On the cluster, CER auto-rebuilds the container when it detects `experiment.def` has changed (via md5 checksum).
