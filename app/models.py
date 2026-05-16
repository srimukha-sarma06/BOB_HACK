from sqlalchemy import Column, Integer, String, Text
from .database import Base


class RepoStorage(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True, index=True)

    repo_link = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    repo_description = Column(Text)

    architecture_summary = Column(Text)