# AIP Developer Guide — Model Conversion & DeepStream/Triton Configs

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

### 2.4. Converting the AI model

Common workflow:

#### PyTorch → ONNX → TRT

1. Export scripted/static ONNX
2. Run `trtexec --onnx=...` with shapes & precision flags

#### TensorFlow → ONNX → TRT

- Use `tf2onnx` or SavedModel export → ONNX → `trtexec`

#### ONNX → TRT

- Direct with `trtexec`

#### TAO (.etlt) → TRT

- Use `tao-converter` with key + shape/precision flags

### 2.5. Preparing the configuration files for DeepStream and Triton

> ℹ️ **Note**: Currently only TensorRT backend supported on-device.

#### Configuring nvinferserver

The DeepStream `nvinferserver` plugin serves as the bridge between DeepStream and Triton Inference Server. Proper configuration is essential for optimal inference performance.

**Model Configuration**: Define the path to your model files (ONNX, TensorRT, etc.), the preprocessing parameters, and the output layers.

**Batch Size and Memory Management**: Specify how many inputs to process in a batch and configure GPU memory usage.

**Backend Configuration**: Set up the TensorRT backend for inference.

More details about the `nvinferserver` plugin configuration: [DeepStream nvinferserver Configuration](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_plugin_gst-nvinferserver.html).

#### Triton Inference Server Configuration

Triton Inference Server requires a model repository and a `config.pbtxt` file for each model to define model behavior, backend settings, and optimization techniques such as batching.

For the general configuration of the Triton Inference Server please refer to this documentation: [Triton Inference Server Documentation](https://github.com/triton-inference-server/server/blob/main/docs/README.md)

#### Configuring Triton Inference Server

**Model Repository Setup**: Organize your models into a structured directory where each model has its own folder containing the model files (e.g., TensorRT engine) and a `config.pbtxt` file.

**Model Configuration (config.pbtxt)**:

- **input/output tensors**: Define the input and output formats for the model.
- **batching**: Enable dynamic batching to optimize inference throughput.
- **optimization**: Configure model optimizations like FP16 or INT8 precision.

#### Sample Configuration Files

Triton documentation provides detailed examples of the `config.pbtxt` file in their [model configuration guide](https://github.com/triton-inference-server/server/blob/main/docs/model_configuration.md).

