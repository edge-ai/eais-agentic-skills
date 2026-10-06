# AIP Developer Guide — Packaging & Distribution

> Part of the EdgeAI Station AIP Developer Guide. See [`INDEX.md`](./INDEX.md) for the full topic map. Section numbers (e.g. §3.5) are preserved from the original guide.

## 5. AIP distribution

### 5.1. Packaging the application

You can automate packaging with a Jupyter Notebook, a custom script, or EAIS Tools
(see the [CLI reference](./12-eais-tools.md)).

Build the AIP distribution package:

```bash
eais-tools aip build --uuid AIP_UUID
```

Export the AIP distribution as a tar.gz archive for the AIP store:

```bash
eais-tools aip export --uuid AIP_UUID
```

> ⚠️ **Warning**: No automatic package shape validator currently (EDGEMATRIX performs review for store distribution).

Be sure to only include the `engine` and `configuration` files of your model and **do not include** the source file of your model nor your working files.

#### 5.1.1. Using the `.include` file

The `.include` file should be placed at the root of your AIP project. It allows you to specify additional files and directories to include in your AIP package beyond the default set. This is particularly useful when your AIP requires custom resources, scripts, or data files.

??? note "Custom include file"
    The default file name is `.include`, but you can use a different name by specifying it with the `--include-file` or `-I` option when building:
    ```bash
    eais-tools aip build --uuid AIP_UUID --include-file .custom-include
    ```

??? tip "Show hidden files in Jupyter"
    Files starting with a dot (like `.include`) are hidden by default in Jupyter. To see the `.include` file in the Jupyter file browser, enable "Show Hidden Files" from the `View` menu.
    

##### Comments and Blank Lines

- Lines starting with `#` are treated as comments and ignored
- Blank lines are ignored
- Inline comments are supported using `#` after the pattern

###### Example

```bash
# This is a full-line comment
configs/extra.conf # This is an inline comment
```

##### **Path Types**

###### Relative Paths (recommended for portability)

- Resolved from the AIP project root directory
- Example: `scripts/setup.sh`

###### Absolute Paths

- Starting with `/` are expanded on the filesystem
- Example: `/opt/custom/library.so`

##### Pattern Matching

| Pattern | Description | Example |
|---------|-------------|---------|
| `*` | Matches any characters within a single directory level | `scripts/*.sh` matches all `.sh` files in `scripts/` |
| `?` | Matches a single character | `config?.txt` matches `config1.txt`, `config2.txt` |
| `**` | Recursive wildcard (matches directories recursively) | `logs/**/*.log` matches all `.log` files under `logs/` |

##### Directory Inclusion

All three notations below are equivalent and include all files recursively:
```
resources      # Directory name without trailing slash
resources/     # Directory name with trailing slash
resources/**   # Explicit recursive glob notation
```

##### Best Practices

- ✅ **Use relative paths** instead of absolute paths for portability across environments
- ✅ **Add comments** to document why specific files are included
- ✅ **Test your patterns** by running [`eais-tools aip build`](./12-eais-tools.md) and reviewing the build logs
- ✅ **Use specific patterns** rather than overly broad wildcards to avoid including unnecessary files
- ❌ **Avoid including source files** (`.etlt`, `.onnx`, working files) that should not be distributed

??? info "Examples"
    ```bash
    # Include a single configuration file
    configs/extra.conf

    # Include a file with inline documentation
    scripts/setup.sh # Setup script for initialization

    # Include all shell scripts in scripts/ directory (non-recursive)
    scripts/*.sh

    # Include all Python files recursively under src/
    src/**/*.py

    # Include entire resources directory (all three notations work)
    resources
    # or
    resources/
    # or
    resources/**

    # Include multiple data formats
    data/*.json
    data/*.csv
    data/*.xml
    ```

### 5.2. Performance testing and validation process

Use the Grafana dashboard to record FPS, and validate performance on each target
device (EX3, EX5, etc.) before distributing the package.

### 5.3. Edgematrix Application store

Once your application is approved, it will be stored on our secured Cloud platform for distribution. The copy of your application will be encrypted in a way that only the target device it has been built for will be able to load it.
Moreover the AIP needs a license on the EdgeAI station to be executed by the runtime.
