# Email Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"  # Change this
SMTP_PASSWORD = "your-app-password"     # Change this
EMAIL_FROM_ADDRESS = "noreply@yourdomain.com"

# API Configuration
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Your Project Name"

# Database Configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Upload Configuration
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Cache Configuration
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 3600  # 1 hour
