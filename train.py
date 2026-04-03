"""Example training script. Replace with your own code."""
import argparse

import wandb


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    return parser.parse_args()


def main():
    args = parse_args()

    # CER sets WANDB_PROJECT, WANDB_RUN_NAME, WANDB_TAGS automatically
    wandb.init(config=vars(args))

    for epoch in range(args.epochs):
        # Replace with your actual training loop
        train_loss = 1.0 / (epoch + 1)
        val_loss = 1.2 / (epoch + 1)

        wandb.log({
            "epoch": epoch,
            "train/loss": train_loss,
            "val/loss": val_loss,
        })

        print(f"Epoch {epoch + 1}/{args.epochs} - train_loss: {train_loss:.4f}")

    wandb.finish()


if __name__ == "__main__":
    main()
