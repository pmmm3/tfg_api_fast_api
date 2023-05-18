from sqlmodel import create_engine

import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "")
DB_PWD = os.getenv("DB_PASSWORD", "")
DB_DEFAULT_DB = os.getenv("DB_DEFAULT_DB", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")

smtp_server = os.getenv("SMTP_SERVER", "")
smtp_port = os.getenv("SMTP_PORT", "")
smtp_username = os.getenv("SMTP_USERNAME", "")
smtp_password = os.getenv("SMTP_PASSWORD", "")

# Database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_DEFAULT_DB}"

# Create database engine
engine = create_engine(DATABASE_URL)

# Perform database migrations
# SQLModel.metadata.create_all(engine)
