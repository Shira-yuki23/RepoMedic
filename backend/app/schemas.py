import re
from pydantic import BaseModel, Field, field_validator


class DiagnosisRequest(BaseModel):
    repo_url: str = Field(max_length=250)
    bug_description: str = Field(min_length=10, max_length=5000)

    @field_validator('repo_url')
    @classmethod
    def validate_repository(cls, value: str) -> str:
        value = value.strip().rstrip('/')
        if not re.fullmatch(r'https://github\.com/[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]+', value):
            raise ValueError('Use a GitHub repository URL: https://github.com/owner/repository')
        return value

    @field_validator('bug_description')
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError('Describe the bug in at least 10 characters.')
        return value


class DiagnosisResponse(BaseModel):
    mode: str = 'mock'
    repo_url: str
    title: str
    summary: str
    steps: list[str]
    disclaimer: str
