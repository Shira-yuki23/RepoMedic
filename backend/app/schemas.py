import re
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class DiagnosisRequest(BaseModel):
    mode: Literal['mock', 'live'] = 'mock'
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


class Evidence(BaseModel):
    path: str = Field(max_length=250)
    line: int = Field(ge=1)
    explanation: str = Field(min_length=1, max_length=1000)
    url: str = ''


class ModelReport(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=3000)
    steps: list[str] = Field(min_length=1, max_length=8)
    evidence: list[Evidence] = Field(default_factory=list, max_length=8)


class DiagnosisResponse(BaseModel):
    mode: str = 'mock'
    repo_url: str
    title: str
    summary: str
    steps: list[str]
    disclaimer: str
    evidence: list[Evidence] = Field(default_factory=list)
    files_reviewed: list[str] = Field(default_factory=list)
    commit: str | None = None
    model: str | None = None
