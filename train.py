"""Example training script using Hydra + W&B. Replace with your own code."""

import hydra
import wandb
from omegaconf import DictConfig, OmegaConf


@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    # CER sets WANDB_PROJECT, WANDB_RUN_NAME, WANDB_TAGS via environment
    wandb.init(
        project=cfg.wandb.project,
        entity=cfg.wandb.entity,
        config=OmegaConf.to_container(cfg, resolve=True),
    )

    for epoch in range(cfg.training.max_epochs):
        # Replace with your actual training loop
        train_loss = 1.0 / (epoch + 1)
        val_loss = 1.2 / (epoch + 1)

        wandb.log({
            "epoch": epoch,
            "train/loss": train_loss,
            "val/loss": val_loss,
        })

        print(f"Epoch {epoch + 1}/{cfg.training.max_epochs} - train_loss: {train_loss:.4f}")

    # Save specified files as W&B artifacts for reproducibility
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
