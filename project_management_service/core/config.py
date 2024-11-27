import os
from dotenv import load_dotenv, find_dotenv
from urllib.parse import quote_plus

# Explicitly specify the path to the .env file
env_path = find_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=env_path)

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 3000))

    MONGO_USER: str = os.getenv("MONGO_USER")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD")
    MONGO_HOST: str = os.getenv("MONGO_HOST")
    MONGO_PORT: str = os.getenv("MONGO_PORT")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME")
    MONGO_READ_PREFERENCE: str = os.getenv("MONGO_READ_PREFERENCE", "primaryPreferred")
    MONGO_AUTH_SOURCE: str = os.getenv("MONGO_AUTH_SOURCE")

    if MONGO_PASSWORD is not None:
        # URL encode the password
        MONGO_PASSWORD_ENCODED: str = quote_plus(MONGO_PASSWORD)
    else:
        raise ValueError("MONGO_PASSWORD must be set in the environment variables")

    # Construct the MongoDB connection string
    MONGO_URL: str = (
        f"mongodb://{MONGO_USER}:{MONGO_PASSWORD_ENCODED}@{MONGO_HOST}:{MONGO_PORT}/"
        f"{MONGO_DB_NAME}?readPreference={MONGO_READ_PREFERENCE}&authSource={MONGO_AUTH_SOURCE}"
    )

settings = Settings()
