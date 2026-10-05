# nmws-documentation

Used to maintain an accurate, verifiably-up-to-date, hierarchical, corpus of documentation for a codebase and its associated product.

| Resource | Purpose |
| --- | --- |
| [skills/**docs-router**](skills/docs-router/SKILL.md) | Finds relevant documentation and briefs agents with trust and freshness citations. |
| [skills/**docs-capture**](skills/docs-capture/SKILL.md) | Turns durable discoveries into deduplicated, source-grounded documentation diffs for approval. |
| [skills/**docs-evaluate**](skills/docs-evaluate/SKILL.md) | Compares tasks with and without the corpus to measure correctness, wrong turns, and token usage. |
| [skills/**docs-validate**](skills/docs-validate/SKILL.md) | Checks frontmatter, references, hierarchy, body structure, scope exclusions, and links. |
| [skills/**docs-verify**](skills/docs-verify/SKILL.md) | Re-derives document claims from current source and proposes corrections and verification updates. |
| [reference/**frontmatter-schema.md**](reference/frontmatter-schema.md) | Defines the shared metadata contract for code and product documentation. |
| [reference/**repository-registry.md**](reference/repository-registry.md) | Defines repository IDs, checkout configuration, local overrides, and safe refresh behavior. |
| [reference/**staleness-convention.md**](reference/staleness-convention.md) | Defines drift detection, freshness results, and how trust affects documentation use. |
| [reference/**validation.md**](reference/validation.md) | Documents validator checks, warnings, limitations, exit codes, and CI usage. |
| [reference/**write-loop.md**](reference/write-loop.md) | Defines approval-gated writes, grounding requirements, and human-review trust transitions. |

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

The router looks for the documentation corpus in this order:

1. `$NMWS_DOCS_CORPUS_ROOT`, if set — point this at the vended docs location in your
   working repo.
2. Otherwise the bundled [`examples/`](examples/), which are illustrative, not authoritative.


## Requirements and tests

Git, Python 3.9+, PyYAML, and markdown-it-py are required. Use your Python environment or a virtual
environment, then install:

```sh
python3 -m pip install -r <plugin-root>/requirements.txt
python3 -m unittest discover -s <plugin-root>/tests -v
```

Tests use temporary local Git repositories; they need no network or proprietary code.
