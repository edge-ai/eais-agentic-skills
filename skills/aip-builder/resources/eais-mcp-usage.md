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

## For AIP Development Tasks

This is the strongest fit for the MCP: an AIP is developed off-device but only observable
on-device, and every observation the skill's troubleshooting section asks for is a read.

### Confirm what the station actually has

Before assuming a package state, read it:

| Question | Tool |
|----------|------|
| Did my AIP register after `eais-tools aip build`? | `video_list_ai_processors` |
| What classes / config / version does the platform think it has? | `video_get_processor_details` |
| Is a pipeline using it, and is it running? | `video_list_pipelines`, `video_get_pipeline_details` |
| What media is available to attach as an input source? | `video_list_media` |

A manifest change auto-unregisters the AIP and detaches it from pipelines. `video_list_ai_processors`
is the fastest way to confirm whether that happened — do not infer it from a local file diff.

### Ground the troubleshooting table in live data

The symptoms in the skill's troubleshooting section map onto MCP reads:

| Symptom | Read this instead of guessing |
|---------|-------------------------------|
| Callback stopped producing data | Logs around the failure window (`observability_query_loki`) |
| FPS drops when callback is active | Pipeline FPS series (`observability_get_grafana_metrics`) |
| Merge timeout | Logs at the merge interval, plus the same FPS/GPU series |
| TRT engine fails to load | Startup logs for the pipeline's launch window |
| `manifest.json` rejected | `video_get_processor_details` for what the platform parsed |
| Pipeline starts but no detections | `video_get_pipeline_details` for runtime status and attached sources |

For GPU and memory pressure — the metrics the developer guide calls out as critical before
attaching more input sources — use `get_grafana_metrics`, confirming the series name exists before
building an expression on it.

### Crash-window workflow

When a pipeline fails, correlate rather than browse:

1. `video_get_pipeline_details` — capture status and the AIP under test.
2. `observability_query_loki` over a **tight** window around the failure, with `direction`
   defaulting to `backward` so the most recent lines come first.
3. `observability_get_grafana_metrics` over the *same* window — FPS or GPU collapsing before the
   first error line usually separates a resource problem from a callback exception.
4. Report the window you queried and the labels you actually matched, so the user can reproduce it.

### What still requires the device

`eais-tools` remains the only way to build, export, check, or test an AIP, and logs may be
unreachable off-device. When the MCP cannot answer, fall back to the
skill's documented commands — `eais-tools aip check`, `eais-tools pipeline test`, and reading
the on-device log file directly — and ask the user to run them.
