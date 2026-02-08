"""
Training Script for Red9inja-GPT
"""

import os
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm
import yaml

from model import Red9injaGPT, ModelConfig, get_config
from data.dataset import TextDataset
from utils.logger import setup_logger
from utils.metrics import calculate_perplexity


class Trainer:
    """Training manager for Red9inja-GPT"""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        scheduler: torch.optim.lr_scheduler._LRScheduler,
        device: torch.device,
        config: dict,
    ):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.config = config
        
        self.logger = setup_logger("trainer")
        self.best_val_loss = float('inf')
        self.global_step = 0
    
    def train_epoch(self, epoch: int):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch}")
        for batch_idx, batch in enumerate(pbar):
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # Forward pass
            logits, loss = self.model(input_ids, labels=labels)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.get('grad_clip', 1.0)
            )
            
            self.optimizer.step()
            self.scheduler.step()
            
            # Update metrics
            total_loss += loss.item()
            self.global_step += 1
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'lr': f"{self.scheduler.get_last_lr()[0]:.2e}",
            })
            
            # Log periodically
            if self.global_step % self.config.get('log_interval', 100) == 0:
                self.logger.info(
                    f"Step {self.global_step} | "
                    f"Loss: {loss.item():.4f} | "
                    f"LR: {self.scheduler.get_last_lr()[0]:.2e}"
                )
        
        avg_loss = total_loss / len(self.train_loader)
        return avg_loss
    
    @torch.no_grad()
    def validate(self):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        
        for batch in tqdm(self.val_loader, desc="Validating"):
            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            logits, loss = self.model(input_ids, labels=labels)
            total_loss += loss.item()
        
        avg_loss = total_loss / len(self.val_loader)
        perplexity = calculate_perplexity(avg_loss)
        
        return avg_loss, perplexity
    
    def save_checkpoint(self, epoch: int, val_loss: float, filename: str = None):
        """Save model checkpoint"""
        if filename is None:
            filename = f"checkpoint_epoch_{epoch}.pt"
        
        checkpoint_dir = self.config.get('checkpoint_dir', 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        filepath = os.path.join(checkpoint_dir, filename)
        
        torch.save({
            'epoch': epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss,
            'config': self.config,
        }, filepath)
        
        self.logger.info(f"Checkpoint saved: {filepath}")
    
    def train(self, num_epochs: int):
        """Main training loop"""
        self.logger.info("Starting training...")
        self.logger.info(f"Total epochs: {num_epochs}")
        self.logger.info(f"Training samples: {len(self.train_loader.dataset)}")
        self.logger.info(f"Validation samples: {len(self.val_loader.dataset)}")
        
        for epoch in range(1, num_epochs + 1):
            # Train
            train_loss = self.train_epoch(epoch)
            
            # Validate
            val_loss, perplexity = self.validate()
            
            self.logger.info(
                f"Epoch {epoch}/{num_epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Perplexity: {perplexity:.2f}"
            )
            
            # Save checkpoint
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.save_checkpoint(epoch, val_loss, "best_model.pt")
            
            # Save periodic checkpoint
            if epoch % self.config.get('save_interval', 5) == 0:
                self.save_checkpoint(epoch, val_loss)
        
        self.logger.info("Training completed!")


def main():
    parser = argparse.ArgumentParser(description="Train Red9inja-GPT")
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--model_size', type=str, default='small', 
                       choices=['small', 'medium', 'large', 'xl'])
    parser.add_argument('--data_path', type=str, required=True, help='Path to training data')
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints')
    
    args = parser.parse_args()
    
    # Load config
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    # Update config with command line args
    config.update({
        'model_size': args.model_size,
        'data_path': args.data_path,
        'batch_size': args.batch_size,
        'epochs': args.epochs,
        'lr': args.lr,
        'device': args.device,
        'checkpoint_dir': args.checkpoint_dir,
    })
    
    # Setup device
    device = torch.device(args.device)
    print(f"Using device: {device}")
    
    # Create model
    model_config = get_config(args.model_size)
    model = Red9injaGPT(model_config).to(device)
    
    print(f"Model: {args.model_size}")
    print(f"Parameters: {model.get_num_params():,}")
    
    # Create datasets (placeholder - implement in data/dataset.py)
    # train_dataset = TextDataset(args.data_path, model_config.max_seq_len)
    # val_dataset = TextDataset(args.data_path, model_config.max_seq_len, split='val')
    
    # train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    # val_loader = DataLoader(val_dataset, batch_size=args.batch_size)
    
    # Optimizer
    optimizer = AdamW(
        model.parameters(),
        lr=args.lr,
        betas=(0.9, 0.95),
        weight_decay=0.1,
    )
    
    # Scheduler
    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=args.epochs * 1000,  # Adjust based on dataset size
        eta_min=args.lr * 0.1,
    )
    
    # Trainer
    # trainer = Trainer(model, train_loader, val_loader, optimizer, scheduler, device, config)
    # trainer.train(args.epochs)
    
    print("\nNote: Implement TextDataset in data/dataset.py to start training")


if __name__ == "__main__":
    main()
