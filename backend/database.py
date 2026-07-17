from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Where the database lives. Matches the user/password/name from docker-compose.yml.
# Format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL = "postgresql://slidetosale:devpassword@localhost:5432/slidetosale"

# The engine is the core connection to the database.
engine = create_engine(DATABASE_URL)

# A session is one conversation with the database. We ask for one whenever we read or write.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every table class we write will inherit from this Base, which ties them together.
Base = declarative_base()
