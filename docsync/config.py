import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "version": "1.0",
    "llm_provider": "groq",
    "llm_model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "llm_temperature": 0.3,
    "include_patterns": ["*.py"],
    "exclude_patterns": ["*test*", "*migration*", ".venv/*", "venv/*", "__pycache__/*"],
    "snapshot_dir": ".docsync",
    "readme_path": "README.md",
    "changelog_path": "CHANGELOG.md",
    "github_base_url": "",
}


class Config:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / ".docsync"
        self.config_file = self.config_dir / "config.json"
        self._data = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self._data.update(json.load(f))

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self._data, f, indent=2)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)
