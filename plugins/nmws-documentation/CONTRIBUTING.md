# Contributing to nmws-documentation

Keep skill instructions focused on decisions and the normal workflow. Put shared
mechanics in directly linked references, and preserve the evidence, trust, and
approval boundaries when editing.

## Run tests

Git and uv are the development prerequisites. `requirements.txt` supplies test
dependencies; uv manages Python without installing the working project:

```sh
uv run --no-project --with-requirements "<plugin-root>/requirements.txt" \
  python -m unittest discover -s "<plugin-root>/tests" -v
```

Tests use temporary local Git repositories; no proprietary code or remote source
access is needed. uv may need downloads to provision Python and dependencies.
Coverage includes packaging/reference links, metadata discovery, source refresh,
freshness checks, structural validation, and isolated helper execution. These
tests do not establish agent-level retrieval or writing quality.

The optional companion has dependency-free Node.js hook tests. With Node.js 20
or newer, run them separately:

```sh
node --test "<repository-root>/plugins/nmws-documentation-auto/tests/hooks.test.mjs"
```

These exercise real hook subprocesses, successful and failed local Git commits,
host payloads, reminder throttling, and packaging. Offer consent, duplicate-finding
judgment, and decline handling are agent instructions, not a hook-side classifier;
instruction contract tests cannot establish agent-level compliance.

## Maintain helper dependencies

Each executable helper declares its Python version and dependencies in inline
script metadata and ships an adjacent `.py.lock` file. After changing that metadata,
regenerate the lock with `uv lock --script "<helper-path>"` and include it in the
update. Helpers must continue to work without installing or modifying the user's
Python project.

## Check the examples

The bundled examples are fabricated format demonstrations, never authoritative
source or product evidence. Validate them explicitly:

```sh
uv run --locked --script "<plugin-root>/skills/retrieve-relevant-documentation/scripts/validate_docs.py" \
  --corpus-root "<plugin-root>/examples" \
  --registry "<plugin-root>/examples/repositories.example.yaml"
```

Keep real-source documents and evaluation evidence in private corpora or private
local artifacts, not this public plugin repository.
