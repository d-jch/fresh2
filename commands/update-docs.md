---
description: Refresh bundled Fresh 2 reference docs from upstream Fresh docs/latest
allowed-tools: ["Bash"]
---

Run the Fresh documentation sync script from this plugin's root:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync_fresh_docs.py" \
  --destination "${CLAUDE_PLUGIN_ROOT}/skills/fresh2/references" \
  --verbose
```

Then verify the refreshed references:

```bash
python3 -m unittest discover -s "${CLAUDE_PLUGIN_ROOT}/tests"
```

Review the resulting `skills/fresh2/references/` changes before committing them.
