# Container Setup

Two containers are involved in the CER pipeline. You run inside one, and your experiments run inside the other.

## Local Container (you are here)

Built from `experiment.def`. This is where you (the agent) run. It's an Apptainer/Singularity container with:

- Python 3 + PyTorch (from NVIDIA base image)
- Standard ML libraries: wandb, pytorch-lightning, hydra-core, scipy, matplotlib
- MCP client (for `./cer` commands)
- Git (for version control)
- No SSH, no internet access (only localhost:8000 for MCP)

The workspace is bind-mounted from the host, so your file edits persist outside the container.

## Cluster Container

The same `experiment.def` is used to build a Singularity container on the LUMI cluster. CER manages this automatically:

- On first submit, the container is built on the cluster
- On subsequent submits, CER checks the md5 checksum of `experiment.def`
- If the checksum changed, it rebuilds (this takes 10+ minutes)
- If unchanged, it reuses the existing container

## When to Modify `experiment.def`

Only modify it when you need system-level packages or new pip dependencies that aren't in `requirements.txt`. For example:

- Need a new C library (e.g., `libffi-dev`) -> edit `experiment.def`
- Need a new Python package -> prefer adding to `requirements.txt` first (installed at runtime via `run.sh`)
- Only add to `experiment.def` if the package is large or slow to install (it gets baked into the image)

## Container Definition Format

```
Bootstrap: docker
From: nvcr.io/nvidia/pytorch:24.07-py3

%post
    apt-get update && apt-get install -y --no-install-recommends \
        package-name \
        && rm -rf /var/lib/apt/lists/*

    pip install --no-cache-dir package-name

%environment
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
```

## Important

- Changing `experiment.def` triggers a rebuild on the cluster, which delays your next submit by 10+ minutes
- The `requirements.txt` route (`pip install -r requirements.txt` in `run.sh`) is faster — packages install at job start without rebuilding the container
- Keep `experiment.def` changes infrequent and batch them
