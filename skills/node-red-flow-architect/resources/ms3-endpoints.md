# Video Analytics API — Endpoint Index

> Compact index of `ms3-openapi.json` (OpenAPI 0.19.0, 50 operations). The full spec is **too large to read in one pass** — use this index to find the operation, then grep the JSON for its `operationId` to pull the exact request/response schema.

**Server base path:** `/ms3` — prefix every path below with it (e.g. `/ms3/aiprocessors`).

Pipelines CRUD & lifecycle, media sources, AI Processor (AIP) upload/registration, snapshots.

## How to get the full schema for one endpoint

```bash
# Find the operation block (request body, params, responses) by operationId:
grep -n '"<operationId>"' ms3-openapi.json
```

Or load the spec into a JSON tool and navigate to the path. **Do not read the whole spec file** — it will be truncated.

## Endpoints by tag

### AI Processors

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| POST | `/aiprocessor/scan` | Scan the AI Processor folder for all AI Processors | `scan_all_aiprocessors_aiprocessor_scan_post` | — | — |
| POST | `/aiprocessor/scan/{uuid}` | Scan the AI Processor folder for new AI Processors | `scan_aiprocessor_aiprocessor_scan__uuid__post` | — | `uuid` |
| POST | `/aiprocessor/upload` | Upload an AI Processor | `upload_aiprocessor_aiprocessor_upload_post` | body | — |
| DELETE | `/aiprocessor/{uuid}` | Delete the specified AI Processor | `delete_aiprocessor_aiprocessor__uuid__delete` | — | `uuid` |
| GET | `/aiprocessor/{uuid}` | Get the details of the specified AI Processor | `get_aiprocessor_aiprocessor__uuid__get` | — | `uuid` |
| GET | `/aiprocessor/{uuid}/changelog` | Get the changelog of the specified AI Processor | `get_aiprocessor_changelog_aiprocessor__uuid__changelog_get` | — | `uuid` |
| GET | `/aiprocessor/{uuid}/icon` | Get the icon of the specified AI Processor | `get_aiprocessor_icon_aiprocessor__uuid__icon_get` | — | `uuid` |
| GET | `/aiprocessor/{uuid}/labels` | Get the labels of the specified AI Processor PGIE model | `get_aiprocessor_labels_aiprocessor__uuid__labels_get` | — | `uuid` |
| POST | `/aiprocessor/{uuid}/options/validate` | Validate the callback option values of the specified AI Processor | `validate_callback_option_values_aiprocessor__uuid__options_validate_post` | body | `uuid` |
| POST | `/aiprocessor/{uuid}/register` | Register the specified AI Processor on the Triton server | `register_aiprocessor_aiprocessor__uuid__register_post` | — | `uuid` |
| GET | `/aiprocessor/{uuid}/status` | Get the status of the specified AI Processor | `check_aiprocessor_status_aiprocessor__uuid__status_get` | — | `uuid` |
| POST | `/aiprocessor/{uuid}/unregister` | Unregister the specified AI Processor from the Triton server | `unregister_aiprocessor_aiprocessor__uuid__unregister_post` | — | `uuid` |
| GET | `/aiprocessors` | Get all the registered AI Processors | `get_all_aiprocessors_aiprocessors_get` | — | — |

### Media

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| POST | `/media` | Create media interface | `create_media_media_post` | body | — |
| DELETE | `/media/{uuid}` | Delete Specified Media | `delete_media_media__uuid__delete` | — | `uuid` |
| GET | `/media/{uuid}` | Get Detailed Information of the Specified Media | `get_media_media__uuid__get` | — | `uuid` |
| PUT | `/media/{uuid}` | Update media interface | `update_media_media__uuid__put` | body | `uuid` |
| GET | `/media/{uuid}/preview` | Get the preview image of the specified Media | `get_media_preview_media__uuid__preview_get` | — | `uuid` |
| PUT | `/media/{uuid}/preview` | Update the preview image of the specified Media | `update_media_preview_media__uuid__preview_put` | — | `uuid` |
| GET | `/media/{uuid}/status` | Check the specified Media is playable | `check_media_status_media__uuid__status_get` | — | `uuid` |
| GET | `/medias` | Get All Available Media | `get_all_media_medias_get` | — | — |

