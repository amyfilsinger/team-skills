# Team Skills

Shared Claude Code skills for the ClassDojo team. Install any skill by dropping its folder into your project's `.claude/skills/` directory.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`salesforce-query`](salesforce-query/) | Query Salesforce data |
| [`what-did-i-forget`](what-did-i-forget/) | Surface forgotten context and tasks |
| [`skill-creator`](skill-creator/) | Create new Claude skills |
| [`qbr-monitoring`](qbr-monitoring/) | Monitor QBR metrics |
| [`slack-debrief`](slack-debrief/) | Scan Slack channels, rank top threads by reply count, produce paste-ready mrkdwn digest |

## How to Use a Skill

1. Copy the skill folder into your project's `.claude/skills/` directory
2. Reload Claude Code
3. Invoke with `/skill-name`

## Contributing

To add your own skill:
1. Fork or clone this repo
2. Add your skill folder (must contain a `SKILL.md`)
3. Update this README with a description
4. Open a PR
