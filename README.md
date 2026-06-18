# Fresh 2 Skills

A Claude Code plugin marketplace providing Fresh 2 framework reference documentation, code examples, and migration guides.

## Installation

```bash
/plugin add marketplace d-jch/fresh2
/plugin install fresh2@fresh2
```

## What's included

- **Fresh 2 skill** — Complete API reference, code patterns, file routing, middleware, islands, signals, forms, Vite integration, deployment guides, and Fresh 1 → Fresh 2 migration guide
- **Reference documentation** — Detailed guides in `references/` covering concepts, advanced topics, plugins, deployment, testing, and examples

## Updating Fresh docs

Bundled reference docs are generated from Fresh upstream `docs/latest`:

```bash
python3 scripts/sync_fresh_docs.py --verbose
```

The script downloads Markdown from `freshframework/fresh`, rewrites `/docs/...` links for local plugin references, and replaces `skills/fresh2/references/`.

After installing the plugin, you can also ask Claude Code to run:

```text
/fresh2:update-docs
```

## License

MIT
