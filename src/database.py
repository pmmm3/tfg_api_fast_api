from sqlmodel import create_engine, SQLModel

DATABASE_URL = "postgresql://pmoreno:Psiquiatrico1@localhost:5432/tfg_pmoreno"

# Create database engine
engine = create_engine(DATABASE_URL)

# Perform database migrations
SQLModel.metadata.create_all(engine)
