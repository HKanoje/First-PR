import os
import time
from fastapi import APIRouter, Depends, Response, Request, HTTPException
from jose import jwt, JWTError
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import get_db, Base, engine
from models.user import User

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

# Create tables (once) on import
Base.metadata.create_all(bind=engine)

oauth = OAuth()
oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)

JWT_SECRET = os.getenv("JWT_SECRET", "dev")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


def make_jwt(user_id: int) -> str:
    """Create a JWT token for a user."""
    payload = {"sub": str(user_id), "exp": int(time.time()) + 60 * 60 * 24 * 7}  # 7 days
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def get_current_user(request: Request, db: Session) -> User | None:
    """Extract and validate JWT from cookies."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return db.query(User).get(int(data["sub"]))
    except JWTError:
        return None


@router.get("/github/login")
async def github_login(request: Request):
    """Initiate GitHub OAuth login."""
    redirect_uri = os.getenv("OAUTH_REDIRECT_URL")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request, response: Response, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback."""
    token = await oauth.github.authorize_access_token(request)
    gh_user = (await oauth.github.get("user", token=token)).json()

    gh_id = gh_user.get("id")
    username = gh_user.get("login")
    avatar = gh_user.get("avatar_url")
    name = gh_user.get("name")
    
    # Best-effort email retrieval
    email = gh_user.get("email")
    if not email:
        emails = (await oauth.github.get("user/emails", token=token)).json()
        pri = next((e["email"] for e in emails if e.get("primary")), None)
        email = pri or (emails[0]["email"] if emails else None)

    # Create or update user
    user = db.query(User).filter(User.github_id == gh_id).first()
    if not user:
        user = User(github_id=gh_id, username=username, name=name, email=email, avatar_url=avatar)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Keep profile fresh
        user.username = username
        user.name = name
        user.email = email
        user.avatar_url = avatar
        db.commit()

    # Create JWT and set cookie
    jwt_token = make_jwt(user.id)
    response = RedirectResponse(url=f"{FRONTEND_ORIGIN}/")
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/"
    )
    return response


@router.post("/logout")
def logout():
    """Logout user by deleting JWT cookie."""
    resp = Response(status_code=204)
    resp.delete_cookie("access_token", path="/")
    return resp


@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    """Get current user profile."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
    }


@router.put("/me")
def update_me(payload: dict, request: Request, db: Session = Depends(get_db)):
    """Update current user profile."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Allow updating specific fields
    user.name = payload.get("name", user.name)
    user.bio = payload.get("bio", user.bio)
    db.commit()
    return {"ok": True}
