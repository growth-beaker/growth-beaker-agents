# growth-beaker-agents

Claude Code plugin marketplace for Growth Beaker.

## Install

From any Claude Code session — no clone required:

```
/plugin marketplace add growth-beaker/growth-beaker-agents
/plugin install coherence-standards@growth-beaker
```

The marketplace is fetched straight from GitHub. Access is via your existing git
credentials, so you need read access to this repo (`gh auth login` or an SSH key
configured for github.com).

To pick up new plugins or updates later:

```
/plugin marketplace update growth-beaker
```

### Local development

Working on a plugin in this repo? Point the marketplace at your checkout instead:

```
/plugin marketplace add /path/to/growth-beaker-agents
```

## Plugins

| Plugin | What it does |
|---|---|
| [`coherence-standards`](./coherence-standards) | Extract a repo's engineering standards from its own artifacts, review them in ~40 decisions, compile them into `AGENTS.md`. |
