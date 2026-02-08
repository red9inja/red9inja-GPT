"""
SQS queue for async processing
"""

import os
import json
import boto3
from typing import Dict, Any


class QueueManager:
    """Manage SQS queues for async processing"""
    
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.queue_url = os.getenv('SQS_QUEUE_URL')
    
    def send_generation_request(
        self,
        user_id: str,
        conversation_id: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> str:
        """Send generation request to queue"""
        message = {
            'user_id': user_id,
            'conversation_id': conversation_id,
            'prompt': prompt,
            'params': params,
            'timestamp': int(time.time())
        }
        
        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'user_id': {
                    'StringValue': user_id,
                    'DataType': 'String'
                },
                'priority': {
                    'StringValue': 'normal',
                    'DataType': 'String'
                }
            }
        )
        
        return response['MessageId']
    
    def receive_messages(self, max_messages: int = 10):
        """Receive messages from queue"""
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=10,
            MessageAttributeNames=['All']
        )
        
        return response.get('Messages', [])
    
    def delete_message(self, receipt_handle: str):
        """Delete processed message"""
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )
    
    def get_queue_depth(self) -> int:
        """Get approximate number of messages in queue"""
        response = self.sqs.get_queue_attributes(
            QueueUrl=self.queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        
        return int(response['Attributes']['ApproximateNumberOfMessages'])


queue_manager = QueueManager()
