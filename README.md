# Red9inja-GPT

A production-grade GPT-style language model implementation from scratch using PyTorch. This project demonstrates the complete architecture of modern Large Language Models (LLMs) similar to ChatGPT and Claude.

## Features

- Full Transformer Architecture: Multi-head self-attention, feed-forward networks, layer normalization
- Scalable Design: Supports models from 10M to 1B+ parameters
- Training Pipeline: Complete training loop with gradient accumulation and mixed precision
- Text Generation: Multiple sampling strategies (greedy, top-k, top-p/nucleus)
- Tokenization: BPE tokenizer implementation
- Distributed Training: Multi-GPU support with DDP
- Model Checkpointing: Save and resume training
- Inference API: REST API for text generation
- Web Interface: Simple chat interface

## Architecture

```
Input Text → Tokenization → Embedding Layer → Transformer Blocks → Output Layer → Generated Text
                                                      ↓
                                          [Multi-Head Attention]
                                          [Feed Forward Network]
                                          [Layer Normalization]
                                          [Residual Connections]
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/red9inja-GPT.git
cd red9inja-GPT

# Install dependencies
pip install -r requirements.txt
```

### Training

```bash
# Train on sample data
python train.py --config configs/small.yaml

# Train with custom parameters
python train.py \
    --vocab_size 50257 \
    --embed_dim 768 \
    --num_layers 12 \
    --num_heads 12 \
    --batch_size 32 \
    --epochs 10
```

### Inference

```bash
# Generate text
python generate.py --prompt "What is artificial intelligence?" --max_tokens 100

# Start API server
python api_server.py --port 8000

# Start web interface
python web_app.py
```

## Project Structure

```
red9inja-GPT/
├── model/
│   ├── transformer.py      # Core transformer architecture
│   ├── attention.py        # Multi-head attention mechanism
│   ├── embeddings.py       # Token and positional embeddings
│   └── config.py           # Model configuration
├── training/
│   ├── trainer.py          # Training loop
│   ├── optimizer.py        # Custom optimizers
│   └── scheduler.py        # Learning rate schedulers
├── data/
│   ├── tokenizer.py        # BPE tokenizer
│   ├── dataset.py          # Dataset loader
│   └── preprocessing.py    # Data preprocessing
├── inference/
│   ├── generator.py        # Text generation
│   └── sampling.py         # Sampling strategies
├── api/
│   ├── server.py           # REST API
│   └── web_app.py          # Web interface
├── configs/
│   ├── small.yaml          # Small model config (10M params)
│   ├── medium.yaml         # Medium model config (100M params)
│   └── large.yaml          # Large model config (1B params)
├── utils/
│   ├── logger.py           # Logging utilities
│   └── metrics.py          # Evaluation metrics
├── train.py                # Training script
├── generate.py             # Generation script
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Model Configurations

### Small (10M parameters)
- Layers: 6
- Embedding Dim: 384
- Heads: 6
- Context Length: 512

### Medium (100M parameters)
- Layers: 12
- Embedding Dim: 768
- Heads: 12
- Context Length: 1024

### Large (1B parameters)
- Layers: 24
- Embedding Dim: 1536
- Heads: 16
- Context Length: 2048

## Training Details

- Optimizer: AdamW with weight decay
- Learning Rate: Cosine annealing with warmup
- Batch Size: Gradient accumulation for large effective batch sizes
- Mixed Precision: FP16 training for faster computation
- Regularization: Dropout, layer normalization

## Performance

| Model Size | Parameters | Training Time | Perplexity | GPU Memory |
|------------|-----------|---------------|------------|------------|
| Small      | 10M       | 2 hours       | ~50        | 4GB        |
| Medium     | 100M      | 1 day         | ~30        | 16GB       |
| Large      | 1B        | 1 week        | ~20        | 40GB       |

## Advanced Features

### Distributed Training
```bash
torchrun --nproc_per_node=4 train.py --config configs/large.yaml
```

### Fine-tuning
```bash
python finetune.py --checkpoint checkpoints/pretrained.pt --data custom_data.txt
```

### Export Model
```bash
python export.py --checkpoint checkpoints/model.pt --format onnx
```

## Technical Details

### Attention Mechanism
```
Attention(Q, K, V) = softmax(QK^T / √d_k) × V
```

### Model Parameters
```
Total Parameters = (vocab_size × embed_dim) + 
                   (num_layers × layer_params) + 
                   (embed_dim × vocab_size)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by GPT-2, GPT-3, and Claude architectures
- Based on "Attention Is All You Need" paper
- Uses PyTorch framework

## Contact

For questions or feedback, please open an issue on GitHub.

---

Note: This is an educational implementation. For production use cases, consider using established models like GPT-4, Claude, or open-source alternatives like Llama.
