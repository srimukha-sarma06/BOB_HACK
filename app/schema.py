from pydantic import BaseModel

class RepoCreate(BaseModel):
    repo_link: str
    repo_name: str
    repo_description: str

class RepoOutput(BaseModel):
    id: int
    repo_link: str
    repo_name: str
    repo_description: str
    architecture_summary: str

    class Config:
        from_attributes = True