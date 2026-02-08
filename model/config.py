"""
Model Configuration
Defines hyperparameters for different model sizes
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for Red9inja-GPT model"""
    
    # Model architecture
    vocab_size: int = 50257
    max_seq_len: int = 1024
    embed_dim: int = 768
    num_layers: int = 12
    num_heads: int = 12
    ff_dim: Optional[int] = None  # If None, defaults to 4 * embed_dim
    
    # Regularization
    dropout: float = 0.1
    attention_dropout: float = 0.1
    
    # Activation
    activation: str = "gelu"
    
    # Normalization
    layer_norm_eps: float = 1e-5
    
    # Initialization
    init_std: float = 0.02
    
    def __post_init__(self):
        if self.ff_dim is None:
            self.ff_dim = 4 * self.embed_dim
        
        # Validate
        assert self.embed_dim % self.num_heads == 0, \
            f"embed_dim ({self.embed_dim}) must be divisible by num_heads ({self.num_heads})"
    
    @property
    def head_dim(self) -> int:
        """Dimension of each attention head"""
        return self.embed_dim // self.num_heads
    
    @property
    def num_parameters(self) -> int:
        """Approximate number of parameters"""
        # Token embeddings
        token_embed = self.vocab_size * self.embed_dim
        # Position embeddings
        pos_embed = self.max_seq_len * self.embed_dim
        
        # Transformer block parameters (per layer)
        # Attention: Q, K, V projections + output projection
        attn_params = 4 * (self.embed_dim * self.embed_dim)
        # Feed-forward: 2 linear layers
        ff_params = 2 * (self.embed_dim * self.ff_dim)
        # Layer norms (2 per block)
        ln_params = 4 * self.embed_dim
        
        layer_params = (attn_params + ff_params + ln_params) * self.num_layers
        
        # Output head
        output_head = self.embed_dim * self.vocab_size
        
        total = token_embed + pos_embed + layer_params + output_head
        return total


# Predefined configurations
SMALL_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=512,
    embed_dim=384,
    num_layers=6,
    num_heads=6,
    dropout=0.1,
)

MEDIUM_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=1024,
    embed_dim=768,
    num_layers=12,
    num_heads=12,
    dropout=0.1,
)

LARGE_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=2048,
    embed_dim=1536,
    num_layers=24,
    num_heads=16,
    dropout=0.1,
)

XL_CONFIG = ModelConfig(
    vocab_size=50257,
    max_seq_len=2048,
    embed_dim=2048,
    num_layers=32,
    num_heads=32,
    dropout=0.1,
)


def get_config(name: str) -> ModelConfig:
    """Get predefined configuration by name"""
    configs = {
        "small": SMALL_CONFIG,
        "medium": MEDIUM_CONFIG,
        "large": LARGE_CONFIG,
        "xl": XL_CONFIG,
    }
    
    if name.lower() not in configs:
        raise ValueError(f"Unknown config: {name}. Available: {list(configs.keys())}")
    
    return configs[name.lower()]


if __name__ == "__main__":
    # Print configuration details
    for name in ["small", "medium", "large", "xl"]:
        config = get_config(name)
        print(f"\n{name.upper()} Configuration:")
        print(f"  Parameters: {config.num_parameters:,}")
        print(f"  Layers: {config.num_layers}")
        print(f"  Embedding Dim: {config.embed_dim}")
        print(f"  Heads: {config.num_heads}")
        print(f"  Context Length: {config.max_seq_len}")
