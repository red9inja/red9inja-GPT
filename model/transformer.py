"""
Complete Transformer Model
Red9inja-GPT: Production-grade GPT implementation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple

from .config import ModelConfig
from .attention import CausalSelfAttention
from .embeddings import TokenEmbedding, PositionalEmbedding


class FeedForward(nn.Module):
    """
    Position-wise Feed-Forward Network
    FFN(x) = max(0, xW1 + b1)W2 + b2
    """
    
    def __init__(self, embed_dim: int, ff_dim: int, dropout: float = 0.1, activation: str = "gelu"):
        super().__init__()
        
        self.fc1 = nn.Linear(embed_dim, ff_dim)
        self.fc2 = nn.Linear(ff_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)
        
        # Activation function
        if activation == "gelu":
            self.activation = nn.GELU()
        elif activation == "relu":
            self.activation = nn.ReLU()
        elif activation == "swish":
            self.activation = nn.SiLU()
        else:
            raise ValueError(f"Unknown activation: {activation}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return x


class TransformerBlock(nn.Module):
    """
    Single Transformer block
    
    x -> LayerNorm -> Attention -> Add -> LayerNorm -> FFN -> Add -> output
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        # Self-attention
        self.attention = CausalSelfAttention(
            embed_dim=config.embed_dim,
            num_heads=config.num_heads,
            max_seq_len=config.max_seq_len,
            dropout=config.attention_dropout,
        )
        
        # Feed-forward network
        self.ffn = FeedForward(
            embed_dim=config.embed_dim,
            ff_dim=config.ff_dim,
            dropout=config.dropout,
            activation=config.activation,
        )
        
        # Layer normalization
        self.ln1 = nn.LayerNorm(config.embed_dim, eps=config.layer_norm_eps)
        self.ln2 = nn.LayerNorm(config.embed_dim, eps=config.layer_norm_eps)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-norm architecture (more stable)
        # Attention block with residual connection
        x = x + self.attention(self.ln1(x))
        
        # FFN block with residual connection
        x = x + self.ffn(self.ln2(x))
        
        return x


class Red9injaGPT(nn.Module):
    """
    Red9inja-GPT: Complete GPT-style language model
    
    Architecture:
        Input -> Token Embedding + Positional Embedding
              -> Transformer Blocks (N layers)
              -> Layer Norm
              -> Output Head (Language Modeling)
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        self.config = config
        
        # Embeddings
        self.token_embedding = TokenEmbedding(config.vocab_size, config.embed_dim)
        self.pos_embedding = PositionalEmbedding(config.max_seq_len, config.embed_dim)
        self.dropout = nn.Dropout(config.dropout)
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(config) for _ in range(config.num_layers)
        ])
        
        # Final layer norm
        self.ln_final = nn.LayerNorm(config.embed_dim, eps=config.layer_norm_eps)
        
        # Output head (language modeling)
        self.lm_head = nn.Linear(config.embed_dim, config.vocab_size, bias=False)
        
        # Weight tying (share weights between token embedding and output head)
        self.lm_head.weight = self.token_embedding.embedding.weight
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize weights following GPT-2 initialization"""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=self.config.init_std)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=self.config.init_std)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Forward pass
        
        Args:
            input_ids: Token IDs of shape (batch_size, seq_len)
            labels: Optional labels for language modeling loss
        
        Returns:
            logits: Output logits of shape (batch_size, seq_len, vocab_size)
            loss: Optional loss if labels are provided
        """
        batch_size, seq_len = input_ids.shape
        
        # Check sequence length
        assert seq_len <= self.config.max_seq_len, \
            f"Sequence length {seq_len} exceeds maximum {self.config.max_seq_len}"
        
        # Get embeddings
        token_emb = self.token_embedding(input_ids)  # (B, T, C)
        pos_emb = self.pos_embedding(token_emb)      # (B, T, C)
        x = self.dropout(token_emb + pos_emb)
        
        # Pass through transformer blocks
        for block in self.blocks:
            x = block(x)
        
        # Final layer norm
        x = self.ln_final(x)
        
        # Language modeling head
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        # Calculate loss if labels provided
        loss = None
        if labels is not None:
            # Shift logits and labels for next token prediction
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            
            # Flatten for cross entropy
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )
        
        return logits, loss
    
    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 100,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        do_sample: bool = True,
    ) -> torch.Tensor:
        """
        Generate text autoregressively
        
        Args:
            input_ids: Starting token IDs (batch_size, seq_len)
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_k: Keep only top k tokens with highest probability
            top_p: Keep top tokens with cumulative probability >= top_p
            do_sample: Whether to sample or use greedy decoding
        
        Returns:
            Generated token IDs (batch_size, seq_len + max_new_tokens)
        """
        for _ in range(max_new_tokens):
            # Crop context if needed
            idx_cond = input_ids if input_ids.size(1) <= self.config.max_seq_len \
                       else input_ids[:, -self.config.max_seq_len:]
            
            # Forward pass
            logits, _ = self(idx_cond)
            
            # Get logits for last token
            logits = logits[:, -1, :] / temperature
            
            # Apply top-k filtering
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
            
            # Apply top-p (nucleus) filtering
            if top_p is not None:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                
                # Remove tokens with cumulative probability above threshold
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                logits[indices_to_remove] = -float('Inf')
            
            # Sample or greedy
            probs = F.softmax(logits, dim=-1)
            if do_sample:
                idx_next = torch.multinomial(probs, num_samples=1)
            else:
                idx_next = torch.argmax(probs, dim=-1, keepdim=True)
            
            # Append to sequence
            input_ids = torch.cat([input_ids, idx_next], dim=1)
        
        return input_ids
    
    def get_num_params(self, non_embedding: bool = True) -> int:
        """
        Return the number of parameters in the model
        """
        n_params = sum(p.numel() for p in self.parameters())
        if non_embedding:
            n_params -= self.pos_embedding.embedding.weight.numel()
        return n_params


if __name__ == "__main__":
    # Test model
    from .config import SMALL_CONFIG
    
    config = SMALL_CONFIG
    model = Red9injaGPT(config)
    
    print(f"Model parameters: {model.get_num_params():,}")
    print(f"Config parameters: {config.num_parameters:,}")
    
    # Test forward pass
    batch_size = 2
    seq_len = 10
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    
    logits, loss = model(input_ids, labels=input_ids)
    print(f"\nForward pass:")
    print(f"  Input shape: {input_ids.shape}")
    print(f"  Output shape: {logits.shape}")
    print(f"  Loss: {loss.item():.4f}")
    
    # Test generation
    generated = model.generate(input_ids[:1, :5], max_new_tokens=10)
    print(f"\nGeneration:")
    print(f"  Input length: 5")
    print(f"  Generated length: {generated.shape[1]}")
