"""
Evaluation metrics
"""

import torch
import math


def calculate_perplexity(loss: float) -> float:
    """
    Calculate perplexity from cross-entropy loss
    Perplexity = exp(loss)
    """
    return math.exp(loss)


def calculate_accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    """
    Calculate token-level accuracy
    """
    predictions = torch.argmax(logits, dim=-1)
    correct = (predictions == labels).sum().item()
    total = labels.numel()
    return correct / total


def calculate_top_k_accuracy(logits: torch.Tensor, labels: torch.Tensor, k: int = 5) -> float:
    """
    Calculate top-k accuracy
    """
    _, top_k_preds = torch.topk(logits, k, dim=-1)
    labels_expanded = labels.unsqueeze(-1).expand_as(top_k_preds)
    correct = (top_k_preds == labels_expanded).any(dim=-1).sum().item()
    total = labels.numel()
    return correct / total
