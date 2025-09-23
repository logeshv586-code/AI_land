from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List, Optional

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserCreate, UserResponse, Token, TokenData, UserUpdate
from app.core.config import settings
from app.services.agent_assignment_service import AgentAssignmentService

router = APIRouter()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        user_role=user.user_role,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        company_name=user.company_name,
        license_number=user.license_number,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Auto-assign agents for buyers and sellers
    if user.user_role in [UserRole.BUYER, UserRole.SELLER]:
        agent_service = AgentAssignmentService(db)
        agent_service.auto_assign_agents_on_registration(db_user.id)

    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user fields if provided
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

# Role-based access control functions
def require_role(allowed_roles: list):
    """Decorator to require specific user roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

def require_buyer(current_user: User = Depends(get_current_user)):
    """Require buyer role"""
    if current_user.user_role != UserRole.BUYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Buyer role required."
        )
    return current_user

def require_seller(current_user: User = Depends(get_current_user)):
    """Require seller role"""
    if current_user.user_role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Seller role required."
        )
    return current_user

def require_buyer_agent(current_user: User = Depends(get_current_user)):
    """Require buyer agent role"""
    if current_user.user_role != UserRole.BUYER_AGENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Buyer agent role required."
        )
    return current_user

def require_seller_agent(current_user: User = Depends(get_current_user)):
    """Require seller agent role"""
    if current_user.user_role != UserRole.SELLER_AGENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Seller agent role required."
        )
    return current_user

def require_agent(current_user: User = Depends(get_current_user)):
    """Require any agent role"""
    if current_user.user_role not in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agent role required."
        )
    return current_user

def require_seller_or_agent(current_user: User = Depends(get_current_user)):
    """Require seller or seller agent role"""
    if current_user.user_role not in [UserRole.SELLER, UserRole.SELLER_AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Seller or seller agent role required."
        )
    return current_user

def require_active_subscription(current_user: User = Depends(get_current_user)):
    """Require active subscription for agents"""
    if current_user.user_role in [UserRole.BUYER_AGENT, UserRole.SELLER_AGENT]:
        if current_user.subscription_status != "active":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Active subscription required for agent features."
            )
    return current_user

# Agent Assignment Endpoints

@router.get("/agents/buyer-agents", response_model=List[UserResponse])
async def get_available_buyer_agents(
    location_area: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available buyer agents"""
    agent_service = AgentAssignmentService(db)
    agents = agent_service.get_available_buyer_agents(location_area)
    return agents

@router.get("/agents/seller-agents", response_model=List[UserResponse])
async def get_available_seller_agents(
    location_area: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available seller agents"""
    agent_service = AgentAssignmentService(db)
    agents = agent_service.get_available_seller_agents(location_area)
    return agents

@router.post("/assign-buyer-agent/{buyer_id}")
async def assign_buyer_agent(
    buyer_id: int,
    agent_id: Optional[int] = None,
    location_area: Optional[str] = None,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Assign a buyer agent to a buyer (only agents can do this)"""
    agent_service = AgentAssignmentService(db)
    assigned_agent = agent_service.assign_buyer_agent(buyer_id, agent_id, location_area)
    
    if not assigned_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available buyer agents found or buyer not found"
        )
    
    return {"message": "Buyer agent assigned successfully", "agent": assigned_agent}

@router.post("/assign-seller-agent/{seller_id}")
async def assign_seller_agent(
    seller_id: int,
    agent_id: Optional[int] = None,
    location_area: Optional[str] = None,
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Assign a seller agent to a seller (only agents can do this)"""
    agent_service = AgentAssignmentService(db)
    assigned_agent = agent_service.assign_seller_agent(seller_id, agent_id, location_area)
    
    if not assigned_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available seller agents found or seller not found"
        )
    
    return {"message": "Seller agent assigned successfully", "agent": assigned_agent}

@router.get("/my-clients", response_model=List[UserResponse])
async def get_my_clients(
    current_user: User = Depends(require_agent),
    db: Session = Depends(get_db)
):
    """Get list of clients for the current agent"""
    agent_service = AgentAssignmentService(db)
    clients = agent_service.get_client_list(current_user.id)
    return clients

@router.get("/can-communicate/{user_id}")
async def check_communication_permission(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user can communicate with specified user"""
    agent_service = AgentAssignmentService(db)
    can_communicate = agent_service.can_communicate(current_user.id, user_id)
    
    return {
        "can_communicate": can_communicate,
        "communication_path": agent_service.get_communication_path(current_user.id, user_id)
    }