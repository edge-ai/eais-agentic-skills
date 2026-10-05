# AIP Developer Guide — eais-tools CLI Reference

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 7. EAIS Tools Client Util for AIP Development

### 7.1. What is the eais-tools ?

A CLI to assist AIP lifecycle: service ops, config validation, pipeline testing, distribution, performance evaluation, callback scaffolding.

Key capabilities:

- Service management (`service restart`, logs)
- Validate Triton / DeepStream configs
- AIP build & export
- Callback generation (ROI / line crossing)
- Performance test harness

### 7.2. How to Use It ?

The eais-tools CLI is organized into several command groups, each targeting specific aspects of AIP development and management. Below is a guide on how to use its key features.

#### Service Management

Restart a service:

```bash
eais-tools service restart --service_name ms3
```

Follow logs for a service:

```bash
eais-tools logs ms3
```

#### Configuration Validation

Validate a Triton model configuration:

```bash
eais-tools configs triton check --aip AIP_UUID --model MODEL_NAME
```

Validate a DeepStream configuration:

```bash
eais-tools configs ds check --aip AIP_UUID
```

#### AIP Management

Check the AIP root folder for missing files and proper setup:

```bash
eais-tools aip check --uuid AIP_UUID
```

Build the AIP distribution package:

```bash
eais-tools aip build --uuid AIP_UUID
```

Export the AIP distribution as a tar.gz archive for the AIP store:

```bash
eais-tools aip export --uuid AIP_UUID
```

#### Pipeline Testing

Test a pipeline with a specified number of media inputs:

```bash
eais-tools pipeline test --aip AIP_UUID --inputs_num 2
```

Clean up test pipelines and media:

```bash
eais-tools pipeline clean
```

#### Callback Generation

Generate a callback.py skeleton file for video analytics:

```bash
eais-tools aip generate-callback --output callback.py --enable-roi --enable-line-count
```

#### AIP Performance Test

Generate a performance test report for your selected AIP (check the installed command's `--help` for supported options):

```bash
eais-tools check perf --aip AIPV1XXX0001 --input-sources 8 --input-src-mp4 /opt/nvidia/deepstream/deepstream/samples/streams/sample_1080p_h264.mp4 --pipelines 1 --inference-drop 0 --duration 60
```

The eais-tools CLI is a powerful utility for developers working on AIP solutions, providing essential tools to simplify and automate common tasks in the development lifecycle.

For more information, check the installed help for each group/command:

```bash
eais-tools --help
```