### Pipelines

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| POST | `/pipeline` | Create new pipeline | `create_new_pipeline_pipeline_post` | body | — |
| POST | `/pipeline/snapshot/download` | Download the image of the specified snapshot records | `download_snapshots_pipeline_snapshot_download_post` | body | — |
| DELETE | `/pipeline/snapshot/{uuid}` | Delete the specified snapshot record | `delete_snapshot_pipeline_snapshot__uuid__delete` | — | `uuid` |
| GET | `/pipeline/snapshot/{uuid}` | Get the image of the specified snapshot record | `show_snapshot_pipeline_snapshot__uuid__get` | — | `uuid` |
| DELETE | `/pipeline/snapshots` | Delete the specified snapshot records | `delete_snapshots_pipeline_snapshots_delete` | — | — |
| GET | `/pipeline/snapshots` | Get snapshot record list | `list_snapshots_pipeline_snapshots_get` | — | — |
| GET | `/pipeline/snapshots/download` | Download the images of the specified snapshot records | `download_snapshots_pipeline_snapshots_download_get` | — | — |
| DELETE | `/pipeline/{uuid}` | Delete the specified pipeline | `delete_pipeline_pipeline__uuid__delete` | — | `uuid` |
| GET | `/pipeline/{uuid}` | Get the details of the specified pipeline | `get_pipeline_pipeline__uuid__get` | — | `uuid` |
| PUT | `/pipeline/{uuid}` | Update pipeline | `update_pipeline_pipeline__uuid__put` | body | `uuid` |
| GET | `/pipeline/{uuid}/fps` | Get the FPS of the specified pipeline | `get_pipeline_fps_pipeline__uuid__fps_get` | — | `uuid` |
| GET | `/pipeline/{uuid}/hls` | Serve Hls Stream | `serve_hls_stream_pipeline__uuid__hls_get` | — | `uuid` |
| GET | `/pipeline/{uuid}/hls/{segment}` | Serve Hls Segment | `serve_hls_segment_pipeline__uuid__hls__segment__get` | — | `uuid`, `segment` |
| GET | `/pipeline/{uuid}/options` | Get pipeline callback options | `get_callback_options_pipeline__uuid__options_get` | — | `uuid` |
| PUT | `/pipeline/{uuid}/options` | Update pipeline callback options | `update_callback_options_pipeline__uuid__options_put` | body | `uuid` |
| POST | `/pipeline/{uuid}/reset_analytics` | Reset Analytics Counter | `reset_analytics_counter_pipeline__uuid__reset_analytics_post` | — | `uuid` |
| POST | `/pipeline/{uuid}/set_tiler/{index}` | Do Change Tiler | `do_change_tiler_pipeline__uuid__set_tiler__index__post` | — | `uuid`, `index` |
| POST | `/pipeline/{uuid}/snapshot/trigger` | Trigger Snapshot | `trigger_snapshot_pipeline__uuid__snapshot_trigger_post` | — | `uuid`, `input_id`, `osd` |
| POST | `/pipeline/{uuid}/start` | Start Pipeline | `start_pipeline_pipeline__uuid__start_post` | — | `uuid` |
| GET | `/pipeline/{uuid}/status` | Get the status of the specified pipeline | `get_pipeline_status_pipeline__uuid__status_get` | — | `uuid` |
| POST | `/pipeline/{uuid}/stop` | Stop Pipeline | `stop_pipeline_pipeline__uuid__stop_post` | — | `uuid` |
| GET | `/pipeline/{uuid}/tiler` | Get Tiler | `get_tiler_pipeline__uuid__tiler_get` | — | `uuid` |
| GET | `/pipelines` | Get all the registered pipelines | `get_all_pipelines_pipelines_get` | — | — |

### Settings

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/device/ms3/log-level` | Get device global log level | `get_global_log_level_device_ms3_log_level_get` | — | — |
| PUT | `/device/ms3/log-level` | Set device global log level | `set_global_log_level_device_ms3_log_level_put` | body | — |
| GET | `/global/license` | Get device license | `get_license_from_ms2_global_license_get` | — | — |
| GET | `/global/stack-mode` | Get device stack mode | `get_stack_mode_global_stack_mode_get` | — | — |

### QA

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/qa` | Check if the QA test is running | `get_qa_status_qa_get` | — | — |

### General

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/metrics` | Get Prometheus metrics | `get_metrics_metrics_get` | — | — |
