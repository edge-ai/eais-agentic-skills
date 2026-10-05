# AIP Developer Guide — Hardware & Conversion Tools

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 1. Development environment

> ℹ️ **Note**: An engineering license is required to access the development tools.

### 1.1. EdgeAI station hardware

#### Hardware specifications for EX5

- **CPU**: 8-core ARM Cortex-A78AE (64-bit, ARM v8.2)
- **GPU**: NVIDIA Ampere, 1024 CUDA cores, 32 Tensor Cores (FP32 / FP16 / INT8)
- **RAM**: 16GB LPDDR5 (102.4 GB/s bandwidth)
- **Storage**: 256GB onboard
- **AI Performance**: Up to 100 TOPS
- **Video**: 4K@60fps encode/decode (H.264 / H.265 / VP8 / VP9) with HW acceleration

### 1.2. Pre-installed Libraries and Compilation Tools

> ℹ️ **Note**: Environment based on Jetpack 6.0 Docker base image (aligned with production microservices).

Key categories:

#### CUDA & TensorRT

- CUDA 12.2.1
- TensorRT 8.6.2 (via DeepStream base)

#### GStreamer stack

- core + base/good/bad/ugly/libav
- dev headers
- RTSP server

#### Deep Learning / Numerical

- OpenBLAS, LAPACK, BLAS
- HDF5, OpenCV, Protobuf
- cuDLA

#### Python & ML

- `pybind11`, `pandas`, `onnx`, `onnxruntime_gpu==1.19.0`, `onnxsim`, `torch==2.3.0`, `torchvision==0.18.0a0+6043bc2`, `nvidia-tao==5.5.1`
- `pyds==1.1.11`, `polygraphy`, `eais_tools`

#### Compilation / Toolchain

- `build-essential`, `cmake`, `llvm-15`, `openmpi`

#### System / Utilities

- `curl`, `nano`, `zsh`, `docker-ce-cli`, `protobuf-compiler`, `hdf5-tools`, `zip`, `gnupg-agent`

#### DeepStream extras

- Triton client utilities
- `update_rtpmanager.sh` patch
- Additional multimedia deps via `user_additional_install.sh`

#### Dev / UI

- Jupyter Server + JupyterLab (incl. Japanese support)

### 1.3. Jupyter Lab IDE

> 🚨 **Important**: Container changes (installed packages, modified files outside mounted volumes) are ephemeral. Persist automation in scripts.

**Persistence**: Store all project data under `/data` (mounted & persistent).

Features:

- Notebooks for iterative development
- Terminal access inside the container
- Integrated Git panel (clone, commit, branch operations)

### 1.4. Available conversion tools

#### `trtexec`

Use for ONNX → TensorRT conversion, benchmarking, and profiling.

Key advantages:

- Supports FP32/FP16/INT8
- Generates timing + memory stats
- Rapid prototyping for engine tuning

#### `tao-converter`

Used for TAO Toolkit `.etlt` → TensorRT engine conversion.

Supports:

- Precision selection (FP16 / INT8)
- Input shape specification

---
