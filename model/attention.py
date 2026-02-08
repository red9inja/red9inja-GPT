"""
Multi-Head Self-Attention Mechanism
Core component of the Transformer architecture
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class MultiHeadAttention(nn.Module):
    """
    Multi-Head Self-Attention mechanism
    
    Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
    """
    
    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.1,
        bias: bool = True,
    ):
        super().__init__()
        
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5
        
        # Q, K, V projections (combined for efficiency)
        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim, bias=bias)
        
        # Output projection
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        
        # Dropout
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        return_attention: bool = False,
    ):
        """
        Args:
            x: Input tensor of shape (batch_size, seq_len, embed_dim)
            mask: Optional attention mask (batch_size, seq_len, seq_len)
            return_attention: Whether to return attention weights
            
        Returns:
            Output tensor of shape (batch_size, seq_len, embed_dim)
            Optionally attention weights if return_attention=True
        """
        B, T, C = x.shape
        
        # Project to Q, K, V
        qkv = self.qkv_proj(x)  # (B, T, 3*C)
        qkv = qkv.reshape(B, T, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # (3, B, num_heads, T, head_dim)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        # Compute attention scores
        attn = (q @ k.transpose(-2, -1)) * self.scale  # (B, num_heads, T, T)
        
        # Apply mask if provided (for causal attention)
        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))
        
        # Softmax to get attention weights
        attn = F.softmax(attn, dim=-1)
        attn = self.attn_dropout(attn)
        
        # Apply attention to values
        out = attn @ v  # (B, num_heads, T, head_dim)
        
        # Concatenate heads
        out = out.transpose(1, 2).contiguous()  # (B, T, num_heads, head_dim)
        out = out.reshape(B, T, C)  # (B, T, embed_dim)
        
        # Output projection
        out = self.out_proj(out)
        out = self.resid_dropout(out)
        
        if return_attention:
            return out, attn
        return out


class CausalSelfAttention(MultiHeadAttention):
    """
    Causal (autoregressive) self-attention
    Prevents attending to future tokens
    """
    
    def __init__(self, embed_dim: int, num_heads: int, max_seq_len: int, dropout: float = 0.1):
        super().__init__(embed_dim, num_heads, dropout)
        
        # Create causal mask (lower triangular)
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(max_seq_len, max_seq_len)).view(
                1, 1, max_seq_len, max_seq_len
            )
        )
    
    def forward(self, x: torch.Tensor, return_attention: bool = False):
        """
        Forward pass with causal masking
        """
        B, T, C = x.shape
        
        # Use causal mask
        mask = self.causal_mask[:, :, :T, :T]
        
        return super().forward(x, mask=mask, return_attention=return_attention)


class FlashAttention(nn.Module):
    """
    Flash Attention - Memory efficient attention
    (Simplified version for demonstration)
    """
    
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        self.dropout = dropout
    
    def forward(self, x: torch.Tensor):
        """
        Memory-efficient attention using PyTorch's scaled_dot_product_attention
        """
        B, T, C = x.shape
        
        # Project to Q, K, V
        qkv = self.qkv_proj(x)
        qkv = qkv.reshape(B, T, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        
        # Use PyTorch's efficient implementation
        out = F.scaled_dot_product_attention(
            q, k, v,
            dropout_p=self.dropout if self.training else 0.0,
            is_causal=True,
        )
        
        # Reshape and project
        out = out.transpose(1, 2).contiguous().reshape(B, T, C)
        out = self.out_proj(out)
        
        return out


if __name__ == "__main__":
    # Test attention mechanism
    batch_size = 2
    seq_len = 10
    embed_dim = 64
    num_heads = 4
    
    x = torch.randn(batch_size, seq_len, embed_dim)
    
    # Test MultiHeadAttention
    attn = MultiHeadAttention(embed_dim, num_heads)
    out = attn(x)
    print(f"MultiHeadAttention output shape: {out.shape}")
    
    # Test CausalSelfAttention
    causal_attn = CausalSelfAttention(embed_dim, num_heads, max_seq_len=512)
    out = causal_attn(x)
    print(f"CausalSelfAttention output shape: {out.shape}")
    
    # Test with attention weights
    out, weights = causal_attn(x, return_attention=True)
    print(f"Attention weights shape: {weights.shape}")
