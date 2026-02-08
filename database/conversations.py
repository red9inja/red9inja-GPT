"""
DynamoDB conversation storage
"""

import os
import boto3
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4


class ConversationStore:
    """Store and retrieve user conversations in DynamoDB"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.conversations_table = self.dynamodb.Table(os.getenv('DYNAMODB_CONVERSATIONS_TABLE'))
        self.messages_table = self.dynamodb.Table(os.getenv('DYNAMODB_MESSAGES_TABLE'))
    
    def create_conversation(self, user_id: str, title: str = "New Conversation") -> str:
        """Create a new conversation"""
        conversation_id = str(uuid4())
        timestamp = int(datetime.now().timestamp())
        
        self.conversations_table.put_item(
            Item={
                'user_id': user_id,
                'conversation_id': conversation_id,
                'title': title,
                'created_at': timestamp,
                'updated_at': timestamp,
                'message_count': 0,
            }
        )
        
        return conversation_id
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get all conversations for a user"""
        response = self.conversations_table.query(
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        
        return response.get('Items', [])
    
    def get_conversation(self, user_id: str, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation"""
        response = self.conversations_table.get_item(
            Key={
                'user_id': user_id,
                'conversation_id': conversation_id
            }
        )
        
        return response.get('Item')
    
    def update_conversation_title(self, user_id: str, conversation_id: str, title: str):
        """Update conversation title"""
        self.conversations_table.update_item(
            Key={
                'user_id': user_id,
                'conversation_id': conversation_id
            },
            UpdateExpression='SET title = :title, updated_at = :updated',
            ExpressionAttributeValues={
                ':title': title,
                ':updated': int(datetime.now().timestamp())
            }
        )
    
    def delete_conversation(self, user_id: str, conversation_id: str):
        """Delete a conversation and all its messages"""
        # Delete all messages
        messages = self.get_messages(conversation_id)
        for msg in messages:
            self.messages_table.delete_item(
                Key={
                    'conversation_id': conversation_id,
                    'message_id': msg['message_id']
                }
            )
        
        # Delete conversation
        self.conversations_table.delete_item(
            Key={
                'user_id': user_id,
                'conversation_id': conversation_id
            }
        )
    
    def add_message(
        self,
        conversation_id: str,
        role: str,  # 'user' or 'assistant'
        content: str,
        user_id: str
    ) -> str:
        """Add a message to a conversation"""
        message_id = str(uuid4())
        timestamp = int(datetime.now().timestamp())
        
        # Add message
        self.messages_table.put_item(
            Item={
                'conversation_id': conversation_id,
                'message_id': message_id,
                'role': role,
                'content': content,
                'timestamp': timestamp,
            }
        )
        
        # Update conversation
        self.conversations_table.update_item(
            Key={
                'user_id': user_id,
                'conversation_id': conversation_id
            },
            UpdateExpression='SET updated_at = :updated, message_count = message_count + :inc',
            ExpressionAttributeValues={
                ':updated': timestamp,
                ':inc': 1
            }
        )
        
        return message_id
    
    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Dict]:
        """Get all messages in a conversation"""
        response = self.messages_table.query(
            KeyConditionExpression='conversation_id = :cid',
            ExpressionAttributeValues={':cid': conversation_id},
            ScanIndexForward=True,  # Oldest first
            Limit=limit
        )
        
        return response.get('Items', [])
    
    def get_conversation_context(self, conversation_id: str, max_messages: int = 10) -> List[Dict]:
        """Get recent messages for context"""
        messages = self.get_messages(conversation_id)
        
        # Return last N messages
        return messages[-max_messages:] if len(messages) > max_messages else messages


# Global instance
conversation_store = ConversationStore()
