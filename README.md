# DocSync CLI

**Keep your Python project documentation automatically synchronized with code changes.**

DocSync scans your Python files using Git, parses public APIs with AST, detects changes, and rewrites only the affected parts of your README and CHANGELOG via LLM (Groq or OpenAI).

---

## Installation

```bash
pip install docsync-cli
```

Requires Python 3.9+. Set `GROQ_API_KEY` or `OPENAI_API_KEY` in your environment.

---

## Quick Start

```bash
# 1. Initialize in your project root
docsync init

# 2. Make some code changes...

# 3. See what API changes were detected
docsync diff

# 4. Regenerate README and CHANGELOG automatically
docsync update
```

---

## Commands

### `docsync init`

Creates the `.docsync/` directory with configuration and snapshot files.

```bash
docsync init
```

### `docsync scan`

Scans changed Python files, parses their public API, and updates the snapshot. Useful after pulling changes or switching branches.

```bash
docsync scan
```

### `docsync diff`

Compares your working tree against the last saved snapshot and displays added, removed, or modified APIs.

```bash
docsync diff
```

Example output:

```
## API Changes Detected

### src/predict.py
  [parameter_added] src/predict.py :: predict - Parameter `threshold = 0.5` added
  [function_added] src/predict.py :: batch_predict - Added `batch_predict(images)`
```

### `docsync update`

Sends detected changes to an LLM to rewrite only the affected parts of your docs.

```bash
# Full LLM mode — rewrites both README and CHANGELOG
docsync update

# Local mode — simple changelog generation (no API key needed)
docsync update --simple

# Preview changes without writing anything
docsync update --dry-run
```

---

## Configuration

Generated `.docsync/config.json`:

```json
{
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
| `llm_model` | `"meta-llama/llama-4-scout-17b-16e-instruct"` | Model name |
| `llm_temperature` | `0.3` | LLM temperature |
| `include_patterns` | `["*.py"]` | Glob patterns for files to scan |
| `exclude_patterns` | `[...]` | Glob patterns to exclude |
| `readme_path` | `"README.md"` | Path to README |
| `changelog_path` | `"CHANGELOG.md"` | Path to CHANGELOG |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | For Groq | Get one at [console.groq.com](https://console.groq.com) |
| `OPENAI_API_KEY` | For OpenAI | Get one at [platform.openai.com](https://platform.openai.com) |

---

## How It Works

```
You change Python code
        |
Git detects changed files
        |
AST parser extracts public API:
  - Functions (name, params, defaults, return type)
  - Classes (name, bases, methods)
        |
Diff engine compares against snapshot
        |
LLM rewrites only outdated sections
        |
README.md + CHANGELOG.md updated
```

### What's tracked

- **Public functions** — `def func(...)` without leading `_`
- **Public classes** — `class MyClass(...)` without leading `_`
- **Public methods** — non-underscore methods on public classes
- **Parameters** — names, defaults, and return annotations

Private/dunder members (`_`, `__`) are ignored.

---

## Example Walkthrough

**Before — your code:**

```python
def predict(image):
    """Run prediction."""
    ...
```

**After — you add a parameter:**

```python
def predict(image, threshold=0.5):
    """Run prediction with confidence threshold."""
    ...
```

**Run `docsync diff`:**

```
[parameter_added] :: predict - Parameter `threshold = 0.5` added
```

**Run `docsync update`** — it updates code examples in your README and appends to CHANGELOG:

```markdown
## v0.2.0

### Changed
- Added `threshold` parameter to `predict()`.
```

---

## Real Project Example

```bash
# Initialize tracking
docsync init

# Edit your Python code...
# Add new functions, change parameters, etc.

# See what changed
docsync diff

# If changes look good, regenerate docs
docsync update --simple
# Or with LLM for smarter rewrites
docsync update
```

---

## Limitations

- **Python only** (MVP scope)
- **Git required** for change detection
- **LLM mode** needs a valid API key
- Best suited for library-style projects with clear public APIs

---

## License

MIT
