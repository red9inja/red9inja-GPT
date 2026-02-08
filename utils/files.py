"""
File upload support
"""

import os
import boto3
from fastapi import UploadFile, HTTPException
from typing import List
import uuid


class FileManager:
    """Manage file uploads to S3"""
    
    def __init__(self):
        self.s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.bucket = os.getenv('S3_BUCKET_NAME')
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'document': ['application/pdf', 'text/plain', 'application/json'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg']
        }
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: str,
        conversation_id: str
    ) -> dict:
        """Upload file to S3"""
        
        # Validate file size
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {self.max_file_size / 1024 / 1024}MB"
            )
        
        # Validate file type
        file_type = self._get_file_type(file.content_type)
        if not file_type:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed: {file.content_type}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        extension = file.filename.split('.')[-1]
        s3_key = f"users/{user_id}/conversations/{conversation_id}/{file_id}.{extension}"
        
        # Upload to S3
        try:
            self.s3.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'conversation_id': conversation_id,
                    'original_filename': file.filename
                }
            )
            
            # Generate presigned URL
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=3600
            )
            
            return {
                'file_id': file_id,
                'filename': file.filename,
                'content_type': file.content_type,
                'size': len(content),
                'url': url,
                's3_key': s3_key
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    def _get_file_type(self, content_type: str) -> str:
        """Get file type category"""
        for file_type, mime_types in self.allowed_types.items():
            if content_type in mime_types:
                return file_type
        return None
    
    async def delete_file(self, s3_key: str):
        """Delete file from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
    
    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Get presigned URL for file"""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': s3_key},
            ExpiresIn=expires_in
        )


file_manager = FileManager()
