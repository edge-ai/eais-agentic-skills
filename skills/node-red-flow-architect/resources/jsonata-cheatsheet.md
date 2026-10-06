# JSONata Cheat-Sheet for `change` Nodes

Use these patterns in `change` node rules with `tot: "jsonata"` instead of Function nodes:

| Goal | JSONata expression |
|------|-------------------|
| Count items matching condition | `$count(payload.objects[label='person'])` |
| Sum a field | `$sum(payload.items.price)` |
| Filter array | `payload.items[active=true]` |
| Map / reshape | `payload.items.{ "id": uuid, "name": title }` |
| Conditional value | `value > 5 ? "high" : "low"` |
| Preserve zero; mark missing as unknown | `$exists(payload.count) ? payload.count : null` |
| Dynamic object key | `$lookup(payload, $key)` (brackets filter; they do not look up dynamic keys) |
| Current timestamp (ms) | `$millis()` |
| ISO timestamp | `$now()` |
| Time window (last 5 min) | `{ "since": $fromMillis($millis() - 300000), "until": $now() }` |
| Group by | `payload.events{type: $count(*)}` |
| Sort ascending | `payload.items^(timestamp)` |
| Sort descending | `payload.items^(>timestamp)` |
| Pick fields | `payload.{ "id": id, "name": name }` |
| Spread + override | `$merge([payload, {"status": "ok"}])` |
| Build command payload | `{ "command": "evaluate", "value": $count(payload.objects[label='person']) }` |

## Example: People counting without a Function node

Instead of a Function node:
```jsonata
(
  $assert($type(payload.objects) = "array", "Missing or invalid detections array");
  { "command": "evaluate", "value": $count(payload.objects[label = "person"]) }
)
```
Set as: `change` node → Set `msg.payload` → to JSONata expression above.

Only use `$count` after verifying the detections array exists. `$count` of a
missing field is zero, which would falsely clear an alarm on missing telemetry.

## Tested callback adapter: keyed class counts

This is one assumed AIP contract, not a universal callback schema:
`{"demo":{"source_id":"demo","obj_counter":{"person":{"max_val":3}}}}`.
The result is always an array of `{source_id, count}`, including for one source.

For string delivery, put a **JSON** node configured to convert JSON strings to
objects before the Change node. Invalid JSON goes to Catch -> unknown/error.
Do not use `$eval` to parse untrusted callback text.

The expression accepts a direct source map, or an array of `{since, until, data}`
records whose **last** record contains that map. Empty maps/windows yield `[]`.
It intentionally uses only the latest window: replaying historical windows can
cause misleading alarm transitions. Choose another policy explicitly if needed.
Unsupported shapes and missing/invalid counts raise an error; wire a Catch node
to an unknown/error output, never synthesize an alarm value of zero.

```jsonata
(
  $assert($type(payload) != "string", "Parse callback JSON with a JSON node first");
  $data := $type(payload) = "array"
    ? ($count(payload) > 0 ? payload[-1].data : {})
    : payload;
  $assert($type($data) = "object", "Expected a source map or latest window data");
  [$map($keys($data), function($key) {(
    $entry := $lookup($data, $key);
    $assert($type($entry) = "object", "Invalid source entry");
    $sid := $entry.source_id;
    $assert(($type($sid) = "string" and $length($sid) > 0) or
      ($type($sid) = "number" and $sid >= 0 and $floor($sid) = $sid),
      "Invalid source_id");
    $count := $entry.obj_counter.person.max_val;
    $assert($type($count) = "number", "Missing or non-numeric person.max_val");
    $assert($count >= 0 and $floor($count) = $count, "Invalid person count");
    {"source_id": $sid, "count": $count}
  )})]
)
```

Wire `Change -> Split -> per-source routing -> Change -> Alarm`. Use a separate
stateful Alarm instance per source. The final Change uses
`{"command":"evaluate","value":payload.count}`; configure a numeric threshold `2`
and operator `>` through the installed Alarm editor. Unknown input must also be
visible to dashboards/consumers; an unchanged prior alarm state is not fresh data.

### Inject payloads are not complete messages

An Inject node creates `msg.payload` from its configured `payload` value. For the
contract above, use this property fragment (inside a full Inject node export):

```json
{
  "props": [{"p": "payload"}],
  "payload": "{\"demo\":{\"source_id\":\"demo\",\"obj_counter\":{\"person\":{\"max_val\":3}}}}",
  "payloadType": "json",
  "once": false,
  "repeat": "",
  "crontab": ""
}
```

Do not put `{"payload": ...}` inside that string: it would create
`msg.payload.payload` and the transform would not see the supplied schema. Test
the exported Inject configuration itself, not just a separately handwritten msg.
Verify valid, zero, missing, malformed, one-source and multi-source results with
the installed JSONata version; a structurally valid flow is not a behavior check.

## When to use JSONata vs Function

- JSONata handles: property access, filtering, mapping, counting, sorting, conditional values, string interpolation
- Function node needed when: stateful logic across messages, external module imports, complex async operations, multiple output ports with different routing logic
