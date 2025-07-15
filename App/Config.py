
import os

# Configuration settings for the Flask application
#  Defines a base configuration class with default/shared settings.
class Config:
    # General configuration
    # SECRET_KEY is used by Flask for session management and CSRF protection.
    # Loads the secret key used for session signing and security from the .env variable JWT_SECRET_KEY.
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret")
    #  Disables SQLAlchemy's event system for tracking modifications — this saves memory and avoids warnings.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #  This is the actual key used to sign/verify JWT tokens. Redundant with SECRET_KEY above, but separated for clarity.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret")

# Subclass of Config for development settings.
class Development(Config):
    # Enables debug mode — you get useful error messages and live reloading.
    DEBUG = True
    #  Loads the development database URI from .env. Which is PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///dev.db")

# Subclass of Config for testing settings.
class Testing(Config):
    #  Enables Flask’s testing mode (special behavior like exceptions being propagated)
    TESTING = True
    # Uses an in-memory SQLite database — fast, temporary, and good for isolated unit tests.
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    # Ensures that app context is cleared after each test case (clean state between tests).
    PRESERVE_CONTEXT_ON_EXCEPTION = False

# Subclass for production environment.
class Production(Config):
    #  Disables debug mode for security and performance.
    DEBUG = False
    #  Loads the production database URI from .env. Which is PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod.db")


# Dictionary to map environment names to their respective configuration classes.
# A dictionary mapping string names to config classes. This lets you pass "development" or "testing" to the create_app() function and automatically get the correct settings.
config_by_name = {
    "development": Development,
    "testing": Testing,
    "production": Production
}
