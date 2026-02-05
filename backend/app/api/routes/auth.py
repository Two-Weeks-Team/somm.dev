"""GitHub OAuth Authentication Routes

Security features:
- CSRF protection with state parameter
- JWT-based session management
- Secure cookie handling
"""

import os
import secrets
import httpx
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Cookie
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt

from app.database.repositories.user import UserRepository
from app.database.connection import get_database
from app.core.logging import logger
import sys

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://www.somm.dev")
# For OAuth callback, use backend URL directly (GitHub calls backend, not frontend)
BACKEND_URL = os.getenv("BACKEND_URL", "http://49.247.9.193:2621")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.get("/github")
async def github_login():
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

    state = secrets.token_urlsafe(32)

    github_oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=repo,user:email,read:user"
        f"&state={state}"
    )

    response = RedirectResponse(url=github_oauth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/github/callback")
async def github_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    oauth_state: Optional[str] = Cookie(None),
):
    response = RedirectResponse(url=f"{FRONTEND_URL}/login")
    response.delete_cookie("oauth_state")

    if error:
        response = RedirectResponse(url=f"{FRONTEND_URL}/login?error={error}")
        response.delete_cookie("oauth_state")
        return response

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    if not state or state != oauth_state:
        response = RedirectResponse(url=f"{FRONTEND_URL}/login?error=invalid_state")
        response.delete_cookie("oauth_state")
        return response

    try:
        logger.info("=" * 60)
        logger.info("[GitHub OAuth] Callback received")
        logger.info(f"[GitHub OAuth] BACKEND_URL: {BACKEND_URL}")
        logger.info(f"[GitHub OAuth] FRONTEND_URL: {FRONTEND_URL}")
        logger.info(
            f"[GitHub OAuth] Code: {code[:10]}..."
            if code
            else "[GitHub OAuth] Code: None"
        )
        logger.info("=" * 60)

        print(
            f"[OAUTH DEBUG] Callback received with code: {code[:10] if code else 'None'}...",
            file=sys.stderr,
        )

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                },
            )
            try:
                token_data = token_response.json()
                print(
                    f"[OAUTH DEBUG] Token response parsed: {token_data}",
                    file=sys.stderr,
                )
            except Exception as json_error:
                print(f"[OAUTH DEBUG] JSON parse error: {json_error}", file=sys.stderr)
                print(
                    f"[OAUTH DEBUG] Raw response: {token_response.text}",
                    file=sys.stderr,
                )
                raise

            if "access_token" not in token_data:
                error_msg = token_data.get("error_description", "OAuth failed")
                print(f"[OAUTH DEBUG] Error: {error_msg}", file=sys.stderr)
                response = RedirectResponse(
                    url=f"{FRONTEND_URL}/login?error={error_msg}"
                )
                response.delete_cookie("oauth_state")
                return response

            access_token = token_data["access_token"]
            print(
                f"[OAUTH DEBUG] Got access_token: {access_token[:10]}...",
                file=sys.stderr,
            )

            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            user_data = user_response.json()
            print(f"[OAUTH DEBUG] Got user_data: {user_data}", file=sys.stderr)

            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            emails = email_response.json()
            print(f"[OAUTH DEBUG] Got emails: {emails}", file=sys.stderr)

            primary_email = next(
                (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                user_data.get("email"),
            )
            print(f"[OAUTH DEBUG] Primary email: {primary_email}", file=sys.stderr)

            db = get_database()
            print("[OAUTH DEBUG] Got database", file=sys.stderr)

            user_repo = UserRepository(db)
            print("[OAUTH DEBUG] Got user_repo", file=sys.stderr)

            existing_user = await user_repo.get_by_github_id(str(user_data["id"]))
            print(f"[OAUTH DEBUG] Existing user: {existing_user}", file=sys.stderr)

            user_info = {
                "github_id": str(user_data["id"]),
                "username": user_data.get("login"),
                "email": primary_email,
                "avatar_url": user_data.get("avatar_url"),
                "github_access_token": access_token,
                "updated_at": datetime.utcnow(),
            }

            if existing_user:
                await user_repo.update(existing_user["_id"], user_info)
                user_id = existing_user["_id"]
                print(f"[OAUTH DEBUG] Updated user: {user_id}", file=sys.stderr)
            else:
                user_info["created_at"] = datetime.utcnow()
                user_id = await user_repo.create(user_info)
                print(f"[OAUTH DEBUG] Created user: {user_id}", file=sys.stderr)

            jwt_token = create_access_token(
                {
                    "sub": user_id,
                    "github_id": str(user_data["id"]),
                    "username": user_data.get("login"),
                }
            )
            print("[OAUTH DEBUG] Created JWT token", file=sys.stderr)

            response = RedirectResponse(
                url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}"
            )
            response.delete_cookie("oauth_state")
            print("[OAUTH DEBUG] Redirecting to frontend", file=sys.stderr)
            return response

    except httpx.HTTPError as e:
        print(f"[OAUTH DEBUG] HTTP Error: {e}", file=sys.stderr)
        response = RedirectResponse(url=f"{FRONTEND_URL}/login?error=github_api_error")
        response.delete_cookie("oauth_state")
        return response
    except Exception as e:
        print(f"[OAUTH DEBUG] Exception: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        response = RedirectResponse(url=f"{FRONTEND_URL}/login?error=internal_error")
        response.delete_cookie("oauth_state")
        return response


@router.get("/me")
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        db = get_database()
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user["_id"],
            "github_id": user.get("github_id"),
            "username": user.get("username"),
            "email": user.get("email"),
            "avatar_url": user.get("avatar_url"),
            "created_at": user.get("created_at"),
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}


@router.get("/refresh")
async def refresh_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False}
        )

        user_id = payload.get("sub")
        github_id = payload.get("github_id")
        username = payload.get("username")

        new_token = create_access_token(
            {"sub": user_id, "github_id": github_id, "username": username}
        )

        return {"access_token": new_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
