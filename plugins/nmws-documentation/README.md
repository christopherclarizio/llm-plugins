# nmws-documentation

Help coding agents reuse and maintain understanding of a codebase and its product.
Capture the concepts, relationships, constraints, and user-facing behavior that are
expensive to rediscover from source, not an inventory of code or a transcript of investigations.

## How it works

The plugin supports a learning loop:

1. **Retrieve** relevant documentation before investigating or changing a system.
2. **Investigate** missing or uncertain information against source and product evidence.
3. **Capture** useful discoveries in an existing document, or propose a new one when needed.
4. **Maintain** documents by checking their structure and re-verifying their claims.

Retrieval does not edit documents. Capture and verification propose concrete diffs
for approval before changing the corpus; they do not commit or push automatically.
A lookup miss alone is not a reason to create documentation.

For example, an agent investigating a playback issue might start with the playback
architecture, follow a link to frame caching, and consult the corresponding product
document for user-visible limitations. If the investigation uncovers an undocumented
invariant, the agent proposes adding it to the relevant code document rather than
creating a debugging diary.

## The documentation corpus

The **corpus** is the collection of documents maintained with this plugin. It lives
outside the plugin and can describe a product implemented across several repositories.
It has two connected trees:

| Tree | Explains | Tiers, broad to focused |
| --- | --- | --- |
| **Code** | How the system is built: concepts, relationships, entry points, invariants, and rationale. | `architecture` → `subsystem` → `component` |
| **Product** | What users can do: capabilities, workflows, context, limitations, and sharp edges. | `overview` → `feature` → `workflow` |

Documents have a specific scope, including what they do **not** cover. Parent/child
links support drill-down; cross-tree links connect behavior to implementation. Start
broad for orientation or go directly to a focused document for a narrow question.
Read only the documents the task needs.

Each Markdown document has shared [frontmatter](reference/frontmatter-schema.md):
a stable ID, routing description, tree and tier, navigation links, trust status,
and code references with per-repository verification metadata.
The [repository registry](reference/repository-registry.md) maps those references
to configured source checkouts.

```text
<corpus-root>/
  code/                     # Code documents
  product/                  # Product documents
  repositories.yaml         # Repository IDs and existing checkouts
  repositories.local.yaml   # Optional local-path overrides; do not commit
```

Use the [code](templates/code-doc.template.md) and
[product](templates/product-doc.template.md) templates for document structure.
The bundled [examples](examples/) demonstrate the format; they are fabricated,
not product knowledge, and are never substituted for an unconfigured corpus.

## Trust, freshness, and correctness

These answer different questions:

| Signal | Question |
| --- | --- |
| **Trust** | What review has this document received: `draft`, `agent-generated`, or `human-reviewed`? |
| **Freshness** | Has referenced code changed since its recorded verification commit? |
| **Accuracy verification** | Do the document's claims hold against the evidence examined now? |

A fresh document can be wrong; a stale document can still be correct. Structural
validation proves neither. Retrieval reports trust and freshness, and corroborates
load-bearing claims from low-trust, stale, or incompletely checked documents.
Product behavior and historical rationale need their own evidence, not inference
from code alone. See the [trust and staleness rules](reference/staleness-convention.md).

## Setup and use

Provide an existing corpus directory to **set-me-up**. It checks Git and
[uv](https://docs.astral.sh/uv/getting-started/installation/), installs missing tools
when permitted, and persists `NMWS_DOCS_CORPUS_ROOT`. It does not create the corpus,
configure repositories, or clone source. Restart the terminal/agent if needed.

Configure the registry with clean checkouts on their authoritative branches,
separate from feature work. Freshness checks fetch and fast-forward those checkouts;
they never switch branches or discard edits. Without a configured corpus, retrieval
reports the gap and continues with source investigation.

| Skill | Use it to |
| --- | --- |
| [set-me-up](skills/set-me-up/SKILL.md) | Configure tools and the corpus location. |
| [retrieve-relevant-documentation](skills/retrieve-relevant-documentation/SKILL.md) | Get a task-specific briefing with trust and freshness citations. |
| [capture-information-in-documentation](skills/capture-information-in-documentation/SKILL.md) | Propose a documentation update for durable new understanding. |
| [verify-documentation-accuracy](skills/verify-documentation-accuracy/SKILL.md) | Assess claims and propose evidence-backed corrections or verification updates. |
| [validate-documentation-form](skills/validate-documentation-form/SKILL.md) | Check metadata, hierarchy, document structure, and links. |

Helpers run in uv-managed environments without installing dependencies into the
working project. First use may need downloads; freshness checks need repository
access. See [helper commands](reference/helpers.md) for direct use and
[contributor guidance](CONTRIBUTING.md) for tests and dependency maintenance.
