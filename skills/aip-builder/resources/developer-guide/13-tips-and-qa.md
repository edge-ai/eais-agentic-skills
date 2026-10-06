# AIP Developer Guide — Tips & Q&A

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 8. Tips

### 8.1. Testing your AIP locally on JupyterLab

The JupyterLab container includes all the necessary environment to develop custom DeepStream pipelines with GStreamer utilities.

Before all it can be useful you test if your configuration files are working properly in a simple pipeline.

Please note that your AIP AI models should be first provisioned on Triton (registered).

Here is an example of Gstreamer pipeline to test from a terminal:

```bash
gst-launch-1.0 \
    nvurisrcbin uri=file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_1080p_h264.mp4 cudadec-memtype=0 file-loop=1 \
    ! nvvidconv ! queue ! nvstreammux0.sink_0 nvstreammux name=nvstreammux0 batch-size=1 \
    ! queue ! nvinferserver config-file-path="/data/aip/AIPV1XXX0001/configs/config_infer_plan_engine_primary.txt" batch-size=1 interval=0 \
    ! queue ! nvdslogger ! queue ! fakesink sync=0
```

Note: replace the `AIPV1XXX0001` folder name with your own AIP UUID.

As an output you should see the FPS metrics of your AI model in this pipeline structure.

### 8.2. Working with Git

You can easily clone a remote Git repository from a terminal in the Jupyter Lab environment:

```bash
git clone https://github.com/<org>/<repo>.git
```

When prompted, authenticate with your GitHub username and a Personal Access Token as the password. Do not embed the token in the remote URL or cache credentials on shared devices — it would persist in `.git/config` and shell history.

### 8.3. Tail the [ms3] videostreaming micro-service logs

From the version 36.3.0 update pack 3 it is possible to directly access the logs from your Jupyter Lab terminal.

To do so simply run the following command:

```bash
tail -f /var/log/edgeai/videostreaming/journal.log
```

### 8.4. TensorRT trtexec advanced usage tips

**FP16 (`--fp16`)**: Use half-precision (FP16) to reduce inference latency and memory usage, suitable for Edge/GPU deployments.

**Workspace memory (`--workspace`)**: Increase workspace (e.g., 4096 MB) to allow better optimization during engine building.

**Dynamic Shapes**: Adjust `--minShapes`, `--optShapes`, and `--maxShapes` for flexible batch sizes or resolutions:  
`--minShapes=1x3x640x640 --optShapes=8x3x640x640 --maxShapes=16x3x640x640`

**Timing Cache**: Use `--timingCacheFile` to speed up subsequent builds:  
`--timingCacheFile=timing.cache`

**Use Spin Wait (`--useSpinWait`)**: Improve latency consistency by reducing thread sleep overhead.

Example command with dynamic batch sizes:

```bash
trtexec --fp16 --workspace=4096 \
    --onnx=yolov8m_pba.pt.onnx \
    --minShapes=1x3x640x640 --optShapes=8x3x640x640 --maxShapes=16x3x640x640 \
    --saveEngine=yolov8m_pba.engine \
    --timingCacheFile=timing.cache \
    --useSpinWait
```

---

## 9. Q&A

### 1. My AIP is not displayed in the AI Processors page

⚠️ First, please check that the name of your AIP root folder matches the name you have chosen in the manifest.json file.

Additionally run the `manifest_json_validator.py` from the utils folder to verify the manifest.json file structure is valid.

If it still does not work please try to forcibly make a scan of your AIP folder calling the following API endpoint from a shell in your Jupyter Lab environment.

Force rescan:

```bash
curl -X 'POST' 'http://ms3_videostreaming:8000/aiprocessor/scan/AIPV1DKE0001' -H 'accept: application/json' -d ''
```

### 2. I cannot compile `model.etlt` from the devkit template

The aibox-devkit archive does not contain the binary of the model but just its reference on Github LFS. You have to replace it with your own model.

You can find the original face detect model provided by Nvidia here:

- <https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/facenet>

### 3. My Triton configuration is invalid

Try to load your AIP model using tritonserver local binary to introspect your config file.

Test manually:

```bash
/opt/tritonserver/bin/tritonserver --model-repository=./models/AIPV1DKE0001_Primary_Detector --log-verbose=1
```
