"""
AWS Cognito Authentication
"""

import os
import jwt
from typing import Optional, Dict
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from functools import lru_cache


security = HTTPBearer()


class CognitoAuth:
    """AWS Cognito authentication handler"""
    
    def __init__(
        self,
        region: str,
        user_pool_id: str,
        client_id: str,
    ):
        self.region = region
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        self.issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> Dict:
        """Get JSON Web Key Set from Cognito"""
        response = requests.get(self.jwks_url)
        return response.json()
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token from Cognito"""
        try:
            # Get JWKS
            jwks = self.get_jwks()
            
            # Decode header to get kid
            header = jwt.get_unverified_header(token)
            kid = header['kid']
            
            # Find the key
            key = None
            for k in jwks['keys']:
                if k['kid'] == kid:
                    key = k
                    break
            
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Verify token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=self.issuer,
            )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    
    def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security)
    ) -> Dict:
        """Get current authenticated user"""
        token = credentials.credentials
        return self.verify_token(token)


# Initialize Cognito auth
cognito_auth = CognitoAuth(
    region=os.getenv("AWS_REGION", "us-east-1"),
    user_pool_id=os.getenv("COGNITO_USER_POOL_ID"),
    client_id=os.getenv("COGNITO_CLIENT_ID"),
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """Dependency to get current user"""
    return cognito_auth.get_current_user(credentials)


def require_admin(user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role"""
    groups = user.get("cognito:groups", [])
    if "admin" not in groups:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_premium(user: Dict = Depends(get_current_user)) -> Dict:
    """Require premium or admin role"""
    groups = user.get("cognito:groups", [])
    if "premium" not in groups and "admin" not in groups:
        raise HTTPException(status_code=403, detail="Premium access required")
    return user
