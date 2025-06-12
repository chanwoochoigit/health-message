import bcrypt
from .database import User, ProfileType


def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt."""
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def create_user(db, username: str, name: str, profile: ProfileType, password: str) -> User:
    password_hash = hash_password(password)
    user = User(
        username=username,
        name=name,
        profile=profile,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db, username: str, password: str) -> User | None:
    """Authenticate user by name and password."""
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return user
    except Exception as e:
        print(f"Authentication error: {e}")
    return None


def get_user_by_id(db, user_id: int) -> User | None:
    """Get user by ID."""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        print(f"Error getting user by ID: {e}")
    return None 