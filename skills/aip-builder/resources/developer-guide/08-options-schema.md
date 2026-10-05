# AIP Developer Guide — options.json Schema & Limitations

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

### 3.9. Option Settings

Option settings feature allows AIP developers to provide user-configurable settings for each pipeline. This feature enables users to manage AIP settings flexibly.

The option settings are defined in an `options.json` file located in the AIP's root folder. In this file, each option's name, type, default value, and numeric limits (both upper and lower bounds) can be specified. After creating a pipeline, users can view and modify the defined option settings via the system's HTTP API. However, changes to the settings will not take effect while the pipeline is running; they will only be applied the next time the pipeline is started after being stopped.

Option settings can be accessed via the `self.options` class variable in the CustomCallback class within `callback.py`.

> ℹ️ **Note**: This option settings feature is in its alpha version.

#### Options.json

The `options.json` file is used by AIP (AI Processor) developers to define option settings. This configuration file allows developers to specify the type, default value, and valid value ranges for each option.

```json
{
    "<option_name>": {
        "value_type": "<type>",
        "default": <default_value>,
        "min_value": <min_value>,  // Optional, valid when value_type is "float" or "int"
        "max_value": <max_value>,  // Optional, valid when value_type is "float" or "int"
        "allowed_values": <allowed_values>,  // Optional, valid when value_type is "literal"
        "description": <description>  // Optional, provides additional information about the option
    },
    ...
}
```

**Parameters:**

- `value_type`: Specifies the type of the option value. It can be one of the following:
  - `"float"`: Floating point number
  - `"int"`: Integer
  - `"bool"`: Boolean (true or false)
  - `"str"`: String
  - `"literal"`: A string value from a restricted list
- `default`: The default value of the option. It should be set according to the value_type.
- `min_value`: The minimum value for the option when value_type is float or int. This is optional, and if value_type is not float or int, it is ignored. If min_value is set, it can be omitted when value_type is not float or int.
- `max_value`: The maximum value for the option when value_type is float or int. This is optional, and if value_type is not float or int, it is ignored. If max_value is set, it can be omitted when value_type is not float or int.
- `allowed_values`: A list of allowed string values for the option when value_type is literal. This is optional, and if value_type is not literal, it is ignored. If allowed_values is set, it can be omitted when value_type is not literal.
- `description`: Additional information about the option. This field is optional and may be omitted. It is provided for future support of setting options through a Web UI, in addition to the HTTP API.

**Example of options.json file:**

```json
{
  "hour": {
    "value_type": "int",
    "default": 12,
    "min_value": 0,
    "max_value": 23
  },
  "meal": {
    "value_type": "literal",
    "default": "beef",
    "allowed_values": ["beef", "chicken"]
  }
}
```

#### HTTP API

This API for users provides endpoints to retrieve and update callback option settings related to the pipeline. These endpoints are used to manage options for the AIP (AI Processor) configuration.

##### GET /pipeline/{uuid}/options

This endpoint retrieves the callback options for the pipeline identified by the specified UUID.

_URL Path Parameters:_

- `uuid`: The unique identifier for the pipeline.

_Response Body:_ On success, the callback options are returned in the following format:

```json
{
  "hour": 12,
  "meal": "beef"
}
```

##### PUT /pipeline/{uuid}/options

This endpoint updates the callback options for the pipeline identified by the specified UUID.

_URL Path Parameters:_

- `uuid`: The unique identifier for the pipeline.

_Request Body:_ The options to update should be provided in the following format:

```json
{
  "options": {
    "hour": 19,
    "meal": "chicken"
  }
}
```

_Response Body:_ The callback options are returned in the following format:

```json
{
  "hour": 19,
  "meal": "chicken"
}
```

### 3.10. Current limitations

- Cannot access raw frame pixels in callback
- Cannot mutate metadata for downstream pipeline stages

