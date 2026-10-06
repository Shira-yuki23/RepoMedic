import json
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import quote
import httpx
from fastapi import HTTPException

MAX_FILES = 12
MAX_FILE_BYTES = 8_000
MAX_TOTAL_BYTES = 60_000
EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.toml', '.yaml', '.yml', '.md', '.go', '.rs', '.java', '.css'}
EXCLUDED = {'node_modules', 'dist', 'build', 'vendor', '.git', '.venv', '__pycache__'}


@dataclass
class RepositorySnapshot:
    commit: str
    files: dict[str, str]
    partial: bool


async def limited_get(client: httpx.AsyncClient, url: str, limit: int) -> bytes:
    async with client.stream('GET', url) as response:
        if response.status_code == 404:
            raise HTTPException(404, 'Repository or file is unavailable. Use an existing public GitHub repository.')
        if response.status_code in (403, 429):
            raise HTTPException(429, 'GitHub request limit reached. Please try again later.')
        if response.status_code != 200:
            raise HTTPException(502, 'GitHub could not provide repository content.')
        content = bytearray()
        async for chunk in response.aiter_bytes():
            content.extend(chunk)
            if len(content) > limit:
                raise HTTPException(413, 'Repository content exceeded the retrieval limit.')
        return bytes(content)


async def read_repository(client: httpx.AsyncClient, repo_url: str, bug: str) -> RepositorySnapshot:
    owner, repo = repo_url.removesuffix('.git').split('/')[-2:]
    root = f'https://api.github.com/repos/{owner}/{repo}'
    metadata = json.loads(await limited_get(client, root, 100_000))
    branch = quote(metadata['default_branch'], safe='')
    commit_data = json.loads(await limited_get(client, f'{root}/commits/{branch}', 500_000))
    commit = commit_data['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise HTTPException(502, 'GitHub returned an invalid commit reference.')
    tree = json.loads(await limited_get(client, f'{root}/git/trees/{commit}?recursive=1', 2_000_000))
    candidates = []
    words = set(re.findall(r'[a-z0-9_]{3,}', bug.lower()))
    for item in tree.get('tree', []):
        path = PurePosixPath(item.get('path', ''))
        if item.get('type') != 'blob' or item.get('mode') == '120000' or not 0 < item.get('size', 0) <= MAX_FILE_BYTES:
            continue
        if path.suffix.lower() not in EXTENSIONS or any(part in EXCLUDED or part.startswith('.') for part in path.parts):
            continue
        if 'lock' in path.name.lower() or path.name.endswith('.min.js'):
            continue
        score = sum(word in str(path).lower() for word in words)
        score += 2 if path.suffix.lower() in {'.py', '.js', '.jsx', '.ts', '.tsx'} else 0
        candidates.append((score, str(path)))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    files = {}
    size = 0
    for _, path in candidates[:MAX_FILES]:
        url = f'https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{quote(path, safe="/")}'
        raw = await limited_get(client, url, MAX_FILE_BYTES)
        if size + len(raw) > MAX_TOTAL_BYTES:
            break
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        if '\x00' in content:
            continue
        files[path] = content
        size += len(raw)
    if not files:
        raise HTTPException(422, 'No supported source files were found within the demo retrieval limits.')
    return RepositorySnapshot(commit, files, bool(tree.get('truncated')) or len(files) < len(candidates))
