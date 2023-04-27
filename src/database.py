from sqlmodel import create_engine, SQLModel
from sqlmodel.pool import StaticPool

DATABASE_URL = "postgresql://pmoreno@localhost:5432/tfg_pmoreno"

# Create database engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

# Perform database migrations
SQLModel.metadata.create_all(engine)
