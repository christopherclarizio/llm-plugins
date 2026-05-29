# LLM Agent Plugins
This repository contains the [Claude Code plugins](https://code.claude.com/docs/en/plugins) created by myself and others that I find worthwhile to use. The marketplace is at `plugins/.claude-plugin/marketplace.json`.

Plugins created by others and published via git are included in this repository in `/plugins/vended` as forks of the original repository via git subtrees. For attribution and notice of modification see: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

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

## DIYing
I setup this repository to centralize where the plugins I use are stored. The use of subtrees allows me to customize any plugin, including those authored by others, and pull upstream changes and contribute changes back upstream. If that aligns with your goals, consider making your own version of this repository — it is public so that you can do so.

### Use
If you do create your own version of this repository and want to follow my organization of it, these are the most important workflows.

**Create a plugin in this repository**:
Create a new plugin folder anywhere under `/plugins` with a `.claude-plugin/plugin.json` manifest, then add an entry pointing at its path to `plugins/.claude-plugin/marketplace.json`.

**Add a plugin from another repository**:
Add the repository with the plugin to `/plugins/vended` as a git subtree, then add an entry pointing at the plugin's path to `plugins/.claude-plugin/marketplace.json`. If you are adding a plugin authored by someone else, you need to fork their repository and add the fork as a subtree.
```sh
# add a plugin from a separate repository
git subtree add --prefix=plugins/vended/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Modify a plugin from another repository**:
Make the changes in a clone of the forked repository — not the subtree in `/plugins/vended` — and merge them, then pull the updated fork into this repository.
```sh
git clone https://github.com/<you-or-your-org>/<repo-name>.git && cd <repo-name>
# edit...
git commit -m "Customize plugin for my workflow" && git push origin main

# pull updated fork into this repository
git subtree pull --prefix=plugins/vended/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Retrieve upstream changes to a repository from a different author**:
Merge the changes into your fork of the original repository then pull the updated fork into this repository.
```sh
cd <repo-name> && git remote add upstream https://github.com/<original-author>/<repo-name>.git
git fetch upstream && git rebase upstream/main && git push origin main

# pull updated fork into this repository
git subtree pull --prefix=plugins/vended/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Contribute changes upstream to a repository from a different author**:
Create a feature branch in your fork of the original repository then create a pull request. Once your changes are merged upstream, pull the updated fork into this repository (see previous section).
```sh
git checkout -b <username>/<feature-or-change-description>
# edit...
git commit -m "Explanation for changes..." && git push origin <username>/<feature-or-change-description>
```
