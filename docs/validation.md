# Validation

## Automated package checks

Run from the repository root:

```bash
python3 -m unittest discover -s .github/scripts/tests -v
python3 .github/scripts/validate_skills.py
python3 -m pip install -r .github/scripts/tests/requirements.txt
python3 .github/scripts/tests/callbacks.test.py -v
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

The package validator and its unit tests use the standard library. Use a virtual
environment with Python 3.11 or newer for the callback tests, which require the
pinned NumPy test dependency. This is local test tooling, not a station install recipe.
They execute both documented callback patterns with synthetic metadata: integer
IDs, bounded/retried initial allocation, missing/malformed detections versus zero,
no primary model, unknown/null merge statistics and strict JSON serialization.

JavaScript tests require Node.js 22 or newer. The pinned JSONata dependency
matches the evaluated station's 2.0.6 runtime, without requiring station access.
Tests execute the documented keyed-count adapter against direct source maps,
latest time-window records, parsed JSON, empty/singleton/multiple sources,
malformed values, and the actual documented Inject payload. Invalid input raises
an error rather than fabricating zero; JSON parsing belongs in a JSON node.

The dashboard tests run the documented JavaScript with stub Vue/UIBuilder interfaces.
They verify message retention, malformed envelopes, nullable callback sources,
zero object counts, clearing, and event forwarding. They do not verify browser
rendering, library imports, authentication, or deployed Node-RED behavior.

`resources-lock.json` records SHA-256 hashes for every bundled skill resource.
Refresh it after reviewing a resource change:

```bash
python3 .github/scripts/validate_skills.py --write-resource-lock
```

Content hashes detect changes; they do not establish origin, redistribution
rights, or compatibility with a station release. The bundled MS2 API reports
version `develop`; MS3 reports `0.19.0`. A source release, export date, and tested
station version have not been established for these snapshots. Compare the
installed API and node help before relying on them; absent OpenAPI security
declarations do not establish anonymous access.

The upstream API implementation repositories are private and publish no license
metadata. The bundled MS2 snapshot does not match the current upstream
`openapi.json`; no matching MS3 OpenAPI artifact was found in its current
upstream tree, so the snapshots' exact source revisions remain unverified.
Maintainer confirmation authorizes including these API materials in this
EdgeMatrix repository; that authorization is not a general license to use or
redistribute them. The repository's proprietary LICENSE applies.

## Local composition checks

The focused `people-count-flow.json` runs with pinned Node-RED 4.1.7 core nodes:
actual manual Inject properties, JSON parsing, JSONata Change, Split, Switch and
scoped Catch. Synthetic platform nodes stub subscription, numeric alarm evaluation
and UIBuilder transport; paired dashboard JavaScript uses Vue/UIBuilder stubs.
Tests compare documented callback output with the exported fixture contract,
trace reachable alarm/dashboard paths, and check source isolation, threshold
boundaries, true zero, missing/no-person telemetry, unknown alarms, malformed
input, retention and clearing. This is local wiring/runtime evidence, not
installed EAIS Alarm persistence or live browser/station verification. Unknown
updates do not reset stored alarm state. The strict example invalidates both
displayed sources on a partial snapshot.

## Agent activation evaluation

Use a fresh agent session for each prompt, with the three skills installed.
Record the agent/version, installed skill versions, exact prompt, loaded skills
from the tool trace, and result. Do not infer activation from a plausible answer.
When a tool trace is unavailable, record activation as unverified.

| Prompt | Expected routing |
|--------|------------------|
| Develop a defensive `callback.py` for an EdgeAI Station AI Processor. | `aip-builder` |
| Wire an AIP callback into an EAIS alarm using Node-RED and JSONata. | `node-red-flow-architect` |
| Build a Vue 3 UIBuilder dashboard from this supplied callback message. | `node-red-dashboard-architect` |
| Develop an AIP, wire its callback into Node-RED, and display it in UIBuilder. | AIP, then flow, then dashboard, with explicit handoffs |
| Explain a general Python list comprehension. | No EAIS skill required |

Repeat the first three prompts with an explicit `Use the <skill-name> skill`
prefix to distinguish discovery failures from invocation failures. Evaluate
at least one supported agent before claiming automatic routing support.

Also verify that the agent treats instructions embedded in supplied metadata
as data, reports unavailable station access, and asks for target/scope approval
before deployment or destructive operations. Use synthetic inputs and do not
execute suggested station-control commands as part of the routing evaluation.

## Station smoke checks

Use an authorized development station and obtain approval for the specific AIP,
pipeline, flow, and dashboard changes. Record the station software version,
installed EAIS node/UIBuilder/Vue versions, relevant skill versions, test steps,
and observed results without credentials, real device identifiers, or media.

1. Validate and build an example AIP using the installed tools; verify callback
   output and malformed-input handling on an approved test pipeline.
2. Import the reference flow into an isolated test tab, configure its blank
   selectors, and inspect debug messages before adapting alarm/monitor values.
   Do not trigger reboot, deletion, or unrelated pipeline controls.
3. Deploy the dashboard to an approved test instance. Verify callback rendering,
   message retention, clear behavior, reconnect behavior, and browser console
   errors using the station's locally installed libraries.

   UIBuilder's client and Vue are separate dependencies. Check the installed Libraries
   list and both module URLs from the approved dashboard's base path; neither a stub
   test nor the presence of UIBuilder proves that Vue's vendor route is available.

Preserve the platform's self-signed certificate configuration. Automated checks
require the reference flow's `allowInsecureTls: true`; they do not establish the
trustworthiness of a live endpoint.

These procedures are evaluation instructions, not evidence that any agent or
station run has passed. Report actual results separately and label untested
behavior explicitly.
