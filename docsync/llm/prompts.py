README_UPDATE_SYSTEM = """You are a technical documentation expert. Your task is to update README.md documentation
based on API changes detected in a Python project. Follow these rules:
1. Only modify sections that are affected by the changes.
2. Keep the existing tone, style, and formatting.
3. Update code examples to reflect new function signatures.
4. Add documentation for new functions/classes if relevant.
5. Never remove documentation for functions that still exist.
6. Output the COMPLETE updated README.md content."""

README_UPDATE_USER = """## Current README.md

{readme_content}

## API Changes Detected

{changes_text}

## Instructions

Update the README.md to reflect the API changes above. Focus on:
- Updating function signatures in code examples
- Adding usage examples for new parameters
- Documenting new public functions/classes
- Removing references to removed APIs
- Updating any parameter descriptions affected by changes

Return the COMPLETE updated README.md content."""

CHANGELOG_SYSTEM = """You are a release notes writer. Generate a concise changelog entry
based on API changes detected in a Python project. Follow semantic versioning principles."""

CHANGELOG_USER = """## Previous Changelog

{changelog_content}

## API Changes

{changes_text}

## Task

Generate an updated CHANGELOG.md. Add a new version entry at the top with:
- A version number (increment appropriately based on changes)
- Today's date
- Changed/Added/Removed sections for each API change

Return the COMPLETE updated CHANGELOG.md content."""
