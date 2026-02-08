"""
Token and Positional Embeddings
"""

import torch
import torch.nn as nn
import math


class TokenEmbedding(nn.Module):
    """
    Token embedding layer
    Converts token IDs to dense vectors
    """
    
    def __init__(self, vocab_size: int, embed_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.embed_dim = embed_dim
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Token IDs of shape (batch_size, seq_len)
        Returns:
            Embeddings of shape (batch_size, seq_len, embed_dim)
        """
        return self.embedding(x) * math.sqrt(self.embed_dim)


class PositionalEmbedding(nn.Module):
    """
    Learnable positional embeddings
    """
    
    def __init__(self, max_seq_len: int, embed_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(max_seq_len, embed_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape (batch_size, seq_len, embed_dim)
        Returns:
            Positional embeddings of shape (batch_size, seq_len, embed_dim)
        """
        batch_size, seq_len = x.shape[0], x.shape[1]
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        return self.embedding(positions)


class SinusoidalPositionalEmbedding(nn.Module):
    """
    Sinusoidal positional embeddings (from original Transformer paper)
    Fixed, not learnable
    
    PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """
    
    def __init__(self, max_seq_len: int, embed_dim: int):
        super().__init__()
        
        # Create positional encoding matrix
        pe = torch.zeros(max_seq_len, embed_dim)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embed_dim, 2).float() * (-math.log(10000.0) / embed_dim)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Register as buffer (not a parameter, but part of state)
        self.register_buffer('pe', pe.unsqueeze(0))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape (batch_size, seq_len, embed_dim)
        Returns:
            Positional embeddings of shape (batch_size, seq_len, embed_dim)
        """
        seq_len = x.shape[1]
        return self.pe[:, :seq_len, :]


class RotaryPositionalEmbedding(nn.Module):
    """
    Rotary Position Embedding (RoPE)
    Used in models like GPT-Neo, PaLM, LLaMA
    More efficient than absolute positional embeddings
    """
    
    def __init__(self, dim: int, max_seq_len: int = 2048, base: int = 10000):
        super().__init__()
        
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        
        # Build cache
        self.max_seq_len = max_seq_len
        self._build_cache(max_seq_len)
    
    def _build_cache(self, seq_len: int):
        """Build rotation matrix cache"""
        t = torch.arange(seq_len, dtype=self.inv_freq.dtype, device=self.inv_freq.device)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        
        self.register_buffer("cos_cached", emb.cos()[None, :, None, :], persistent=False)
        self.register_buffer("sin_cached", emb.sin()[None, :, None, :], persistent=False)
    
    def forward(self, x: torch.Tensor, seq_len: int = None):
        """
        Apply rotary embeddings to input
        """
        if seq_len > self.max_seq_len:
            self._build_cache(seq_len)
        
        return (
            self.cos_cached[:, :seq_len, :, :],
            self.sin_cached[:, :seq_len, :, :],
        )


def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor):
    """
    Apply rotary position embeddings to queries and keys
    """
    def rotate_half(x):
        x1, x2 = x[..., : x.shape[-1] // 2], x[..., x.shape[-1] // 2 :]
        return torch.cat((-x2, x1), dim=-1)
    
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    
    return q_embed, k_embed


if __name__ == "__main__":
    # Test embeddings
    batch_size = 2
    seq_len = 10
    vocab_size = 1000
    embed_dim = 64
    
    # Token IDs
    tokens = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    # Test TokenEmbedding
    token_emb = TokenEmbedding(vocab_size, embed_dim)
    token_out = token_emb(tokens)
    print(f"Token embedding shape: {token_out.shape}")
    
    # Test PositionalEmbedding
    pos_emb = PositionalEmbedding(512, embed_dim)
    pos_out = pos_emb(token_out)
    print(f"Positional embedding shape: {pos_out.shape}")
    
    # Test SinusoidalPositionalEmbedding
    sin_pos_emb = SinusoidalPositionalEmbedding(512, embed_dim)
    sin_pos_out = sin_pos_emb(token_out)
    print(f"Sinusoidal positional embedding shape: {sin_pos_out.shape}")
    
    # Combined
    combined = token_out + pos_out
    print(f"Combined embedding shape: {combined.shape}")
