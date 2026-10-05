# Live Device Access via the EAIS MCP

The optional EAIS MCP integration (`eais-gateway-mcp`) exposes a
running EdgeAI Station to an agent over the Model Context Protocol. When it is connected you can
read **live** device state instead of reasoning only from this skill's static resources.
This reference applies only when the tools are already available. No MCP installation is
required to use this skill.

## Optional by design

The MCP is **never required**. Most users run these skills with no reachable station.

1. Check whether EAIS MCP tools are present in your current tool list.
2. If they are, call `list_devices` **first** — it is the only way to learn which Device IDs exist.
3. If they are not present, or every device is unreachable, say so **once**, then continue with
   this skill's static resources and ask the user for logs/exports as usual.

Do not ask the user to install or configure the MCP in the middle of a task, and never block a
deliverable on it.

## Tool inventory

Every domain tool takes a `device` argument: the Device ID string reported by `list_devices` (for
example `<STATION_ID>`) — not a URL, not a hostname.

| Tool | Returns |
|------|---------|
| `list_devices` | Configured Device IDs, base URL, cached auth/availability status |
| `gateway_health` | Gateway status and which child servers are mounted |
| `device_get_time` | System time and configured timezone |
| `device_get_ntp_status` | Clock sync state and active NTP servers |
| `device_get_network_config` | Interfaces, IPs, link state, gateways, DNS |
| `video_list_media` | Media assets with IDs and names |
| `video_get_media_details` | One media asset (by `media_id`) |
| `video_list_ai_processors` | Registered AIPs with IDs, names, types |
| `video_get_processor_details` | One AIP (by `processor_id`) |
| `video_list_pipelines` | Pipelines with IDs, names, status |
| `video_get_pipeline_details` | One pipeline (by `pipeline_id`) — config and runtime status |
| `observability_query_loki` | Log lines for a LogQL query over a time range |
| `observability_get_grafana_metrics` | Prometheus time-series for a PromQL range query |

Your MCP client may namespace these (e.g. `mcp--eais--video_list_pipelines`). Match whatever
appears in your tool list rather than assuming a prefix.

## Hard limits — read before planning

- **Every tool is read-only.** There is no tool to create, update, delete, deploy, restart, or
  upload anything. Never describe an MCP call as applying a change.
- **No Node-RED flow access.** Flows cannot be fetched or deployed through the MCP. Keep working
  from flow JSON found in the workspace or supplied by the user.
- **No UIBuilder source access.** Dashboard HTML/CSS/JS cannot be read or written.
- **No AIP packaging or pipeline control.** On-device `eais-tools` remains the only path for
  build, export, registration, and pipeline test.
- **The MCP covers a small read-only subset of MS2/MS3.** This skill's own resources remain the
  authority for every endpoint the MCP does not expose.

Treat the MCP as a way to *observe* the station and *ground* your output in real identifiers and
real logs. Everything that changes the station is still performed by the user.

### Verify log source and availability

Log availability and device routing depend on the connected integration. Do not assume
that a returned log stream belongs to the requested device solely from the tool arguments.

Probe with a cheap, narrow query first. Cross-check that returned lines plausibly belong to the
device you expect, and state the uncertainty if you cannot confirm it. If the call errors or
returns nothing, fall back to on-device logs.

## Querying logs (LogQL)

Label values are **deployment-specific** and are not documented by the MCP, which exposes no
label-discovery endpoint. Only `job="nodered"` appears in the MCP's own documentation and tests —
treat every other label value as a guess until you observe it in a result.

Discover empirically: start from a stream selector you have evidence for, read the `labels` object
attached to each returned line, then narrow using the exact pairs you saw.

```logql
{job="nodered"}                      # evidenced in the MCP's own docs and tests
{job="nodered"} |= "error"           # substring filter
```

Do not invent job names, container names, or service labels in a query you present as ready to run.
If you must guess, label it as a guess and give the user the discovery query as well.

**Cost control:** `limit` defaults to 100 and is capped at 5000; `start`/`end` default to the last
hour. Narrow the time window around the event you are investigating instead of raising `limit`.

## Querying metrics (PromQL)

`get_grafana_metrics` is a **range** query: `query` plus optional `start`/`end` (default: last
hour) and `step` (default `60s`).

Metric names are deployment-specific. Confirm a series exists before building an expression on top
of it:

```promql
up                                   # which scrape targets are alive
```

Prefer a coarse `step` over a long window to keep responses small, and read the returned
`total_series` before asking for more.

## For Node-RED Flow Tasks

The MCP cannot read or deploy flows, so it does not change how you author them. What it does change
is the quality of two things you would otherwise have to guess: **device identifiers** and
**runtime evidence**.

### Use real identifiers in `http request` nodes

The skill's device-API section has you locate an endpoint, pull its schema, and build a request.
The MCP supplies the values that go into that request:

| You need | Tool |
|----------|------|
| A real `pipeline_id` for an `/ms3/pipeline/{id}` call | `video_list_pipelines` |
| A real `media_id` for a media or snapshot call | `video_list_media` |
| A real AIP id, and the classes it actually exposes | `video_list_ai_processors`, `video_get_processor_details` |
| The device's current network/IP configuration | `device_get_network_config` |
| Device clock and NTP state, when timestamps look wrong | `device_get_time`, `device_get_ntp_status` |

Prefer a real ID read from the station over a placeholder. When no device is reachable, keep using
placeholders and say explicitly that they must be substituted.

The MCP is **not** a substitute for the OpenAPI resources. It exposes a small read-only subset;
`ms2-endpoints.md` / `ms3-endpoints.md` and the specs they index remain the authority for request
and response schemas, and for every endpoint the MCP does not cover.

### Read runtime errors instead of predicting them

`{job="nodered"}` is the one stream selector the MCP itself documents, which makes Node-RED runtime
errors the most reliably reachable logs:

```logql
{job="nodered"} |= "error"
```

Use it to check whether a flow you are reviewing is actually failing at runtime, and what the real
message is, before proposing a fix. Read the `labels` on returned lines to discover the other
selectors this deployment uses.

This is evidence, not a debugger. A `catch` node wired to a logging path is still the correct
in-flow mechanism, and a `debug` node is still how you observe a message shape.

### What the MCP cannot do here

- **It cannot fetch deployed flows.** Locate flow JSON in the workspace, or ask the user to export
  it from the editor. There is no `get_flows` tool despite what the MCP's roadmap documents.
- **It cannot deploy or update flows.** Deliver flow JSON plus import instructions, exactly as
  before. Never tell the user a flow was applied.
- **It cannot restart services or trigger a redeploy.**
