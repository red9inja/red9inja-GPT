"""
Quick start script to test the model
"""

import torch
from model import Red9injaGPT, get_config, SMALL_CONFIG, MEDIUM_CONFIG, LARGE_CONFIG


def print_model_info(config_name: str):
    """Print information about a model configuration"""
    config = get_config(config_name)
    
    print(f"\n{'='*60}")
    print(f"{config_name.upper()} Model Configuration")
    print(f"{'='*60}")
    print(f"Parameters: {config.num_parameters:,}")
    print(f"Layers: {config.num_layers}")
    print(f"Embedding Dimension: {config.embed_dim}")
    print(f"Attention Heads: {config.num_heads}")
    print(f"Head Dimension: {config.head_dim}")
    print(f"Feed-Forward Dimension: {config.ff_dim}")
    print(f"Max Sequence Length: {config.max_seq_len}")
    print(f"Vocabulary Size: {config.vocab_size:,}")
    print(f"Dropout: {config.dropout}")
    print(f"{'='*60}\n")


def test_model(config_name: str = 'small'):
    """Test model creation and forward pass"""
    print(f"\nTesting {config_name} model...")
    
    # Get configuration
    config = get_config(config_name)
    
    # Create model
    model = Red9injaGPT(config)
    print(f"✓ Model created successfully")
    print(f"  Total parameters: {model.get_num_params():,}")
    
    # Test forward pass
    batch_size = 2
    seq_len = 32
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
    
    print(f"\n✓ Testing forward pass...")
    print(f"  Input shape: {input_ids.shape}")
    
    with torch.no_grad():
        logits, loss = model(input_ids, labels=input_ids)
    
    print(f"  Output shape: {logits.shape}")
    print(f"  Loss: {loss.item():.4f}")
    
    # Test generation
    print(f"\n✓ Testing text generation...")
    prompt = input_ids[:1, :5]  # First sample, first 5 tokens
    print(f"  Prompt length: {prompt.shape[1]}")
    
    with torch.no_grad():
        generated = model.generate(
            prompt,
            max_new_tokens=20,
            temperature=0.8,
            top_k=50,
        )
    
    print(f"  Generated length: {generated.shape[1]}")
    print(f"  Generated tokens: {generated[0].tolist()}")
    
    print(f"\n✓ All tests passed for {config_name} model!\n")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Red9inja-GPT - Quick Start")
    print("="*60)
    
    # Print all configurations
    for config_name in ['small', 'medium', 'large', 'xl']:
        print_model_info(config_name)
    
    # Test small model
    print("\n" + "="*60)
    print("Running Tests")
    print("="*60)
    
    test_model('small')
    
    print("\n" + "="*60)
    print("Quick Start Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Prepare your training data")
    print("2. Run: python train.py --data_path your_data.txt --model_size small")
    print("3. Generate text: python generate.py --checkpoint checkpoints/best_model.pt --prompt 'Your prompt'")
    print("4. Start API: python api/server.py")
    print("5. Start web UI: python api/web_app.py")
    print("\nFor more information, see README.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
