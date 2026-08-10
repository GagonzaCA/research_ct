# Contributing

## Code style

- **Black** formatter, line length 100
- **Google-style docstrings** on all public APIs
- **Type hints** on all function signatures
- **Pascal_Case_With_Underscores** for classes

## Before committing

```bash
black src/ tests/
mypy src/
pytest
```

## Adding documentation

1. Write your markdown file in `docs/` or `docs/guides/`
2. Add it to the `nav:` tree in `mkdocs.yml`
3. Run `mkdocs serve` to preview locally
4. Run `mkdocs build` to generate the static site
