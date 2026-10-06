# nmws-documentation

Used to maintain an accurate, verifiably-up-to-date, hierarchical, corpus of documentation for a codebase and its associated product.

| Resource | Purpose |
| --- | --- |
| [skills/**set-me-up**](skills/set-me-up/SKILL.md) | Installs missing uv/Git tools and configures the user's corpus location. |
| [skills/**retrieve-relevant-documentation**](skills/retrieve-relevant-documentation/SKILL.md) | Finds relevant documentation and briefs agents with trust and freshness citations. |
| [skills/**capture-information-in-documentation**](skills/capture-information-in-documentation/SKILL.md) | Turns durable discoveries into deduplicated, source-grounded documentation diffs for approval. |
| [skills/**validate-documentation-form**](skills/validate-documentation-form/SKILL.md) | Checks frontmatter, references, hierarchy, body structure, scope exclusions, and links. |
| [skills/**verify-documentation-accuracy**](skills/verify-documentation-accuracy/SKILL.md) | Re-derives document claims from current source and proposes corrections and verification updates. |
| [reference/**frontmatter-schema.md**](reference/frontmatter-schema.md) | Defines the shared metadata contract for code and product documentation. |
| [reference/**repository-registry.md**](reference/repository-registry.md) | Defines repository IDs, checkout configuration, local overrides, and safe refresh behavior. |
| [reference/**staleness-convention.md**](reference/staleness-convention.md) | Defines drift detection, freshness results, and how trust affects documentation use. |

## Design Principles

1. **Documentation follows the NMWS documentation contract** Every piece of documentation carries the same YAML frontmatter according to the NMWS documentation
contract so that it can be used as part of the system. See [`reference/frontmatter-schema.md`](reference/frontmatter-schema.md).
2. **Documentation captures code and product information** The documentation corpus
contains documentation for the code **and** the product so that it can answer "how is this built / how does it work" *and* "what does this do for a user, how is it used, where does it fit, what are the sharp edges."
3. **Documentation authorship and staleness are verifiable** Every piece of documentation can be checked for authorship and staleness so that it can be used 
according to its accuracy.
4. **Documentation is progressively disclosed** The documentation corpus forms a
shallow hierarchy so that minimal context is needed for LLM agents to retrieve the
relevant documentation.

## Conceptual overview

The collection of all documentation is called the **documentation corpus** or just
**corpus**. One **corpus** can describe a product which spans several code repositories. 

Every piece of documentation contains YMAL frontmatter which contains
information as required by the **NWMS documentation contract**.

## Setup

Run the **set-me-up** skill and provide the path to your documentation corpus.
It checks for `uv` and Git, installs missing tools when permitted, and persists
`NMWS_DOCS_CORPUS_ROOT` in your shell configuration (or Windows user environment).
Restart the terminal/agent if necessary to inherit the setting. It does not create
a corpus, clone repositories, or change repository configuration.

The router looks for the documentation corpus in this order:

1. `$NMWS_DOCS_CORPUS_ROOT`, if set — point this at the vended docs location in your
   working repo.
2. Otherwise the bundled [`examples/`](examples/), which are illustrative, not authoritative.


## Requirements and tests

Only Git and [uv](https://docs.astral.sh/uv/getting-started/installation/) need to be
installed. Run the helpers through uv:

```sh
uv run --locked --script <plugin-root>/skills/retrieve-relevant-documentation/scripts/check_staleness.py \
  <doc-path> --registry <corpus-root>/repositories.yaml
uv run --locked --script <plugin-root>/skills/retrieve-relevant-documentation/scripts/validate_docs.py \
  --corpus-root <corpus-root>
```

Each executable helper declares its Python version and dependencies in inline
script metadata and ships an adjacent `.py.lock` file. uv automatically uses or
downloads compatible Python and installs the locked dependencies into an isolated,
cached environment. No manual Python, pip, or virtualenv setup is needed, and the
working repository's Python project is not installed or modified. First use needs
network access unless Python and dependencies are already available in uv's cache;
download/permission failures are explicit errors, not skipped checks.

For plugin development, `requirements.txt` supplies the test dependencies:

```sh
uv run --no-project --with-requirements <plugin-root>/requirements.txt \
  python -m unittest discover -s <plugin-root>/tests -v
```

After changing a helper's dependency metadata, regenerate its bundled lockfile with
`uv lock --script <helper-path>` and include that lockfile in the plugin update.

Tests use temporary local Git repositories and need no proprietary code or remote
source access. uv may need network access to provision Python and test/helper dependencies.
