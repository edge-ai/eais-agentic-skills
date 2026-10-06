# AIP Developer Guide — manifest.json Schema

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

### 2.3. `manifest.json` file structure

Key fields (example semantics):

- `unique_id`: Vendor-assigned AIP ID (e.g. `AIPV1DKE0001`)
- `name`, `version`, `hardware_target`: e.g. `["EX3", "EX5"]`
- `description`: A brief summary of the AIP package's purpose or functionality
- `vendor`, `website`: Contains details about the vendor or provider of the AIP package
- `license`: Specifies the license type under which the AIP package is distributed
- `maximum_input_streams`: Defines the maximum number of input streams the AIP can handle simultaneously
- `user_manual`: A URL link to the user manual or documentation for the AIP
- `primary_processor`: Model definition block
- `secondary_processors`: Optional list (same schema as primary)
- `tracker_engine`: Optional; defines tracker library usage. Can be `null` if no tracker is used.
- `analytic_plugins`: Controls DeepStream nvdsanalytics feature enablement & custom handling

The `primary_processor` contains details about the primary AI processing model used in the pipeline:

- `name`: The name of the primary AI processor model (e.g. "AIPV1DKE0001_Primary_Detector")
- `description`: Describes the function of the primary processor (e.g. "Detection of faces")
- `model`: Indicates the type of model architecture used (e.g. "DetectNet_v2")
- `classes`: Lists the object classes that the model detects (e.g. "face"). Needs to match your model labels
- `config_plan`: Points to the configuration file used for this processor (e.g. "config_infer_primary_detector_xxxx.txt")
- `batch_size`: Defines the max batch size of the model

The `tracker_engine` contains details about the tracking engine used in the AIP (optional — may be `null`):

- `name`: The name of the tracking engine. Currently only Nvidia default trackers are supported
- `description`: A brief explanation of the tracker
- `model`: Indicates the tracking model type
- `lib_path`: The path to the ".so" library file for the tracker engine
- `config_plan`: Specifies the configuration file for the tracker engine
- `tracker_width`: Defines the width resolution for the tracking engine
- `tracker_height`: Defines the height resolution for the tracking engine

`analytic_plugins` structure example:

```json
"analytic_plugins": {
    "ROI": { "custom": false },
    "DIR": { "custom": false },
    "OVC": { "custom": false },
    "LCC": { "custom": true }
}
```

The `analytic_plugins` field is a configuration item that defines which of the four analysis features provided by the NVIDIA DeepStream nvdsanalytics plugin are allowed to be used by the application. For each feature, you can specify whether to use the standard nvdsanalytics feature or implement your own logic for analysis and overlay drawing.

Keys are feature names, and are limited to the following four types. They are not intended to be added or deleted by AIP developers or users. Also, uppercase and lowercase are case-sensitive, and lowercase and mixed notations are invalid:

- **ROI**: ROI Filtering
- **DIR**: Direction Detection
- **OVC**: Overcrowding Detection
- **LCC**: Line Crossing

The feature setting values ​​have the following meanings:

- `custom`: Determines whether the corresponding analytics feature uses the standard processing of nvdsanalytics or the user implements their own processing.
  - `false`: Standard nvdsanalytics processing is performed, including rendering and metadata output, and you can access the results in your application's callback.py script.
  - `true`: Standard nvdsanalytics processing is not performed, and drawing and metadata output are not performed. AIP developers must implement their own processing in callback.py. The user's settings can be accessed via `self.analytics_settings` in the UserCustomCallback class in callback.py.

> ℹ️ **Note**: Line Crossing (LCC) coordinates follow nvdsanalytics spec: two direction points + two virtual line points. When checking the Line Crossing settings, you will see four coordinate values. These values represent two coordinates for the direction, followed by two coordinates for the virtual line. This format follows the specification of NVIDIA's nvdsanalytics plugin. For more details, please refer to the [NVIDIA documentation](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_plugin_gst-nvdsanalytics.html#id3).

