"""
GitHub OAuth Authentication Routes
"""

import os
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://www.somm.dev")


@router.get("/auth/github")
async def github_login():
    """Redirect to GitHub OAuth login page"""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

    github_oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=user:email,repo,read:org"
        f"&redirect_uri={FRONTEND_URL}/api/auth/github/callback"
    )
    return RedirectResponse(url=github_oauth_url)


@router.get("/auth/github/callback")
async def github_callback(request: Request, code: str = None, error: str = None):
    """Handle GitHub OAuth callback"""
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": f"{FRONTEND_URL}/api/auth/github/callback",
                },
            )
            token_data = token_response.json()

            if "access_token" not in token_data:
                error_msg = token_data.get(
                    "error_description", "OAuth token exchange failed"
                )
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error={error_msg}")

            access_token = token_data["access_token"]

            # Get user info from GitHub
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            user_data = user_response.json()

            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/callback?token={access_token}&github_id={user_data.get('id')}"
            )

    except Exception as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={str(e)}")


@router.get("/auth/me")
async def get_current_user(request: Request):
    """Get current logged-in user"""
    return {"message": "Not implemented yet"}


@router.post("/auth/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}
