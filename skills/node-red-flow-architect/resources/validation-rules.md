# Node-RED Flow JSON Validation Rules

When parsing, reviewing, or generating Node-RED flow JSON, perform these structural validation checks organized by severity.

## Tier 1 — ERRORS (block import / must fix)

- Root element is not a JSON array of node objects
- A node object is missing an `id` property (string, unique across the flow)
- A node object is missing a `type` property (string)
- Duplicate `id` values exist in the flow
- A non-tab, non-config node is missing a `z` property or references a non-existent tab
- `wires` references a node ID that does not exist in the flow
- Wires target an inputless node (`catch`, `status`, `complete`, `inject`, `callback`).
  Catch subscribes to errors through its scope; it is not a normal data-path sink.
- A custom EAIS node (`device`, `aip`, `pipeline`, `callback`, `record`, `monitor`, `account`) is missing its `server` property reference
  - `alarm` is **exempt** — it performs no device I/O and takes no `server` property. Do not flag it.

## Tier 2 — WARNINGS (flag but allow)

- Orphaned config nodes (no regular node references them)
- A flow tab has no `catch` node for error handling
- Function nodes missing `try/catch` for defensive coding
- `http in` nodes without a corresponding downstream `http response` node
- `link in` / `link out` nodes with mismatched `links` arrays
- Self-referencing wires without a delay/trigger (likely infinite loop)

### Function-node abuse patterns (Tier 2)

Flag any Function node whose `func` body matches these — they almost always have a declarative replacement:

| Pattern in `func` | Suggested replacement |
|---|---|
| Single `msg.payload = X; return msg` | `change` node, Set rule |
| `msg.payload = msg.payload.X` | `change` node, Move rule |
| `.filter(...)` then `return msg` | `change` + JSONata `payload[cond]` |
| `.map(...)` then `return msg` | `change` + JSONata `payload.{...}` |
| `.length` or `.reduce` count then `return msg` | `change` + JSONata `$count(...)` |
| `if (...) { node.send([msg, null]) } else { node.send([null, msg]) }` | `switch` node |
| Loops emitting per-item via `node.send` | `split` node |
| Mustache-style string concatenation | `template` node |
| `msg !== last; last = msg` pattern | `rbe` node (report-by-exception) |

## Tier 3 — STYLE (suggest improvement)

- Nodes with empty or generic `name` property (e.g., "debug 1")
- Function nodes whose body is a single assignment/filter/map/count (should be `change` + JSONata)
- `eais-server` config nodes missing `deploymentMode` or connection settings

## Behavioral checks (separate from structural validity)

- Exercise the actual exported Inject payloads; Inject already creates
  `msg.payload`, so a full message envelope nested inside it may break consumers.
- Evaluate JSONata against valid, zero, missing and malformed values, plus empty,
  singleton and multiple-source results. Use `$lookup` for dynamic keys, not
  bracket filtering. Keep a stable array shape when feeding a Split node.
- Parse serialized JSON with a JSON node and route parse/transform errors to
  Catch -> unknown/error; missing measurements must not become zero.
- Use the tested adapter in [jsonata-cheatsheet.md](jsonata-cheatsheet.md) only
  when the observed AIP/envelope matches its stated contract.
- Walk the actual exported wires from callback/Inject to every intended output.
  An adapter -> Split -> per-source route -> alarm path must be connected in the
  JSON, not just described in prose. Catch runs in parallel via its scope and
  routes errors to unknown/error; do not wire an adapter into Catch.

## Report Format

When validation issues are found, report them in a table:

| Severity | Node ID | Type | Issue | Fix |
|----------|---------|------|-------|-----|
| ERROR | `abc123` | `pipeline` | Missing `server` reference | Add valid `eais-server` config node ID |
| WARNING | `def456` | `function` | Body is a single `.filter()` | Replace with `change` + JSONata |
| STYLE | `ghi789` | `debug` | Generic name "debug 1" | Rename to describe its purpose |
