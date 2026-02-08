"""
Conversation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from auth.cognito import get_current_user
from database.conversations import conversation_store


router = APIRouter(prefix="/conversations", tags=["Conversations"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class MessageRequest(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: int
    updated_at: int
    message_count: int


class MessageResponse(BaseModel):
    message_id: str
    role: str
    content: str
    timestamp: int


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    user_id = user['sub']
    conversation_id = conversation_store.create_conversation(user_id, request.title)
    
    conversation = conversation_store.get_conversation(user_id, conversation_id)
    return conversation


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """List all user conversations"""
    user_id = user['sub']
    conversations = conversation_store.get_user_conversations(user_id, limit)
    return conversations


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    """Get a specific conversation with messages"""
    user_id = user['sub']
    
    conversation = conversation_store.get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = conversation_store.get_messages(conversation_id)
    
    return {
        "conversation": conversation,
        "messages": messages
    }


@router.put("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    user: dict = Depends(get_current_user)
):
    """Update conversation title"""
    user_id = user['sub']
    
    conversation = conversation_store.get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation_store.update_conversation_title(user_id, conversation_id, title)
    
    return {"message": "Title updated"}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    user_id = user['sub']
    
    conversation = conversation_store.get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation_store.delete_conversation(user_id, conversation_id)
    
    return {"message": "Conversation deleted"}


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    request: MessageRequest,
    user: dict = Depends(get_current_user)
):
    """Add a message to conversation"""
    user_id = user['sub']
    
    conversation = conversation_store.get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add user message
    message_id = conversation_store.add_message(
        conversation_id=conversation_id,
        role='user',
        content=request.content,
        user_id=user_id
    )
    
    # Get the message
    messages = conversation_store.get_messages(conversation_id)
    message = next((m for m in messages if m['message_id'] == message_id), None)
    
    return message


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    """Get all messages in a conversation"""
    user_id = user['sub']
    
    conversation = conversation_store.get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = conversation_store.get_messages(conversation_id, limit)
    return messages
