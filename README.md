# DocSync CLI

Keep project documentation automatically synchronized with code changes.

```bash
docsync init      # Initialize project
docsync scan      # Scan and create/update API snapshot
docsync diff      # Show detected API changes
docsync update    # Regenerate documentation
```

Requires `GROQ_API_KEY` (or `OPENAI_API_KEY`) environment variable for LLM-powered updates.
