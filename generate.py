"""
Text Generation Script
"""

import argparse
import torch
from transformers import GPT2Tokenizer

from model import Red9injaGPT, get_config


def load_model(checkpoint_path: str, device: torch.device):
    """Load model from checkpoint"""
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Get model config
    model_size = checkpoint['config'].get('model_size', 'small')
    config = get_config(model_size)
    
    # Create and load model
    model = Red9injaGPT(config).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    return model


def generate_text(
    model: Red9injaGPT,
    tokenizer: GPT2Tokenizer,
    prompt: str,
    max_tokens: int = 100,
    temperature: float = 0.8,
    top_k: int = 50,
    top_p: float = 0.95,
    device: torch.device = torch.device('cpu'),
):
    """Generate text from prompt"""
    
    # Encode prompt
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    
    # Generate
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=True,
        )
    
    # Decode
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    return generated_text


def main():
    parser = argparse.ArgumentParser(description="Generate text with Red9inja-GPT")
    parser.add_argument('--checkpoint', type=str, required=True, help='Path to model checkpoint')
    parser.add_argument('--prompt', type=str, required=True, help='Input prompt')
    parser.add_argument('--max_tokens', type=int, default=100, help='Maximum tokens to generate')
    parser.add_argument('--temperature', type=float, default=0.8, help='Sampling temperature')
    parser.add_argument('--top_k', type=int, default=50, help='Top-k sampling')
    parser.add_argument('--top_p', type=float, default=0.95, help='Top-p (nucleus) sampling')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    
    args = parser.parse_args()
    
    device = torch.device(args.device)
    print(f"Using device: {device}")
    
    # Load tokenizer (using GPT-2 tokenizer as default)
    print("Loading tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    
    # Load model
    print(f"Loading model from {args.checkpoint}...")
    model = load_model(args.checkpoint, device)
    
    print(f"\nPrompt: {args.prompt}")
    print(f"Generating {args.max_tokens} tokens...\n")
    print("-" * 80)
    
    # Generate
    generated = generate_text(
        model,
        tokenizer,
        args.prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        device=device,
    )
    
    print(generated)
    print("-" * 80)


if __name__ == "__main__":
    main()
