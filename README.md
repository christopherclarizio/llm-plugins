# LLM Agent Plugins
This repository contains [Claude Code plugins](https://code.claude.com/docs/en/plugins) that I find worthwhile to use.

All plugins that I did not create are included in this repository in `/vended`. Those plugins that were distributed via git are included as forks of the original repository via git subtrees. For attribution and notice of modification see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

## Installation 

**Add the marketplace**
```sh
/plugin marketplace add https://github.com/christopherclarizio/llm-plugins
```

**Install plugins**
```sh
/plugin install learning-goal
/plugin install learning-opportunities
# etc...
```

## Plugins
| Plugin | Description |
|--------|-------------|
| **`ed3d-00-getting-started`** | Getting started guide and onboarding for ed3d-plugins. Run `/getting-started` to see this README. |
| **`ed3d-plan-and-execute`** | Planning and execution workflows for Claude Code. Feed it a decent-sized task and it'll help you get it done in a sustainable and thought-through way |
| **`ed3d-house-style`** | House style for software development; Very Opinionated |
| **`ed3d-basic-agents`** | Core agents for general-purpose tasks (haiku, sonnet, opus). Other plugins expect this to exist |
| **`ed3d-research-agents`** | Agents for research across multiple data sources (codebase, internet, combined); other plugins expect this to exist |
| **`ed3d-extending-claude`** | Knowledge skills for extending Claude Code: plugins, commands, agents, skills, hooks, MCP servers. Other plugins expect this to exist |
| **`ed3d-playwright`**| Playwright automation with subagents |
| **`ed3d-hook-skill-reinforcement`** | UserPromptSubmit hook that reinforces the need to activate skills—helps make sure skills actually get used. Requires `ed3d-extending-claude` to work |
| **`ed3d-hook-claudemd-reminder`** | PostToolUse hook that reminds to update CLAUDE.md before committing |
| **`ed3d-hook-security-hardening`** | PreToolUse and PostToolUse hooks that catch secrets leakage patterns |
| **`ed3d-session-reflection`** | EXPERIMENTAL. Session awareness and conversation review tooling. Requires `ed3d-extending-claude` |
| **`learning-opportunities`** | Suggest learning exercises after completing architectural work |
| **`learning-opportunities-auto`** | Automatic version of **`learning-opportunities`** |
| **`orient`** | Create lessons to familiarize a repository and bodebase |
| **`learning-goal`** | Structured interactive goal setting |
| **`clarizio-documentation`** | Structured documentation of code and product |

### Use

**Create a plugin in this repository**:
Create a new plugin folder anywhere under  with a `.claude-plugin/plugin.json` manifest, then add an entry pointing at its path to `.claude-plugin/marketplace.json`.

**Add a plugin from another repository**:
Add the repository with the plugin to `/vended` as a git subtree, then add an entry pointing at the plugin's path to `.claude-plugin/marketplace.json`. If you are adding a plugin authored by someone else, you need to fork their repository and add the fork as a subtree.
```sh
# add a plugin from a separate repository
git subtree add --prefix=vended/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Modify a plugin from another repository**:
Make the changes in a clone of the forked repository — not the subtree in `/vended` — and merge them, then pull the updated fork into this repository.
```sh
git clone https://github.com/<you-or-your-org>/<repo-name>.git && cd <repo-name>
# edit...
git commit -m "Customize plugin for my workflow" && git push origin main

# pull updated fork into this repository
git subtree pull --prefix=vended/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Retrieve upstream changes to a repository from a different author**:
Merge the changes into your fork of the original repository then pull the updated fork into this repository.
```sh
cd <repo-name> && git remote add upstream https://github.com/<original-author>/<repo-name>.git
git fetch upstream && git rebase upstream/main && git push origin main

# pull updated fork into this repository
git subtree pull --prefix=vended/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Contribute changes upstream to a repository from a different author**:
Create a feature branch in your fork of the original repository then create a pull request. Once your changes are merged upstream, pull the updated fork into this repository (see previous section).
```sh
git checkout -b <username>/<feature-or-change-description>
# edit...
git commit -m "Explanation for changes..." && git push origin <username>/<feature-or-change-description>
```
