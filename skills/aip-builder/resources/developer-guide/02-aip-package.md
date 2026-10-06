# AIP Developer Guide — Starting a Project & Package Structure

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 2. AIP development guide

### 2.1. Starting a new project

Two main approaches inside JupyterLab:

**Clone a repository**:

1. Open DevTools → AIP Builder → Git tab
2. Click “Clone a Repository”
3. Ensure you’re inside `/data` before cloning (⚠️ persistence requirement)

**Manual import**:

- Upload or drag & drop files into `/data`

### 2.2. AIP package structure

> ℹ️ **Note**: Contact your vendor for access to the AIP template repository (DevKit).

```shell
/ (root)
    CHANGELOG.md                         # Mandatory
    README.md                            # Mandatory
    callback.py                          # Mandatory (callback implementation)
    manifest.json                        # Mandatory (AIP metadata)
    bin/
        build.sh                         # Recommended: model build (ONNX→TRT etc.)
    configs/
        config_infer_primary_xxxx.txt    # Mandatory (primary detector)
        config_tracker_xxxx.yml          # Optional (tracker config)
    localdev.ipynb                       # Optional automation notebook
    models/
        <AIP_UUID>_Primary_Detector/
            1/                           # Mandatory (TRT engine)
            config.pbtxt                 # Mandatory (Triton model config)
            labels.txt                   # Optional (class labels)
            model.etlt                   # Source model (DO NOT bundle your source file for distribution)
    resources/
        Logo.png                         # Mandatory (AIP logo)
```

> ⚠️ **Warning**: The AIP prefix (e.g. `AIPV1DKE0001`) is assigned by EDGEMATRIX and must be unique.

