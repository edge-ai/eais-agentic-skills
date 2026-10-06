# EdgeAI Station AIP Developer Guide — Index

> Version: 2.2 · Models: EX5 · Author: Edgematrix.

This guide was split into focused, independently loadable parts so an agent can load **only the topic it needs** (each file stays well under the ~20 KB read limit). Load a single part on demand — do **not** read all parts at once.

## Topic Map

| Part | Topic | Load when you need... | Original § |
|------|-------|-----------------------|-----------|
| [01-hardware-and-tools.md](./01-hardware-and-tools.md) | Hardware & conversion tools | EX5 hardware specs, pre-installed libraries, `trtexec`/`tao-converter` capabilities, JupyterLab IDE | §1 |
| [02-aip-package.md](./02-aip-package.md) | Project start & package structure | Starting a new AIP project, full package directory layout | §2.1–2.2 |
| [03-manifest-schema.md](./03-manifest-schema.md) | `manifest.json` schema | Full field definitions, `primary_processor`/`tracker_engine`/`analytic_plugins` (ROI/DIR/OVC/LCC) semantics | §2.3 |
| [04-model-and-configs.md](./04-model-and-configs.md) | Model conversion & configs | PyTorch/TF/ONNX/TAO → TRT workflow, `nvinferserver` + Triton `config.pbtxt` setup | §2.4–2.5 |
| [05-callback-init-probe.md](./05-callback-init-probe.md) | Callback: overview, init & probe | Callback execution model, `initialize()`, `parse_batch_meta()` numpy-dtype probe pattern, `data_parser_config` keys | §3.1–3.3 |
| [06-callback-display-meta.md](./06-callback-display-meta.md) | Callback: display meta | Drawing shapes/text overlays, the 16-item-per-structure limit | §3.4 |
| [07-callback-merge-push.md](./07-callback-merge-push.md) | Callback: merge, push, class vars & Node-RED setup | `merge_and_analyze()` aggregation, push behaviour, available class variables, wiring the callback node | §3.5–3.8 |
| [08-options-schema.md](./08-options-schema.md) | `options.json` schema & limits | User-configurable option types, `self.options` access, current callback limitations | §3.9–3.10 |
| [09-testing-debugging.md](./09-testing-debugging.md) | Testing & debugging | AIP registration, log system, performance metrics, EX3 portability | §4 |
| [10-distribution.md](./10-distribution.md) | Packaging & distribution | `.include` rules, packaging steps, performance validation, app store | §5 |
| [11-apis.md](./11-apis.md) | Device & video streaming APIs | Pointers to the EdgeAI Video Streaming & Device Management APIs | §6 |
| [12-eais-tools.md](./12-eais-tools.md) | `eais-tools` CLI reference | CLI commands for AIP build/check/export, config validation, pipeline tests | §7 |
| [13-tips-and-qa.md](./13-tips-and-qa.md) | Tips & Q&A | Local JupyterLab testing, Git workflow, log tailing, `trtexec` advanced tips, common Q&A | §8–9 |

## Legend (used throughout all parts)

> ℹ️ **Note**: Additional helpful information, tips, or clarification.
>
> ⚠️ **Warning**: A cautionary point requiring careful attention to avoid potential issues.
>
> 🚨 **Important**: Critical information. Ignoring it could result in serious problems (system failure, data loss, security breaches, etc.).
