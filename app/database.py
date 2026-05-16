from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Your Postgres connection string
sqlalchemy_database_url = 'postgresql://repouser:bob123@localhost:5432/RepoStorage'

engine = create_engine(sqlalchemy_database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()