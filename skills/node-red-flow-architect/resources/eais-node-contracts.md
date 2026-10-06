# EAIS Custom Node Contracts

Durable responsibilities and common message patterns for EAIS custom nodes.
Load this resource when building or modifying flows that use EAIS nodes.

This is not a package-version schema. Node options and message fields may evolve
without requiring a skill update. For exact behavior on a target station:

1. Inspect the installed node's editor help and an exported instance of that node.
2. Wire a `debug` node to the complete message and observe live output.
3. Treat `eais-reference-flow.json` as a wiring example, never as an exact contract.

## Node Input/Output Contracts

| Node | Input (`msg.payload`) | Output (`msg.payload`) |
|------|-------------------------------|--------------------------------|
| `device` | `{ command: "info"\|"connectivity"\|"network"\|"stack"\|"license"\|"reboot" }` | Command-specific result |
| `account` | `{ command: "users"\|"tokens" }` | Command-specific result |
| `aip` | `{ command: "info"\|"status", processorId? }` | AIP info/status object |
| `pipeline` | `{ command: "info"\|"status"\|"start"\|"stop"\|"restart"\|"snapshot", pipelineId? }` | Status/config object |
| `callback` | N/A (0 inputs, subscription) | AIP-defined results delivered by MS3 merge/push processing (see below) |
| `alarm` | `{ command: "evaluate", value: N }` or `{ acknowledge: true }` or `{ reset: true }` | `{ alarm: { state, stateChanged, currentValue, triggered, timestamp } }` |
| `record` | `{ action: "list"\|"get"\|"download"\|"delete", filters?, uuid? }` | Action-specific result |
| `monitor` | `{ command: "get", metricMode?, metricType?, metricName?, aggregation? }` | `{ name, value, unit, timestamp }` or grouped metrics |

## Important Notes

- All nodes except `callback` require an input message to trigger
- `callback` is a subscription node — outputs automatically when the pipeline sends analytics data
- `record` uses `action` (not `command`) as its dispatch field
- All EAIS nodes (except `alarm`) require a `server` property referencing an `eais-server` config node
- Numeric performance metrics (FPS, CPU, memory) come from `monitor`, not `pipeline`
- The `pipeline status` command returns operational state only — not FPS metrics

## The `callback` Node — Output Is Not Fixed

The `callback` node is the only EAIS node whose business payload is deliberately
free-form:

- Its **contents** are decided by the AI Processor's `merge_and_analyze()` — free-form and
  AIP-specific. Two AIPs on the same device can emit completely different structures.
- Its **delivery envelope** is decided by MS3 merge/push configuration. A subscriber may
  receive a direct probe result, a direct merge result, or multiple time-windowed merge
  records.
- The installed Node-RED callback node forwards what it receives. Depending on its
  available settings, serialized JSON may be parsed into an object or left as a string.
- Metadata enrichment is optional and can be absent when disabled or when enrichment
  cannot be completed.

Never write transforms, alarm rules, or dashboard bindings against an assumed callback
shape. Wire a `debug` node set to **complete msg object**, deploy, read one real message,
and build against what you observe. Guard for the shapes you did not observe.

Do not copy hidden fields or defaults from a reference export. Select the pipeline and
optional capabilities through the installed node editor, then preserve the exported
configuration for that station.

## Standardized Message Envelope

EAIS nodes add operational context under `msg.eais` alongside `msg.payload`.
Exact fields depend on the node and operation and may evolve. Common fields include:

```
msg.payload = <business result from handler>
msg.eais = { ok: true|false, node: "<type>", command: "<cmd>", ...nodeSpecificContext }
```

Use `msg.payload` for business logic. Use `msg.eais` only for debugging, logging, or conditional routing on success/failure (`msg.eais.ok`).

## Node-to-Node Payload Adapters

Before wiring EAIS nodes together, validate that the output shape of one satisfies the input contract of the next. Common adapters using `change` node + JSONata:

| Source → Target | Adapter JSONata |
|----------------|----------------|
| `monitor` single metric → `alarm` evaluate | First use a Switch node to accept only observed numeric `msg.payload.value`; route missing/invalid values to an error path. Then use `{ "command": "evaluate", "value": payload.value }` |
| `pipeline` status → `switch` route by state | Switch node on `msg.payload.overall` (values: `"Running"`, `"Stopped"`, `"Error"`) |
| `callback` result → object-count `alarm` | Validate/normalize the observed shape first (see the tested keyed-count adapter in [jsonata-cheatsheet.md](jsonata-cheatsheet.md)); after Split, use `{ "command": "evaluate", "value": payload.count }`. Missing counts go to unknown/error, not zero. |

## Node Responsibility Boundaries

| Need | Use this node | NOT this node |
|------|---------------|---------------|
| Pipeline operational state (Running/Stopped/Error) | `pipeline` with `command: "status"` | — |
| FPS, CPU, memory, temperature metrics | `monitor` with appropriate `metricType` | `pipeline` (status only) |
| Object detection counts | `callback` result | `monitor` |
| Alarm evaluation from a metric | `monitor` → adapter → `alarm` | Direct `pipeline` to `alarm` |
