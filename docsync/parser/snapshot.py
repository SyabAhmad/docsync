import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from docsync.parser.ast_parser import FileAPI


class Snapshot:
    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir
        self.snapshot_file = snapshot_dir / "api_snapshot.json"
        self._data: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.snapshot_file.exists():
            with open(self.snapshot_file) as f:
                self._data = json.load(f)

    def save(self):
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        with open(self.snapshot_file, "w") as f:
            json.dump(self._data, f, indent=2)

    def update_file(self, file_api: FileAPI):
        self._data[file_api.file_path] = file_api.to_dict()

    def remove_file(self, file_path: str):
        self._data.pop(file_path, None)

    def get_file(self, file_path: str) -> Optional[FileAPI]:
        data = self._data.get(file_path)
        if data:
            return FileAPI.from_dict(data)
        return None

    def get_all_files(self) -> Dict[str, FileAPI]:
        return {
            path: FileAPI.from_dict(data)
            for path, data in self._data.items()
        }

    def file_has_changed(self, file_api: FileAPI) -> bool:
        existing = self._data.get(file_api.file_path)
        if existing is None:
            return True
        return existing.get("file_hash") != file_api.file_hash

    def clear(self):
        self._data.clear()
