from datetime import timedelta

# JWT Settings
JWT_SECRET_KEY = "your-secret-key"  # Change this in production!
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Settings
MIN_PASSWORD_LENGTH = 8
REQUIRED_PASSWORD_CHARS = {
    "uppercase": 1,
    "lowercase": 1,
    "numbers": 1,
    "special": 1
}

# Rate Limiting
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = timedelta(minutes=15)
MAX_PASSWORD_RESET_ATTEMPTS = 3
PASSWORD_RESET_WINDOW = timedelta(hours=24)

# Token Expiration
VERIFICATION_TOKEN_EXPIRE_HOURS = 24
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1

# Session Settings
SESSION_COOKIE_NAME = "session_id"
SESSION_EXPIRE_MINUTES = 60
