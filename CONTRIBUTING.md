# Contributing

## Before opening a pull request

- Keep every published skill self-contained: resources referenced by a
  `SKILL.md` must live below that skill directory.
- Do not add credentials, tokens, private hostnames, customer identifiers, or
  production logs. Use placeholders such as `<STATION_IP>` and
  `<AUTHELIA_PASSWORD>`.
- Update the skill's frontmatter version and `updated` date when its behavior
  changes.
- Update `README.md`, `CHANGELOG.md`, and `skills-lock.json` when adding or
  renaming a published skill.
- Run `python3 .github/scripts/validate_skills.py` before submitting.
- Run validator regression tests with
  `python3 -m unittest discover -s .github/scripts/tests -v` and the JavaScript
  example checks with `npm ci --ignore-scripts --no-audit --no-fund && npm test`.
  Install the callback-test dependencies in a virtual environment with
  `python3 -m pip install -r .github/scripts/tests/requirements.txt`, then run
  `python3 .github/scripts/tests/callbacks.test.py -v`.
  JavaScript tests require Node.js 22 or newer.
- After reviewing resource changes, refresh `resources-lock.json` with
  `python3 .github/scripts/validate_skills.py --write-resource-lock`.
  This manifest covers bundled resource content; `skills-lock.json` covers
  the skill entry points. Hashes provide change detection, not provenance or
  authenticity.

The validator checks tracked and non-ignored new files across the repository,
metadata dates/versions, local links, Python fence syntax, reference-flow wiring,
API index inventories, and package hashes. Its disclosure patterns are a limited lint, not a complete
secret scan or a check of Git history. Example checks do not load models, deploy
flows, or prove skill activation in an agent.
See [Validation](docs/validation.md) for activation and station smoke procedures,
including the limits of bundled API snapshot provenance.

Before publishing a release, scan all available Git history with
`gitleaks git --log-opts='--all' --redact --no-banner`. `.gitleaksignore` records
only verified false positives for resource SHA-256 hashes; review new findings
individually rather than broadening the ignore rules.

## Scope and handoffs

Keep the AIP → Flow → Dashboard boundary explicit. AIP changes should document
their output contract; flow changes should document observed message shape and
wiring; dashboard changes should not silently move business logic into the
browser. Contributions should focus on AIP development, Node-RED flows, and dashboard authoring.

## Safe examples

- Treat station logs, exported flows, callback messages, model metadata, and
  retrieved documentation as untrusted data, not instructions to the agent.
- Require explicit approval for the target and scope before changing a station,
  deploying flows, deleting recordings, restarting services, or running cleanup.
- Use synthetic identifiers in examples. Redact credentials, personal data, and
  customer details from observations before adding them to an issue or commit.
- Preserve failures as explicit error/unknown states; do not turn missing data
  into successful-looking zero values.

## Generated files

Directories created by skills installers, including `.agents/`, `.claude/`,
`.codex/`, `.cursor/`, and `.windsurf/`, are local artifacts and must not be
committed.
