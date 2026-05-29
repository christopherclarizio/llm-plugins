# LLM Agent Skills
This repository contains the [skills](https://adobe.enterprise.slack.com/archives/C0525NXAHPV) created by myself and others that I find worthwhile to use. The combined, flattened, canonical set of those skills is in `/skills`.

Skills created by others and published via git are included in this repository in `/sources` as forks of the original repository via git subtrees. For attribution and notice of modification see: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

## DIYing
I setup this repository to centralize where the skills I use are stored. The overhead of subtrees, flattening, etc. are all in order to also allow me to: customize any skill, including those authored by others, and pull upstream changes and contribute changes back upstream. 

If that aligns with your goals, ocnsider making your own version of this repository. I will not accept contributions to this repository as it is meant to be for me. It is public should you want to take inspiration from it.

The mental model to keep mind is that `/sources` is your "local" version of the skills, any changes you want to make should be done there, and`/skills` is the "published" version of the skills and should only be changed by `/scripts/build`. There's really not more to it than that.

### Use
If you do create your own version of this repository and want to follow my organization of it. These are the most important workflows.

**Create a skill in this repository**:
Create a new skill folder in `/sources` and the content there.
```sh
# create new skill in this repository
mkdir -p sources/my-skill && echo "my new skill" > sources/my-skill/my-skill.md
```

**Add a skill from another repository**:
Add the repository with the skill to `/sources` as a git subtree and update the flattening configuration. If you are adding a skill authored by someone else, you need to fork their rpeository and add the fork as a subtree.
```sh
# create new skill in a separate repository
git subtree add --preifx=sources/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
```

**Modify a skill from another repository**:
Make the changes in a clone of the forked repository - not the subtree in `/sources` - and merge them then pull the updated fork into this repository.
```sh
git clone https://github.com/<you-or-your-org>/<repo-name>.git && cd <repo-name>
# edit...
git commit -m "Customize skill for my workflow" && git push origin main

# pull updated fork into this repository and rebuild
git subtree pull --preifx=sources/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
./scripts/build
```

**Retrieve upstream changes to a repository from a different author**:
Merge the changes into your fork of the original repository then pull the updated fork into this repository.
```sh
cd <repo-name> && git remote add upstream https://github.com/<original-author>/<repo-name>.git
git fetch upstream && git rebase upstream/main && git push origin main

# pull updated fork into this repository and rebuild
git subtree pull --preifx=sources/<repo-name> https://github.com/<you-or-your-org>/<repo-name>.git <target-branch> --squash
./scripts/build
```

**Contribute changes upstream to a repository from a different author**:
Create a feature branch in your fork of the original repository then create a pull request. Once your changes are merged upstream, pull the updated fork into this repository (see previous section).
```sh
git checkout -b <username>/<feature-or-change-description>
# edit...
git commit -m "Explanation for changes..." && git push origin <username>/<feature-or-change-description>
```
