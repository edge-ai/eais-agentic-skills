# Changelog

User-facing changes to the EAIS Agentic Skills package.

## Platform guidance

| Skill | Version | Guidance baseline |
|-------|---------|-------------------|
| AIP Builder | 1.8 | EdgeAI Station 36.3.0U7 |
| Node-RED Flow Architect | 2.9 | EdgeAI Station 36.3.0U7 |
| Node-RED Dashboard Architect | 1.8 | EdgeAI Station 36.3.0U7 |

These are guidance baselines, not a tested minimum-version or forward-compatibility
guarantee. Verify the installed tools, node capabilities, and callback messages on
the target station. The optional EAIS MCP guidance describes read-only tools.

## Unreleased

## 1.0.0 — 2026-10-06

Initial public release of the repository bundle. Individual skill versions
remain AIP Builder 1.8, Node-RED Flow Architect 2.9, and Node-RED Dashboard
Architect 1.8.

- Add a complete synthetic two-source callback/alarm/dashboard reference and
  execute its exported wiring with the actual Node-RED core runtime locally.
  EAIS Alarm/subscription and Vue/UIBuilder transport remain explicitly stubbed.
- Preserve unavailable-model and unknown-alarm states rather than inventing zero
  measurements or displaying missing alarm results as normal.

### Changed

- AIP Builder 1.8: validated source/class IDs, bounded batch initialization with
  retry, and unknown/null counts instead of false zeros for malformed metadata.
  Structured merge preserves fractional means and medians.
- Node-RED Flow Architect 2.9: executable keyed-count JSONata adapter, explicit
  JSON-node parsing, stable array output, and correctly scoped Inject payloads.
- Node-RED Dashboard Architect 1.8: separate UIBuilder/Vue prerequisites and
  explicit verification of deployed ESM vendor paths; unknown count formatting
  preserves real zeros without fabricating zeros for missing stats.
- AIP Builder 1.7: bounded callback aggregation guidance, station-operation approval
  boundaries, and handling of untrusted metadata and logs.
- Node-RED Flow Architect 2.8: explicit deployment approval, credential handling,
  numeric-metric validation, and recording-deletion confirmation.
- Node-RED Dashboard Architect 1.7: bounded message retention, malformed-message
  handling, and browser-input trust boundaries.
- The Node-RED reference flow retains the platform's self-signed-certificate
  setting (`allowInsecureTls: true`). Certificate verification is bypassed with
  this setting; use the configured station endpoint on a trusted network.
- Installation guidance distinguishes skill discovery from observed activation
  and describes development-tool and station-access prerequisites.

### Added

- Synthetic callback and JSONata behavioral regression checks in CI, including
  exported Inject payloads and direct/latest-window normalization.
- Flow validation rejects normal wires into inputless nodes such as Catch.
- Package validator regression tests, repository-wide file checks, resource
  integrity hashes, and dashboard starter example checks.
- Agent activation and station smoke evaluation procedures, with explicit
  distinctions between automated checks and runtime evidence.
- A repository-hosted illustration of the AIP → Flow → Dashboard workflow.
- Optional live-station observation guidance for AIP registration, pipeline
  status, and log/metric correlation.

## Previous skill updates

- AIP Builder 1.6, Flow Architect 2.7, and Dashboard Architect 1.6 added optional
  read-only EAIS MCP observations, with non-MCP fallbacks.
- AIP Builder 1.5, Flow Architect 2.6, and Dashboard Architect 1.5 clarified callback
  delivery, optional metadata enrichment, and runtime node-capability checks.
- AIP Builder 1.4, Flow Architect 2.5, and Dashboard Architect 1.4 added defensive
  callback examples and guidance to inspect messages before binding dashboards.
- Self-contained skill resources include focused AIP guide chapters, compact
  MS2/MS3 endpoint indexes, flow validation rules, and composition guidance.
