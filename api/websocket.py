"""
WebSocket support for streaming responses
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio

from auth.cognito import get_current_user


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)
    
    async def send_to_user(self, message: str, user_id: str):
        """Send message to all connections of a user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)
    
    async def stream_generation(
        self,
        websocket: WebSocket,
        prompt: str,
        model,
        tokenizer,
        device,
        max_tokens: int = 100
    ):
        """Stream model generation token by token"""
        try:
            # Encode prompt
            input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
            
            # Generate tokens one by one
            generated_tokens = []
            
            for _ in range(max_tokens):
                # Get next token
                with torch.no_grad():
                    outputs = model(input_ids)
                    logits = outputs[0] if isinstance(outputs, tuple) else outputs
                    next_token_logits = logits[:, -1, :]
                    next_token = torch.argmax(next_token_logits, dim=-1)
                
                # Add to sequence
                input_ids = torch.cat([input_ids, next_token.unsqueeze(0)], dim=1)
                generated_tokens.append(next_token.item())
                
                # Decode and send
                token_text = tokenizer.decode([next_token.item()])
                
                await websocket.send_json({
                    "type": "token",
                    "content": token_text,
                    "done": False
                })
                
                # Small delay for streaming effect
                await asyncio.sleep(0.05)
                
                # Check for end token
                if next_token.item() == tokenizer.eos_token_id:
                    break
            
            # Send completion
            full_text = tokenizer.decode(generated_tokens)
            await websocket.send_json({
                "type": "complete",
                "content": full_text,
                "done": True
            })
        
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "content": str(e),
                "done": True
            })


manager = ConnectionManager()
