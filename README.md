# DocSync CLI

Keep project documentation automatically synchronized with code changes.

DocSync scans your Python project, parses the public API using AST, detects changes, and regenerates only the affected parts of your README and CHANGELOG via LLM.

---

## Installation

```bash
pip install docsync-cli
```

Requires Python 3.9+.

---

## Quick Start

```bash
# 1. Initialize in your project root
docsync init

# 2. Scan changed files and snapshot the API
docsync scan

# 3. Preview what changed
docsync diff

# 4. Regenerate README and CHANGELOG
docsync update
```

---

## Commands

### `docsync init`

Creates `.docsync/config.json` and `.docsync/api_snapshot.json` in your project root.

```bash
docsync init
```

### `docsync scan`

Finds changed Python files via Git, parses public functions/classes/methods with AST, compares against the previous snapshot, and saves the new snapshot.

```bash
docsync scan
```

### `docsync diff`

Shows detected API changes without modifying anything. Useful for review before running `update`.

```bash
docsync diff
```

Output:

```
## API Changes Detected

### src/predict.py
  [function_added] src/predict.py :: predict - Added `predict(image, threshold)`
  [parameter_added] src/predict.py :: predict - Parameter `threshold = 0.5` added
```

### `docsync update`

Sends detected changes to an LLM (Groq by default) to rewrite only the affected parts of README.md and CHANGELOG.md.

```bash
# Use LLM for both README and CHANGELOG
docsync update

# Use LLM for README, simple local changelog
docsync update --simple

# Preview changes without writing
docsync update --dry-run
```

---

## Configuration

Generated `.docsync/config.json`:

```json
{
  "version": "1.0",
  "llm_provider": "groq",
  "llm_model": "meta-llama/llama-4-scout-17b-16e-instruct",
  "llm_temperature": 0.3,
  "include_patterns": ["*.py"],
  "exclude_patterns": ["*test*", "*migration*", ".venv/*", "venv/*", "__pycache__/*"],
  "readme_path": "README.md",
  "changelog_path": "CHANGELOG.md"
}
```

| Key | Default | Description |
|---|---|---|
| `llm_provider` | `"groq"` | `"groq"` or `"openai"` |
| `llm_model` | `"meta-llama/llama-4-scout-17b-16e-instruct"` | Model name for the provider |
| `llm_temperature` | `0.3` | LLM temperature (lower = more deterministic) |
| `include_patterns` | `["*.py"]` | Glob patterns for files to scan |
| `exclude_patterns` | `[...]` | Glob patterns to exclude |
| `readme_path` | `"README.md"` | Path to README relative to project root |
| `changelog_path` | `"CHANGELOG.md"` | Path to CHANGELOG relative to project root |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes (if using Groq) | Get one at [console.groq.com](https://console.groq.com) |
| `OPENAI_API_KEY` | Yes (if using OpenAI) | Get one at [platform.openai.com](https://platform.openai.com) |

---

## How It Works

```
Developer changes code
        |
DocSync scans changed files (git diff)
        |
Parses Python code using AST
        |
Extracts public functions, classes, methods, parameters
        |
Compares with previous snapshot
        |
Detects added/removed/modified APIs
        |
Finds outdated README sections
        |
Uses LLM to rewrite only affected parts
        |
Updates README.md + CHANGELOG.md
```

### What Gets Tracked

- Public functions (`def func(...)`)
- Public classes (`class MyClass(...)`)
- Public methods (non-underscore methods on public classes)
- Function parameters and their defaults
- Return type annotations

Private members (starting with `_`) are ignored.

---

## Example

**Before — code change:**

```python
# src/model.py
def predict(image):
    """Run prediction on an image."""
    ...
```

**After — code change:**

```python
# src/model.py
def predict(image, threshold=0.5):
    """Run prediction with confidence threshold."""
    ...
```

**`docsync diff` output:**

```
[function_modified] src/model.py :: predict - File modified
[parameter_added] src/model.py :: predict - Parameter `threshold = 0.5` added
```

**`docsync update` rewrites README code examples** to reflect the new signature, and appends to CHANGELOG:

```markdown
## v0.2.0

### Changed
- Added `threshold` parameter to `predict()`.
```

---

## Project Status

Early-stage MVP. Currently supports Python projects with Git tracking.
