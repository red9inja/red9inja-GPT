"""
FastAPI server for text generation
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import torch
from transformers import GPT2Tokenizer
from typing import Optional

from model import Red9injaGPT, get_config
from auth.routes import router as auth_router
from auth.cognito import get_current_user
from database.routes import router as conversation_router
from database.conversations import conversation_store
from utils.rate_limit import rate_limit_middleware
from utils.cache import cache, cached
from utils.metrics import metrics_middleware, get_metrics
from api.websocket import manager


app = FastAPI(title="Red9inja-GPT API", version="1.0.0")

# Add middlewares
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(metrics_middleware)

# Include routers
app.include_router(auth_router)
app.include_router(conversation_router)

# Global model and tokenizer
model = None
tokenizer = None
device = None


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.8
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.95
    do_sample: bool = True


class GenerateResponse(BaseModel):
    generated_text: str
    prompt: str
    num_tokens: int


@app.on_event("startup")
async def load_model():
    """Load model on startup"""
    global model, tokenizer, device
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    
    # Load model (you need to specify checkpoint path)
    # For now, create a small model for demonstration
    config = get_config('small')
    model = Red9injaGPT(config).to(device)
    model.eval()
    
    print("Model loaded successfully!")


@app.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    conversation_id: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Generate text from prompt (Authenticated users only)"""
    
    if model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    user_id = user['sub']
    
    # Create conversation if not provided
    if not conversation_id:
        conversation_id = conversation_store.create_conversation(user_id, "New Chat")
    
    # Add user message to conversation
    conversation_store.add_message(
        conversation_id=conversation_id,
        role='user',
        content=request.prompt,
        user_id=user_id
    )
    
    try:
        # Get conversation context
        context_messages = conversation_store.get_conversation_context(conversation_id)
        
        # Build context from previous messages
        context_text = ""
        for msg in context_messages[-5:]:  # Last 5 messages
            context_text += f"{msg['role']}: {msg['content']}\n"
        
        full_prompt = context_text + f"user: {request.prompt}\nassistant:"
        
        # Encode prompt
        input_ids = tokenizer.encode(full_prompt, return_tensors='pt').to(device)
        
        # Generate
        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                top_k=request.top_k,
                top_p=request.top_p,
                do_sample=request.do_sample,
            )
        
        # Decode
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        assistant_response = generated_text.split("assistant:")[-1].strip()
        
        # Add assistant message to conversation
        conversation_store.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=assistant_response,
            user_id=user_id
        )
        
        return GenerateResponse(
            generated_text=assistant_response,
            prompt=request.prompt,
            num_tokens=len(output_ids[0]),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint (Public)"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device),
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()


@app.get("/")
async def root():
    """Root endpoint (Public)"""
    return {
        "message": "Red9inja-GPT API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "generate": "/generate",
            "stream": "/ws/generate",
            "health": "/health",
            "docs": "/docs",
        }
    }


@app.websocket("/ws/generate")
async def websocket_generate(
    websocket: WebSocket,
    token: str
):
    """WebSocket endpoint for streaming generation"""
    try:
        # Verify token
        from auth.cognito import cognito_auth
        user = cognito_auth.verify_token(token)
        user_id = user['sub']
        
        # Connect WebSocket
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_json()
                prompt = data.get('prompt')
                conversation_id = data.get('conversation_id')
                
                if not prompt:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Prompt is required"
                    })
                    continue
                
                # Create conversation if needed
                if not conversation_id:
                    conversation_id = conversation_store.create_conversation(user_id)
                
                # Add user message
                conversation_store.add_message(
                    conversation_id=conversation_id,
                    role='user',
                    content=prompt,
                    user_id=user_id
                )
                
                # Stream generation
                await manager.stream_generation(
                    websocket=websocket,
                    prompt=prompt,
                    model=model,
                    tokenizer=tokenizer,
                    device=device,
                    max_tokens=data.get('max_tokens', 100)
                )
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
    
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
