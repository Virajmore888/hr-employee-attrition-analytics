# Import required libraries
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env filesource /root/ml_env/bin/activate
load_dotenv()

# Function to create a database connection engine
def get_engine():

    # Read credentials from .env
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME")

    # Check if any credential is missing, stop early with clear error
    missing = [name for name, val in [
        ("DB_HOST", host), ("DB_PORT", port), ("DB_USER", user),
        ("DB_PASSWORD", password), ("DB_NAME", dbname)
    ] if not val]

    if missing:
        raise ValueError(f"Missing values in .env: {missing}")

    # Encode password so special characters do not break the connection string
    safe_password = quote_plus(password)

    # Build the connection string
    connection_string = f"mysql+pymysql://{user}:{safe_password}@{host}:{port}/{dbname}"

    # Create and return the engine
    engine = create_engine(connection_string)
    return engine


if __name__ == "__main__":
    engine = get_engine()
    with engine.connect() as conn:
        print("✅ Connection successful!")


