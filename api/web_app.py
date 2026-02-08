"""
Gradio Web Interface for Red9inja-GPT
"""

import gradio as gr
import torch
from transformers import GPT2Tokenizer

from model import Red9injaGPT, get_config


# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Loading model on {device}...")

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
config = get_config('small')
model = Red9injaGPT(config).to(device)
model.eval()

print("Model loaded!")


def generate_text(
    prompt: str,
    max_tokens: int = 100,
    temperature: float = 0.8,
    top_k: int = 50,
    top_p: float = 0.95,
):
    """Generate text from prompt"""
    
    if not prompt:
        return "Please enter a prompt"
    
    try:
        # Encode
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
        generated = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        return generated
    
    except Exception as e:
        return f"Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Red9inja-GPT") as demo:
    gr.Markdown("# 🤖 Red9inja-GPT")
    gr.Markdown("A production-grade GPT implementation")
    
    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(
                label="Prompt",
                placeholder="Enter your prompt here...",
                lines=5,
            )
            
            with gr.Row():
                max_tokens = gr.Slider(
                    minimum=10,
                    maximum=500,
                    value=100,
                    step=10,
                    label="Max Tokens",
                )
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=2.0,
                    value=0.8,
                    step=0.1,
                    label="Temperature",
                )
            
            with gr.Row():
                top_k = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=50,
                    step=1,
                    label="Top-K",
                )
                top_p = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    value=0.95,
                    step=0.05,
                    label="Top-P",
                )
            
            generate_btn = gr.Button("Generate", variant="primary")
        
        with gr.Column():
            output = gr.Textbox(
                label="Generated Text",
                lines=15,
            )
    
    # Examples
    gr.Examples(
        examples=[
            ["What is artificial intelligence?"],
            ["Once upon a time in a distant land,"],
            ["The future of technology is"],
            ["Explain quantum computing in simple terms:"],
        ],
        inputs=prompt_input,
    )
    
    # Connect button
    generate_btn.click(
        fn=generate_text,
        inputs=[prompt_input, max_tokens, temperature, top_k, top_p],
        outputs=output,
    )
    
    gr.Markdown("""
    ### About
    Red9inja-GPT is a production-grade implementation of GPT-style language models.
    
    **Parameters:**
    - **Max Tokens**: Maximum number of tokens to generate
    - **Temperature**: Controls randomness (higher = more random)
    - **Top-K**: Keep only top K tokens with highest probability
    - **Top-P**: Nucleus sampling threshold
    """)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
