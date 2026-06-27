# Changelog

## v0.1.1 (2026-06-27)

### Fixed
- LLM client now uses `requests` library for reliable HTTPS connections on Windows
- Config defaults set to Groq provider with `meta-llama/llama-4-scout-17b-16e-instruct` model
- Schema fixes for PyPI publishing

### Added
- Comprehensive README with full command reference, configuration docs, and walkthrough

## v0.1.0 (2026-06-27)

### Added
- `docsync init` — project initialization
- `docsync scan` — Git-based change detection and AST parsing
- `docsync diff` — API diff display
- `docsync update` — LLM-powered README and CHANGELOG regeneration
- Groq and OpenAI LLM provider support
- JSON snapshot storage for API state tracking
