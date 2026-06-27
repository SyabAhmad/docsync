import argparse
import sys
from pathlib import Path

from docsync.config import Config
from docsync.git.detector import GitDetector
from docsync.parser.ast_parser import ASTParser
from docsync.parser.snapshot import Snapshot
from docsync.diff.api_diff import APIDiff, DiffResult
from docsync.llm.client import LLMClient
from docsync.generators.readme_updater import READMEUpdater
from docsync.generators.changelog import ChangelogGenerator


def find_project_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".docsync").exists() or (parent / ".git").exists():
            return parent
    return cwd


def cmd_init(args):
    root = Path.cwd()
    config = Config(root)
    config.save()
    snapshot = Snapshot(config.config_dir)
    snapshot.save()
    print(f"Initialized DocSync in {root}")
    print(f"  Config:  {config.config_file}")
    print(f"  Snapshot: {snapshot.snapshot_file}")


def cmd_scan(args):
    root = Path.cwd()
    config = Config(root)
    snapshot = Snapshot(config.config_dir)
    detector = GitDetector(root)
    parser = ASTParser(root)

    changed_files = detector.get_changed_files(config.get("include_patterns", ["*.py"]))

    if not changed_files:
        print("No changed Python files detected.")
        return

    api_diff = APIDiff()
    all_changes = DiffResult()

    for rel_path in changed_files:
        file_api = parser.parse_file(rel_path)
        if file_api is None:
            continue
        old_api = snapshot.get_file(file_api.file_path)

        if snapshot.file_has_changed(file_api):
            print(f"  Scanning: {rel_path}")
            file_changes = api_diff.diff_file(old_api, file_api)
            all_changes.changes.extend(file_changes)

        snapshot.update_file(file_api)

    snapshot.save()
    print(f"Scanned {len(changed_files)} file(s). Snapshot saved.")

    if all_changes.has_changes():
        print("\nChanges detected:")
        print(all_changes.to_text())


def cmd_diff(args):
    root = Path.cwd()
    config = Config(root)
    snapshot = Snapshot(config.config_dir)
    detector = GitDetector(root)
    parser = ASTParser(root)
    api_diff = APIDiff()

    files = detector.get_changed_files(config.get("include_patterns", ["*.py"]))

    all_changes = DiffResult()

    for rel_path in files:
        current = parser.parse_file(rel_path)
        if current is None:
            continue
        previous = snapshot.get_file(current.file_path)
        changes = api_diff.diff_file(previous, current)
        all_changes.changes.extend(changes)

    print(all_changes.to_text())


def cmd_update(args):
    root = Path.cwd()
    config = Config(root)
    snapshot = Snapshot(config.config_dir)
    detector = GitDetector(root)
    parser = ASTParser(root)
    api_diff = APIDiff()

    files = detector.get_changed_files(config.get("include_patterns", ["*.py"]))

    all_changes = DiffResult()

    for rel_path in files:
        current = parser.parse_file(rel_path)
        if current is None:
            continue
        previous = snapshot.get_file(current.file_path)
        changes = api_diff.diff_file(previous, current)
        all_changes.changes.extend(changes)
        if not args.dry_run:
            snapshot.update_file(current)

    if not all_changes.has_changes():
        print("No API changes detected. Nothing to update.")
        return

    print(all_changes.to_text())

    llm = LLMClient(
        provider=config.get("llm_provider", "openai"),
        model=config.get("llm_model", "gpt-4o-mini"),
        temperature=config.get("llm_temperature", 0.3),
    )

    readme_path = root / config.get("readme_path", "README.md")
    changelog_path = root / config.get("changelog_path", "CHANGELOG.md")

    readme_updater = READMEUpdater(llm, readme_path)
    changelog = ChangelogGenerator(llm, changelog_path)

    print("\n--- README Update ---")
    readme_updater.update(all_changes, dry_run=args.dry_run)

    print("\n--- CHANGELOG Update ---")
    if args.simple:
        changelog.update_simple(all_changes, dry_run=args.dry_run)
    else:
        changelog.update(all_changes, dry_run=args.dry_run)

    if not args.dry_run:
        snapshot.save()
        print("\nDocumentation updated successfully.")
    else:
        print("\nDRY RUN — Snapshot not updated.")


def main():
    parser = argparse.ArgumentParser(
        description="DocSync — Keep documentation synchronized with code changes."
    )
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize DocSync in the current project")
    p_scan = sub.add_parser("scan", help="Scan changed files and update API snapshot")
    p_diff = sub.add_parser("diff", help="Show detected API changes")
    p_update = sub.add_parser("update", help="Regenerate documentation")
    p_update.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p_update.add_argument("--simple", action="store_true", help="Use simple local changelog (no LLM)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    commands = {
        "init": cmd_init,
        "scan": cmd_scan,
        "diff": cmd_diff,
        "update": cmd_update,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
