# Skills

A collection of Agent Skills for AI coding assistants.

## Available Skills

| Skill | Description |
|-------|-------------|
| [academic-research](./academic-research/) | Systematic academic literature search with source prioritization and APA 7th edition citations |
| [apa-style-citation](./apa-style-citation/) | Generate, format, and validate academic citations following APA 7th Edition guidelines |

## Installation

### Using the Skills CLI (recommended)

```bash
npx skills add romanmesicek/skills --skill academic-research
npx skills add romanmesicek/skills --skill apa-style-citation
```

### Manual Installation

**Claude Code:**
```bash
cp -r academic-research ~/.claude/skills/
cp -r apa-style-citation ~/.claude/skills/
```

**Claude.ai:**
1. Download the skill folder as ZIP
2. Go to Settings > Capabilities > Skills
3. Upload the ZIP file

## Compatibility

Skills follow the [Agent Skills Specification](https://agentskills.io/specification) and work with:
- Claude Code
- Claude.ai (with code execution enabled)
- Cursor
- Windsurf
- Other compatible agents

## License

MIT License - see [LICENSE](./LICENSE)

## Author

Roman Mesicek
