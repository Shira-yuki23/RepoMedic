import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str
    access_token: str

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv('NEBIUS_API_KEY', ''),
            model=os.getenv('NEBIUS_MODEL', 'nvidia/nemotron-3-super-120b-a12b'),
            base_url=os.getenv('NEBIUS_BASE_URL', 'https://api.tokenfactory.us-central1.nebius.com/v1').rstrip('/'),
            access_token=os.getenv('REPOMEDIC_ACCESS_TOKEN', ''),
        )

    @property
    def live_available(self):
        return bool(self.api_key and self.access_token)
