import subprocess
import os
from pathlib import Path
from typing import List, Optional


class GitDetector:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def get_changed_files(self, patterns: Optional[List[str]] = None) -> List[Path]:
        if patterns is None:
            patterns = ["*.py"]
        try:
            return self._get_changed_git(patterns)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._get_changed_fs(patterns)

    def _get_changed_git(self, patterns: List[str]) -> List[Path]:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=self.repo_root, check=True
        )
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True, text=True, cwd=self.repo_root, check=True
        )
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, cwd=self.repo_root, check=True
        )
        all_files = set()
        for out in [result.stdout, staged.stdout, untracked.stdout]:
            for line in out.splitlines():
                line = line.strip()
                if line:
                    all_files.add(Path(line))
        return self._filter_matches(all_files, patterns)

    def _get_changed_fs(self, patterns: List[str]) -> List[Path]:
        all_files = []
        for root, dirs, files in os.walk(self.repo_root):
            for f in files:
                all_files.append(Path(root) / f)
        rel_files = {p.relative_to(self.repo_root) for p in all_files}
        return self._filter_matches(rel_files, patterns)

    def _filter_matches(self, files: set, patterns: List[str]) -> List[Path]:
        import fnmatch
        matched = []
        for f in files:
            f_str = str(f.as_posix())
            if any(fnmatch.fnmatch(f_str, p) for p in patterns):
                matched.append(f)
        return sorted(matched)

    def get_all_tracked_python_files(self) -> List[Path]:
        try:
            result = subprocess.run(
                ["git", "ls-files", "*.py"],
                capture_output=True, text=True, cwd=self.repo_root, check=True
            )
            return sorted({Path(line) for line in result.stdout.splitlines() if line.strip()})
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._get_changed_fs(["*.py"])
