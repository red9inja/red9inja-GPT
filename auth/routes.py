"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import boto3
import os

from auth.cognito import get_current_user, require_admin


router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cognito client
cognito_client = boto3.client('cognito-idp', region_name=os.getenv("AWS_REGION", "us-east-1"))
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    token_type: str = "Bearer"


@router.post("/signup", status_code=201)
async def signup(request: SignupRequest):
    """
    Register a new user
    """
    try:
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=request.email,
            Password=request.password,
            UserAttributes=[
                {'Name': 'email', 'Value': request.email},
                {'Name': 'name', 'Value': request.name},
            ]
        )
        
        return {
            "message": "User created successfully. Please check your email to verify.",
            "user_sub": response['UserSub']
        }
    
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=400, detail="User already exists")
    except cognito_client.exceptions.InvalidPasswordException:
        raise HTTPException(status_code=400, detail="Password does not meet requirements")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login user and get tokens
    """
    try:
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': request.email,
                'PASSWORD': request.password,
            }
        )
        
        return TokenResponse(
            access_token=response['AuthenticationResult']['AccessToken'],
            id_token=response['AuthenticationResult']['IdToken'],
            refresh_token=response['AuthenticationResult']['RefreshToken'],
        )
    
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except cognito_client.exceptions.UserNotConfirmedException:
        raise HTTPException(status_code=401, detail="Please verify your email first")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-email")
async def verify_email(email: EmailStr, code: str):
    """
    Verify email with confirmation code
    """
    try:
        cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
        )
        
        return {"message": "Email verified successfully"}
    
    except cognito_client.exceptions.CodeMismatchException:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/resend-code")
async def resend_verification_code(email: EmailStr):
    """
    Resend verification code
    """
    try:
        cognito_client.resend_confirmation_code(
            ClientId=CLIENT_ID,
            Username=email,
        )
        
        return {"message": "Verification code sent"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(email: EmailStr):
    """
    Initiate password reset
    """
    try:
        cognito_client.forgot_password(
            ClientId=CLIENT_ID,
            Username=email,
        )
        
        return {"message": "Password reset code sent to your email"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
async def reset_password(email: EmailStr, code: str, new_password: str):
    """
    Reset password with code
    """
    try:
        cognito_client.confirm_forgot_password(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code,
            Password=new_password,
        )
        
        return {"message": "Password reset successfully"}
    
    except cognito_client.exceptions.CodeMismatchException:
        raise HTTPException(status_code=400, detail="Invalid reset code")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_profile(user: dict = Depends(get_current_user)):
    """
    Get current user profile
    """
    return {
        "sub": user.get("sub"),
        "email": user.get("email"),
        "name": user.get("name"),
        "groups": user.get("cognito:groups", []),
        "email_verified": user.get("email_verified"),
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token
    """
    try:
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            }
        )
        
        return {
            "access_token": response['AuthenticationResult']['AccessToken'],
            "id_token": response['AuthenticationResult']['IdToken'],
            "token_type": "Bearer"
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
async def logout(access_token: str):
    """
    Logout user (revoke token)
    """
    try:
        cognito_client.global_sign_out(
            AccessToken=access_token
        )
        
        return {"message": "Logged out successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Admin endpoints
@router.get("/users", dependencies=[Depends(require_admin)])
async def list_users(limit: int = 60):
    """
    List all users (Admin only)
    """
    try:
        response = cognito_client.list_users(
            UserPoolId=USER_POOL_ID,
            Limit=limit
        )
        
        users = []
        for user in response['Users']:
            user_data = {
                'username': user['Username'],
                'status': user['UserStatus'],
                'enabled': user['Enabled'],
                'created': user['UserCreateDate'].isoformat(),
            }
            
            # Extract attributes
            for attr in user.get('Attributes', []):
                user_data[attr['Name']] = attr['Value']
            
            users.append(user_data)
        
        return {"users": users, "count": len(users)}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{email}/add-to-group", dependencies=[Depends(require_admin)])
async def add_user_to_group(email: str, group: str):
    """
    Add user to group (Admin only)
    """
    try:
        cognito_client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
            Username=email,
            GroupName=group
        )
        
        return {"message": f"User added to {group} group"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{email}", dependencies=[Depends(require_admin)])
async def delete_user(email: str):
    """
    Delete user (Admin only)
    """
    try:
        cognito_client.admin_delete_user(
            UserPoolId=USER_POOL_ID,
            Username=email
        )
        
        return {"message": "User deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
