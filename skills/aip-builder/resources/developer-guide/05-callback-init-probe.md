# AIP Developer Guide — Callback — Overview, Initialize & Probe

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 3. Callback specifications

### 3.1. Callback model (overview)

AIP can freely analyze and shape the inference results (in NVIDIA's proprietary format) generated for each frame by the inference part of the pipeline, and periodically send the data to Node-RED, etc. AIP developers can implement a Python script (`callback.py`) to analyze the inference results and include it in the AIP package. This Python implementation is called a callback. The callback is executed for all frame buffers immediately after inference, tracking, and analytics are finished, so the results can be obtained and processed. The callback is divided into three functions: a probe function, a merge function, and a push function. An initialization function is also provided that can define and initialize class variables that can be used commonly within `callback.py`. AIP developers implement the initialization, probe, and merge functions in `callback.py`. For detailed implementation examples of each function, please also refer to the sample AIP code provided by EDGEMATRIX.

**Probe function**: A function executed every frame using GStreamer Probe. Since the execution speed of this function has a large effect on FPS, this function is provided for the purpose of parsing NVIDIA format inference results as quickly as possible.

**Merge function**: A function executed at regular intervals. The default interval is 1 second, but it can be freely changed when setting up the pipeline. It is used to aggregate data within the target period by processing all the outputs of the probe functions executed within the interval (ex. 1 second) together. For example, it can output the minimum and maximum numbers ​​of detected car objects among the frame buffers for the last 1 second.

**Push function**: A function executed at regular intervals longer than the merge function. The default is 5 seconds, but it can be freely changed when setting up the pipeline. This function periodically sends the results of the merge function to another service such as Node-RED. This function cannot be implemented in `callback.py`.

### 3.2. Initialization function

A function that is executed once at the start of the pipeline. This function can be used to define global variables for the class. It also selects the data to be extracted. By not extracting unnecessary data, the processing time of the probe function can be reduced. The name of this function is `initialize()`, and it has no arguments and no return value.

> ⚠️ **Warning**: Do not override the `__init__()` function, but use the `initialize()` function instead. If you override the `__init__()` function in an incorrect way, class variables that would normally be available will not be initialized and will become unusable.

#### Metadata extraction settings

To set the scope of metadata extraction, use `self.data_parser_config`. This variable is a dictionary with Boolean values, and you can choose whether or not to perform extraction by setting the value of a specific key. The configurable items are as follows:

- `frame_meta_list`: Basic information about a frame. There are as many of these as there are input sources.
- `obj_meta_list`: Information about detected objects. Contains information such as class and coordinates. There are as many as the number of detected objects.
- `classifier_meta_list`: Additional inference information for a detected object. Holds the detection results of secondary inference models.
- `label_info_list`: List of labels of the given class. It exists in the classifier meta.
- `frame_user_meta_list`: A list of user metadata associated with the frame data. Analytics analysis results are included in this metadata.
- `obj_user_meta_list`: A list of user metadata associated with the object data. Analytics analysis results are included in this metadata.
- `display_meta_list`: Information about the shape to be drawn on the frame image.

> ℹ️ **Note**: For example, if there is no secondary inference model in the AIP, the developer can skip extraction by changing the `classifier_meta_list` setting to `False`.

These settings basically conform to the metadata structure provided by NVIDIA DeepStream. The metadata extracted based on these settings is converted into a Python object and can be referenced in the probe function as an argument named `data_dict`. For details about the metadata structure, see the [official NVIDIA documentation](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_plugin_metadata.html).

#### Example `initialize()`

```python
import logging
from numbers import Integral, Real
from typing import Any, List
import numpy as np

logger = logging.getLogger(__name__)

def initialize(self) -> None:
    # In this example, only PGIEs are present in the AIP
    # and only `frame_user_meta_list` is needed for
    # NvDsAnalytics analysis, so only these are read out.
    self.data_parser_config = {
        "frame_meta_list": True,
        "obj_meta_list": True,
        "classifier_meta_list": False,
        "label_info_list": False,
        "frame_user_meta_list": True,
        "obj_user_meta_list": False,
        "display_meta_list": False,
    }

    # AIP developers may implement any process here to be
    # performed during initialisation. Here, a dtype for
    # the frame is defined in order to efficiently parse
    # and aggregate the metadata in a Numpy array.
    self.frame_dtype = np.dtype([
        ('source_id', int),
        ('frame_num', float),
        ('num_obj_meta', float),
        ('ntp_timestamp', float),
        ('obj_counter', (float, len(self.pgie_classes or []))),
        ('analytics_roi', object),
        ('analytics_lcc', object)
    ])

    # AIP developers may define additional class variables as required.
    self.max_frames_in_batch = 0
    self.num_frames_in_batch = 0
    self.first_time = True
    self.default_frame_data = None
    self.analytics_roi_labels = {}
    self.analytics_lcc_labels = {}
    self.obj_coords_dict = {}
    self.invalid_metadata_count = 0
    self.source_capacity_limit = 16  # Example limit; match the AIP's supported inputs.
    if not self.pgie_classes:
        logger.warning("No primary model classes; class measurements unavailable")
```

#### Full access mode

By default, in `callback.py`, metadata is passed in as pre-parsed Python objects. This feature was designed to make it easier for users to handle metadata. However, this design introduces several limitations:

- Metadata is read-only, meaning that modifications made within `callback.py` generally cannot be reflected in the video output. (Custom rendering overlays are supported, however.)
- It is not possible to delete or modify text information added by PGIE or SGIE.
- User metadata created by custom C++ libraries cannot be accessed.

These limitations can become problematic when implementing more advanced AIP features. For example:

- When you need to handle user metadata generated by a custom library during inference and send it to Node-RED.
- When you want to change the font used for displaying objects detected by PGIE or SGIE (e.g., to display Japanese fonts).

> ℹ️ **Note**: The Noto CJK font is installed for Japanese. (`fonts-noto-cjk` is installed via apt.)
> For example, you can use `Noto Sans CJK JP` or the monospaced font `Noto Sans Mono CJK JP`. If you use a monospaced font, we recommend setting the font size to 12 or higher.

In such cases, AIP developers can gain access to the raw metadata buffer by setting `self.full_access = True` within the `initialize()` function. This allows you to work directly with the raw metadata buffer instead of the pre-parsed Python data. By using PyDS to parse and edit the metadata, you gain greater flexibility in implementation.

> 🚨 **Important**:
>
> - `self.full_access` is `False` by default. When `self.full_access` is set to `True`, you do not need to define `self.data_parser_config`. (If defined, it will be ignored internally.)
> - Instead of implementing `parse_batch_meta(self, data_dict: Any) -> Any`, you must implement `parse_batch_meta_full(self, gst_buffer: Any) -> Any`. The `gst_buffer` argument provides the raw metadata buffer for each frame, which can be processed using PyDS. The implementation must parse this buffer and return a Python object to be passed to the next processing stage.
> - To avoid memory management issues, the returned Python object must not include any pointer objects referencing the original buffer. Only use the parsed values.
> - EDGEMATRIX does not provide support for issues arising from the use of PyDS when `self.full_access = True` is enabled. Use at your own risk. Do not use this feature if you are unfamiliar with PyDS.

**Code example for overriding PGIE object labels with Japanese text:**

```python
class UserCustomCallback(CustomCallback):
    def initialize(self):
        self.full_access = True

    def parse_batch_meta_full(self, gst_buffer: Any) -> Any:
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
        l_frame = batch_meta.frame_meta_list
        while l_frame is not None:
            try:
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break

            l_obj = frame_meta.obj_meta_list
            while l_obj is not None:
                try:
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)

                    # Change the font size and color of the text
                    obj_meta.text_params.font_params.font_name = "Noto Sans CJK JP"
                    obj_meta.text_params.font_params.font_size = 8

                    # Change the text color to white
                    obj_meta.text_params.font_params.font_color.red = 1.0
                    obj_meta.text_params.font_params.font_color.green = 1.0
                    obj_meta.text_params.font_params.font_color.blue = 1.0
                    obj_meta.text_params.font_params.font_color.alpha = 1.0

                    # Change the background color to black with some transparency
                    obj_meta.text_params.set_bg_clr = 1
                    obj_meta.text_params.text_bg_clr.red = 0.0
                    obj_meta.text_params.text_bg_clr.green = 0.0
                    obj_meta.text_params.text_bg_clr.blue = 0.0
                    obj_meta.text_params.text_bg_clr.alpha = 0.5

                    # Set the Japanese text to be displayed
                    obj_meta.text_params.display_text = "テスト出力"

                except StopIteration:
                    break

                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break

            try:
                l_frame = l_frame.next
            except StopIteration:
                break

        return None

    def merge_and_analyze(self, frame_data_list: List[Any], frame_time_list: List[float]) -> Any:
        merged_data = {}
        return merged_data
```

### 3.3. Probe function

Purpose: Fast extraction per frame → outputs minimal structured object for merge phase.

> ⚠️ **Warning**: An unhandled exception drops the affected callback result, and
> sustained repeated failures can cause MS3 to stop callback processing. Handle
> expected malformed or missing metadata defensively. The exact retry/grace policy
> is a runtime concern and may change; callback code must not depend on it.
>
> ℹ️ **Note**: It is the callback that processes the analytics data in the metadata and sends it to Node-RED. To make the analytics data available in the Node-RED, the AIP developer must implement that logic in the callback. By default, the data is simply ignored and not sent to the Node-RED side. For an example of how analytics data processing is implemented, please refer to the sample AIP code provided by EDGEMATRIX.

The probe function parses the metadata structure for each frame, extracts the necessary data, and writes the result to the frame data queue. The goal of this function is to extract the data as fast as possible without dropping the FPS of the pipeline. The process to obtain data in the probe function can be divided into the following three steps. Developers only need to implement the creation of frame data in callback.py.

#### Metadata structure analysis

Since the size of the generated metadata entity is huge, it is loaded as a structure mainly consisting of pointers. Furthermore, the structure and list length take various forms depending on the pipeline configuration, the type of inference engine, etc. In this step, the format of the inference result structure is analyzed by following the pointers.

#### Selective reading of metadata entities

If you try to read data from all pointers in the metadata, the amount of data will become huge, and the FPS will decrease due to the increased processing time. Therefore, AIP provides the `self.data_parser_config` settings described in the previous section to allow you to selectively extract only the data you need from the structure. This reduces the time loss caused by expanding unnecessary data that is not going to be referenced.

#### Creation of frame data

AIP developers can freely extract and format the necessary information from the Python objects converted by the metadata adapter, allowing them to write the minimum amount of data to the next queue. The name of this function is `parse_batch_meta()`. The argument to this function is a `data_dict`, which is a Python object with the same structure as the framebuffer metadata, selectively extracted based on the configuration. The return value of this function is an arbitrary Python object, and the list of the output of this function is fed into the merge function via the frame data queue. The developer implements some processing to format the input metadata (usually to filter out only the data of interest) in this function.

#### Example helpers

```python
def reject_metadata(self):
    # One warning per callback lifetime; counters record subsequent rejections.
    if self.invalid_metadata_count == 0:
        logger.warning("Invalid callback metadata; rejected samples remain unknown")
    self.invalid_metadata_count += 1

def _init_frame_data(self, num_source_ids: int):
    """
    Here I Define additional functions to create default values for
    Numpy frame data.
    """
    # Initialise the data with the dtype structure for the frame by
    # filling it with zeros.
    frame_data = np.zeros((num_source_ids,), dtype=self.frame_dtype)

    # Check the number of PGIE classes.
    if self.pgie_classes is None:
        num_pgie_classes = 0
    else:
        num_pgie_classes = len(self.pgie_classes)

    # Assigning default values to zero-filled data.
    # In rare cases, some frames may be missing, so np.nan is used as the
    # default value so that missing frames can be distinguished.
    for source_id in range(num_source_ids):
        frame_data[source_id] = (
            source_id,                    # source_id
            np.nan,                       # frame_num
            np.nan,                       # num_obj_meta
            np.nan,                       # ntp_timestamp
            [np.nan] * num_pgie_classes,  # obj_counter
            None,                         # analytics_roi
            None                          # analytics_lcc
        )
    return frame_data

def _init_parse(self, batch_meta):
    """
    Here I Define additional functions to be performed only
    in the first frame.
    The number of input sources in the pipeline is obtained
    at this time, as it may vary depending on user preferences.
    Default values for Numpy frame data are also defined here.
    """
    # The number of input sources for the pipeline is obtained
    # from the batch meta and stored in a class variable.
    size = batch_meta.get('max_frames_in_batch')
    if (isinstance(size, bool) or not isinstance(size, Integral)
            or not 0 < size <= self.source_capacity_limit):
        self.reject_metadata()
        return False
    self.max_frames_in_batch = int(size)

    # Prepare default numpy frame data according to the number
    # of input sources in the pipeline.
    self.default_frame_data = self._init_frame_data(self.max_frames_in_batch)
    return True
```

`source_capacity_limit` is an example-local allocation bound, not a platform
variable. Set it to the AIP's supported input capacity. An invalid first batch
returns an empty typed array and retries
initialization on the next valid batch; it does not allocate from an untrusted size.

#### Example `parse_batch_meta`

```python
def parse_batch_meta(self, data_dict: Any) -> Any:
    """
    Function executed every frame.
    The implementation in this example can be performed in
    about 150-300 µs on EX5.
    """
    # In this example, there are variables (number of input sources,
    # default Numpy frame data) that we want to define after receiving
    # the initial data, so we define a function to be executed only
    # on the first frame.
    self.obj_coords_dict = {}
    batch_meta = data_dict.get('batch_meta') if isinstance(data_dict, dict) else None
    if not isinstance(batch_meta, dict):
        self.reject_metadata()
        return (self.default_frame_data.copy() if not self.first_time
                else np.empty((0,), dtype=self.frame_dtype))
    frames = batch_meta.get('frame_meta_list')
    if not isinstance(frames, list):
        self.reject_metadata()
        return (self.default_frame_data.copy() if not self.first_time
                else np.empty((0,), dtype=self.frame_dtype))
    if self.first_time:
        if not self._init_parse(batch_meta):
            return np.empty((0,), dtype=self.frame_dtype)
        self.first_time = False

    # Copying default values for Numpy frame data
    frame_data = self.default_frame_data.copy()

    # Get a Frame meta for each input source from the Batch meta and
    # write it to the Numpy frame data.
    for frame_meta in frames:
        if not isinstance(frame_meta, dict):
            self.reject_metadata()
            continue
        source_id = frame_meta.get('source_id')
        if (isinstance(source_id, bool) or not isinstance(source_id, Integral)
                or not 0 <= source_id < self.max_frames_in_batch):
            self.reject_metadata()
            continue
        source_id = int(source_id)

        # Basic frame information
        for key in ('frame_num', 'num_obj_meta', 'ntp_timestamp'):
            value = frame_meta.get(key)
            if (not isinstance(value, bool) and isinstance(value, Real)
                    and np.isfinite(value)):
                frame_data[source_id][key] = value

        # Object counter
        # (checks the Obj meta list one by one and counts the
        # number of detected objects per class).
        if self.pgie_classes is not None:
            objects = frame_meta.get('obj_meta_list')
            if not isinstance(objects, list):
                self.reject_metadata()
                continue
            counts = [0] * len(self.pgie_classes)
            valid_counts = True
            obj_coords = []
            for obj_meta in objects:
                class_id = obj_meta.get('class_id') if isinstance(obj_meta, dict) else None
                if (isinstance(class_id, bool) or not isinstance(class_id, Integral)
                        or not 0 <= class_id < len(self.pgie_classes)):
                    self.reject_metadata()
                    valid_counts = False
                    continue
                class_id = int(class_id)
                counts[class_id] += 1
                rect = obj_meta.get('rect_params')
                if isinstance(rect, dict):
                    values = [rect.get(key) for key in ('left', 'top', 'width', 'height')]
                    if all(not isinstance(v, bool) and isinstance(v, Real)
                           and np.isfinite(v) for v in values):
                        left, top, width, height = values
                        obj_coords.append((left + width / 2, top + height / 2, class_id))
            if valid_counts:
                frame_data[source_id]['obj_counter'] = counts
            self.obj_coords_dict[source_id] = obj_coords

        # Aggregation of Analytics plug-ins.
        # If the ROI Filtering plugin or Line Crossing plugin is activated,
        # the detection results can be checked in `frame_meta['frame_user_meta_list']`.
        # The `ObjInROIcnt` and `objLCCurrCnt` have the following Dict form.
        # `{'roi_1': 1, 'roi_2': 2}`
        # Key names are determined according to the user's pipeline settings
        # and cannot be known exactly in advance.
        # Therefore, the Python Object of type Dict, which is read out here,
        # is assigned directly to the Numpy frame data.
        user_meta = frame_meta.get('frame_user_meta_list')
        if isinstance(user_meta, list) and user_meta and isinstance(user_meta[0], dict):
            for output, key in (('analytics_roi', 'objInROIcnt'),
                                ('analytics_lcc', 'objLCCurrCnt')):
                value = user_meta[0].get(key)
                if isinstance(value, dict):
                    frame_data[source_id][output] = value

    # Send the created Numpy frame data to the next process.
    return frame_data
```

Only an observed empty `obj_meta_list` produces zero counts. Missing/malformed
lists or invalid class entries keep NaN counts, so incomplete detection metadata
cannot clear a downstream alarm as if no objects were detected. Merge converts
unknown numeric values to JSON null, not NumPy NaN or integer sentinels.
