# Documentation validation

`validate_docs.py` is an offline consumer of the shared frontmatter contract. It reads
Markdown under `<corpus-root>/code/` and `<corpus-root>/product/`; keep corpus support
files outside those directories. At least one document is required.

```sh
python3 <plugin-root>/skills/docs-router/scripts/validate_docs.py \
  --corpus-root <corpus-root>
```

`--registry` defaults to `<corpus-root>/repositories.yaml`. The registry must be
well-formed, but configured local checkouts need not exist. No fetch, Git operation,
local override, metadata mutation, or network access occurs.

## Errors

- Missing/malformed frontmatter, unknown fields, duplicate YAML keys, missing required strings,
  invalid IDs, or duplicate corpus-wide IDs.
- Unknown tree, wrong directory, incompatible tier, invalid trust, malformed
  navigation/keyword lists, or duplicate list entries.
- Missing/invalid `code_references`, unknown repository IDs, unsafe reference paths,
  invalid commit/date/verifier, or removed `sources`/top-level `verified_at` fields.
- Unresolved navigation IDs, self-links, cross-tree hierarchy, incorrect altitude
  direction, or missing reciprocal parent/children links. Related links may cross trees;
  they need not be reciprocal. Missing counterparts are not invented.
- Missing/empty template sections or absent explicit scope exclusions. Use wording
  such as "does not cover", "out of scope", or "excludes". Section headings are the
  exact level-two headings from the selected template.
- Missing local Markdown link/image targets or heading/explicit HTML anchors.
  Inline, reference-style, image, and HTML links are parsed; fenced-code examples
  are not links. Local links use relative paths. External HTTP(S), mail, telephone,
  and network-path URLs are not fetched. Markdown heading fragments follow the
  common GitHub slug convention; non-Markdown fragments are not checked.

## Warnings and limits

More than 20 lines of fenced/indented code warns about code-restating trivia. An
absent counterpart link warns when `related` is empty. These are review heuristics,
not judgments of correctness. Review altitude, scope, duplication, and actual
counterpart availability in the capture/verify workflow.

This linter does not prove prose correctness, reference-path coverage, freshness,
human review, sentence counts, or adequate product evidence. Custom renderer-specific
anchors/extensions may need adjustment to ordinary Markdown/HTML anchors.

Exit `0`: no errors (warnings allowed). Exit `1`: document errors. Exit `2`:
configuration, corpus-read, or dependency failure. `--strict` also makes warnings
exit `1`; enable it only when intentionally requiring zero heuristic warnings.

For corpus CI, install the plugin's pinned-range requirements and run this same command
against the private corpus. The public plugin tests need no private source or network.
