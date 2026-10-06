# AIP Developer Guide — Testing & Debugging

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 4. Testing and Debugging

### 4.1. AIP registration and pipeline creation

Registered AIPs appear in “AI Processors”. Manifest modifications trigger auto-unregister.

Once the AIP is registered it can be used in a pipeline. If the AIP manifest is changed it will be automatically unregistered and detached from the pipelines that were created. So you need to edit the concerned pipelines.

#### Autoreload Pipeline Feature

When the Autoreload Pipeline checkbox is enabled during pipeline creation, the pipeline will automatically start when the device or service is restarted. Enabling this feature helps minimize pipeline downtime after a restart.

If you do not need the auto-restart function, deselect the checkbox when creating the pipeline.

This feature is enabled by default.

> ℹ️ **Note**: In engineering mode or development mode, this feature will not operate even if the checkbox is enabled.

### 4.2. Log system

The EdgeAI station stack includes a comprehensive logging system to monitor and debug operations. This system based on Grafana Loki captures logs related to the different micro-services including the video processing and AI processors orchestration.

Logs can be retrieved, filtered, and analyzed to diagnose issues, track system behavior directly from within the device.

Additionally, the log levels can be adjusted to provide more debugging information if needed (cf. device setup section).

### 4.3. Performance metrics

One of the key metrics for the AIP hardware utilization are the GPU and memory usage. It is critical to monitor those values to prevent device over utilization, performance loss and in the worst case potential unresponsiveness or crash. Be sure before creating new pipelines and attaching input sources that your device load is not too high.

#### Global GPU utilization

Monitor overall GPU usage across all running AIPs and pipelines.

#### General memory consumption (GPU memory is shared memory)

Track both system and GPU memory usage as they share the same physical memory pool on the device.

When looking at your pipeline performance you can check the metrics for the Triton server and the pipelines FPS. It will give you a clear understanding of the inference processing speed for the different video streaming pipelines and AIP.

#### Triton inference server performance

Monitor inference latency, throughput, and queue depths for AI model execution.

#### FPS monitoring of the pipeline

Track real-time frame processing rates for each pipeline to ensure optimal performance.

> ⚠️ **Warning**: From version `36.3.0u3`, AIPs may run locally (not via Triton); Triton metrics may not reflect performance.

### 4.4. Portability on EX3

We are currently evaluating if there is any downside porting AIP built on the EX5 environment to the EX3 platform. We don't have for the moment any evidence of performance issues for the demo applications we have developed.

