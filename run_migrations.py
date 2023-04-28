from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

load_dotenv()

# Load the Alembic configuration from alembic.ini
config = Config("alembic.ini")

# Perform the database migrations using the Alembic configuration
command.upgrade(config, "head")
