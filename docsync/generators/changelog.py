from pathlib import Path
from datetime import date
from typing import Optional

from docsync.diff.api_diff import DiffResult, ChangeType
from docsync.llm.client import LLMClient
from docsync.llm.prompts import CHANGELOG_SYSTEM, CHANGELOG_USER


class ChangelogGenerator:
    def __init__(self, llm_client: LLMClient, changelog_path: Path):
        self.llm = llm_client
        self.changelog_path = changelog_path

    def update(self, diff_result: DiffResult, dry_run: bool = False) -> Optional[str]:
        if not diff_result.has_changes():
            print("No changes for CHANGELOG.")
            return None

        changelog_content = self._read_current()
        changes_text = diff_result.to_text()

        user_prompt = CHANGELOG_USER.format(
            changelog_content=changelog_content,
            changes_text=changes_text,
        )

        print("Generating updated CHANGELOG via LLM...")
        result = self.llm.complete(CHANGELOG_SYSTEM, user_prompt)

        if result and not dry_run:
            self._write(result)
            print(f"Updated {self.changelog_path}")
        elif result and dry_run:
            print("=== DRY RUN — CHANGELOG would be updated ===")

        return result

    def update_simple(self, diff_result: DiffResult, dry_run: bool = False) -> Optional[str]:
        """Simple local changelog generation without LLM."""
        if not diff_result.has_changes():
            return None

        today = date.today().isoformat()
        lines = [f"## v0.1.0 ({today})", ""]

        has_adds = False
        has_removes = False
        has_modifies = False

        added = []
        removed = []
        modified = []

        for change in diff_result.changes:
            if change.type in (ChangeType.FUNCTION_ADDED, ChangeType.CLASS_ADDED,
                                ChangeType.METHOD_ADDED, ChangeType.PARAMETER_ADDED):
                added.append(change)
            elif change.type in (ChangeType.FUNCTION_REMOVED, ChangeType.CLASS_REMOVED,
                                  ChangeType.METHOD_REMOVED, ChangeType.PARAMETER_REMOVED):
                removed.append(change)
            else:
                modified.append(change)

        if added:
            lines.append("### Added")
            for c in added:
                lines.append(f"- {c.details}")
            lines.append("")

        if modified:
            lines.append("### Changed")
            for c in modified:
                lines.append(f"- {c.details}")
            lines.append("")

        if removed:
            lines.append("### Removed")
            for c in removed:
                lines.append(f"- {c.details}")
            lines.append("")

        changelog = "\n".join(lines)

        existing = self._read_current()
        full = changelog + "\n" + existing

        if not dry_run:
            self._write(full)
            print(f"Updated {self.changelog_path}")
        else:
            print("=== DRY RUN — CHANGELOG would be updated ===")

        return full

    def _read_current(self) -> str:
        if self.changelog_path.exists():
            return self.changelog_path.read_text(encoding="utf-8")
        return "# Changelog\n\n"

    def _write(self, content: str):
        self.changelog_path.parent.mkdir(parents=True, exist_ok=True)
        self.changelog_path.write_text(content, encoding="utf-8")
