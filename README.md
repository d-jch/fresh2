# Fresh 2 Skills

A Claude Code plugin marketplace providing Fresh 2 framework reference documentation, code examples, and migration guides.

## Installation

### Claude Code

```bash
/plugin add marketplace d-jch/fresh2
/plugin install fresh2@fresh2
```

### Codex

This repository is also a Codex-compatible plugin. The local development
marketplace entry lives at `~/.agents/plugins/marketplace.json` and points at
`~/plugins/fresh2`, which is a symlink back to this repository.

Install it in Codex with:

```bash
codex plugin add fresh2@personal
```

After changing plugin metadata or bundled docs, reinstall it and start a new
Codex thread so the updated skill metadata is loaded.

## What's included

- **Fresh 2 skill** — Complete API reference, code patterns, file routing, middleware, islands, signals, forms, Vite integration, deployment guides, and Fresh 1 → Fresh 2 migration guide
- **Reference documentation** — Detailed guides in `references/` covering concepts, advanced topics, plugins, deployment, testing, and examples

## Updating Fresh docs

Bundled reference docs are generated from Fresh upstream `docs/latest`:

```bash
python3 scripts/sync_fresh_docs.py --verbose
```

The script downloads Markdown from `freshframework/fresh`, rewrites `/docs/...` links for local plugin references, and replaces `skills/fresh2/references/`.

After installing the plugin in Claude Code, you can also run:

```text
/fresh2:update-docs
```

For Codex/local development, run the script directly from the plugin root:

```bash
python3 scripts/sync_fresh_docs.py --verbose
python3 -m unittest discover -s tests
```

## License

MIT
