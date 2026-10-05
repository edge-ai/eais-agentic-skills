# Synthetic two-source people-count flow

[people-count-flow.json](people-count-flow.json) is a complete importable **draft**,
not a station deployment. It has no reboot, recording-deletion, pipeline-control,
credential or account operations. Callback server/pipeline selection and UIBuilder
deployment still require explicit target/scope/recovery approval. Preserve the
self-signed certificate setting `allowInsecureTls: true`.

## Contract

Assume numeric source IDs `0` and `1`, with one direct merge result:

```json
{
  "0": {"source_id": 0, "obj_counter": {"person": {"max_val": 3}}},
  "1": {"source_id": 1, "obj_counter": {"person": {"max_val": 1}}}
}
```

The JSON node converts strings to objects. The adapter also accepts an array of
time-window records whose last `data` is this complete map. This example requires
both configured sources on each snapshot. Empty, partial, invalid and missing
person measurements invalidate both sources instead of retaining stale healthy
data. Other source sets or delivery policies require an explicit adaptation.
No primary/person model means unavailable measurements, never fabricated zeros.

## Actual exported wiring

`callback/Inject -> JSON -> adapter` branches to:

- `tag topic="counts" -> UIBuilder`, sending the complete array **before Split**.
- `Split -> Switch source_id -> per-source Change -> separate Alarm` instances.
  Each Change sets `msg.source_id` before replacing `payload` with
  `{"command":"evaluate","value":payload.count}`. Alarm output preserves this
  top-level source ID; a Change sets `topic="alarm"` before UIBuilder.

Catch subscribes to parse/adapter/command/alarm errors through its `scope`, not
normal input wires. It feeds diagnostic Debug and a Change producing
`topic="unknown", payload={state:"unknown",source_ids:[0,1],reason:...}`.
The unknown path does not reset, acknowledge or send zero into either alarm.
An unmatched source route uses the same unknown path.

The paired Dashboard Architect resources `people-count-dashboard.js` and
`people-count-dashboard.html` consume exactly these topics. Counts reset display
alarm freshness to unknown until the corresponding alarm result arrives.
Unknown input clears displayed counts/alarm states, not the alarm nodes' stored
state. Missing `triggered` or unrecognized alarm state must not display as OK.
Browser code does not calculate the threshold.

## Fixtures and checks

The exported manual-only Inject nodes test source 0 fault/source 1 normal, genuine
zero counts, missing person statistics, and invalid JSON. Inspect complete
callback and UIBuilder messages before using any real data.

Local tests run the exported flow with actual Node-RED Inject/JSON/Change/Split/
Switch/Catch nodes. Only EAIS subscription, EAIS Alarm and UIBuilder are stubs.
The alarm stub models independent numeric evaluations, not the installed node's
acknowledgment/persistence/state-machine implementation. Tests feed output into
the actual paired dashboard JavaScript with stub Vue/UIBuilder and verify source
isolation, zero, unknown/error propagation, tags, retention and clearing.
They do not prove station access, installed-node behavior, real Vue imports,
rendering, authentication, reconnect handling or end-to-end deployment.
