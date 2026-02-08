# Conversation Persistence with DynamoDB

## Overview

User conversations are automatically saved and persisted using:
- **DynamoDB** - Conversations and messages storage
- **EBS CSI** - Persistent volume for user data
- **Automatic context** - Previous messages included in generation

## Features

### Conversation Management
- Create new conversations
- List all user conversations
- Get conversation with messages
- Update conversation title
- Delete conversations

### Message Storage
- All messages saved automatically
- Conversation context maintained
- Message history for each user
- Timestamps and metadata

### Persistent Storage
- DynamoDB for conversations (scalable, serverless)
- EBS volume for user files (100GB)
- Automatic backups (Point-in-time recovery)
- TTL for old conversations (optional)

## API Endpoints

### Create Conversation
```bash
POST /conversations
Authorization: Bearer TOKEN

{
  "title": "My Chat"
}
```

### List Conversations
```bash
GET /conversations?limit=50
Authorization: Bearer TOKEN
```

Response:
```json
[
  {
    "conversation_id": "uuid",
    "title": "My Chat",
    "created_at": 1234567890,
    "updated_at": 1234567890,
    "message_count": 5
  }
]
```

### Get Conversation
```bash
GET /conversations/{conversation_id}
Authorization: Bearer TOKEN
```

Response:
```json
{
  "conversation": {...},
  "messages": [
    {
      "message_id": "uuid",
      "role": "user",
      "content": "Hello",
      "timestamp": 1234567890
    },
    {
      "message_id": "uuid",
      "role": "assistant",
      "content": "Hi! How can I help?",
      "timestamp": 1234567891
    }
  ]
}
```

### Update Title
```bash
PUT /conversations/{conversation_id}/title?title=New Title
Authorization: Bearer TOKEN
```

### Delete Conversation
```bash
DELETE /conversations/{conversation_id}
Authorization: Bearer TOKEN
```

### Generate with Context
```bash
POST /generate?conversation_id={id}
Authorization: Bearer TOKEN

{
  "prompt": "What did we discuss?",
  "max_tokens": 100
}
```

The model will use previous messages as context!

## How It Works

### 1. User Sends Message
```
User: "What is AI?"
```

### 2. Saved to DynamoDB
```
conversations table:
- user_id: "user-123"
- conversation_id: "conv-456"
- title: "AI Discussion"

messages table:
- conversation_id: "conv-456"
- message_id: "msg-789"
- role: "user"
- content: "What is AI?"
```

### 3. Model Generates Response
```
Context: Previous 5 messages
Prompt: "What is AI?"
Response: "AI is..."
```

### 4. Response Saved
```
messages table:
- conversation_id: "conv-456"
- message_id: "msg-790"
- role: "assistant"
- content: "AI is..."
```

### 5. Next Message Uses Context
```
User: "Tell me more"

Context includes:
- "What is AI?"
- "AI is..."
- "Tell me more"
```

## DynamoDB Tables

### conversations
- **Hash Key**: user_id
- **Range Key**: conversation_id
- **Attributes**: title, created_at, updated_at, message_count
- **GSI**: UserCreatedIndex (user_id, created_at)

### messages
- **Hash Key**: conversation_id
- **Range Key**: message_id
- **Attributes**: role, content, timestamp
- **GSI**: ConversationTimeIndex (conversation_id, timestamp)

## Persistent Volume

### EBS Volume (100GB)
- Mounted at: `/app/user_data`
- Storage class: gp3 (fast SSD)
- Persistent across pod restarts
- Automatic backups

### Usage
```python
# Save user files
with open('/app/user_data/user_123/file.txt', 'w') as f:
    f.write(data)

# Load user files
with open('/app/user_data/user_123/file.txt', 'r') as f:
    data = f.read()
```

## Cost

### DynamoDB
- Free tier: 25 GB storage, 25 WCU, 25 RCU
- Pay-per-request: $1.25 per million writes, $0.25 per million reads
- Example: 10,000 users, 100 messages each = ~$2/month

### EBS
- gp3: $0.08 per GB-month
- 100 GB = $8/month
- Snapshots: $0.05 per GB-month

## Frontend Integration

### JavaScript Example
```javascript
// Create conversation
const conv = await fetch('https://gpt.vmind.online/conversations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ title: 'New Chat' })
});
const { conversation_id } = await conv.json();

// Send message
const response = await fetch(`https://gpt.vmind.online/generate?conversation_id=${conversation_id}`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ prompt: 'Hello!' })
});

// Get conversation history
const history = await fetch(`https://gpt.vmind.online/conversations/${conversation_id}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { messages } = await history.json();
```

## Benefits

1. **Persistent Conversations** - Never lose chat history
2. **Context Awareness** - Model remembers previous messages
3. **Multi-device** - Access from anywhere
4. **Scalable** - DynamoDB handles millions of users
5. **Backup** - Point-in-time recovery enabled
6. **Fast** - Low latency reads/writes

## Monitoring

### CloudWatch Metrics
- Read/Write capacity
- Throttled requests
- Item count
- Storage size

### Logs
- Conversation creation
- Message additions
- Deletions

## Security

- User isolation (user_id in key)
- IAM roles for pod access
- Encryption at rest
- Encryption in transit
- No cross-user access

## Cleanup

### Auto-delete old conversations
Set TTL in DynamoDB:
```python
# Delete after 90 days
ttl = int(time.time()) + (90 * 24 * 60 * 60)
```

Already configured in Terraform!
