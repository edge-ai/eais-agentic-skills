# Device Manager API — Endpoint Index

> Compact index of `ms2-openapi.json` (OpenAPI develop, 85 operations). The full spec is **too large to read in one pass** — use this index to find the operation, then grep the JSON for its `operationId` to pull the exact request/response schema.

**Server base path:** `/ms2` — prefix every path below with it (e.g. `/ms2/device/gpg`).

Reboot, clock/NTP, network/IP, accounts, tokens, GPG keys, licensing, system stack.

## How to get the full schema for one endpoint

```bash
# Find the operation block (request body, params, responses) by operationId:
grep -n '"<operationId>"' ms2-openapi.json
```

Or load the spec into a JSON tool and navigate to the path. **Do not read the whole spec file** — it will be truncated.

## Endpoints by tag

### Device

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/device/backups` | List Backup Files | `list_backups_device_backups_get` | — | — |
| GET | `/device/backups/full/{filename}` | Download Specified Full Backup File | `download_full_backup_device_backups_full__filename__get` | — | `filename` |
| POST | `/device/backups/full/{filename}` | Upload Full Backup File | `upload_full_backup_device_backups_full__filename__post` | body | — |
| GET | `/device/backups/user/{filename}` | Download Specified User Backup File | `download_user_backup_device_backups_user__filename__get` | — | `filename` |
| DELETE | `/device/backups/{kind}/{filename}` | Delete Specified Backup File | `delete_backup_file_device_backups__kind___filename__delete` | — | `kind`, `filename` |
| GET | `/device/connectivity` | Check device connectivity status | `check_device_status_device_connectivity_get` | — | — |
| GET | `/device/dashboards` | Get dashboards | `get_dashboards_device_dashboards_get` | — | — |
| GET | `/device/global/info` | Get device information | `get_device_info_device_global_info_get` | — | — |
| GET | `/device/global/language` | Get device global language | `get_global_language_device_global_language_get` | — | — |
| PUT | `/device/global/language` | Set device global language | `set_global_language_device_global_language_put` | body | — |
| GET | `/device/global/log-level` | Get device global log level | `get_global_log_level_device_global_log_level_get` | — | — |
| PUT | `/device/global/log-level` | Set device global log level | `set_global_log_level_device_global_log_level_put` | body | — |
| GET | `/device/gpg` | Download Device GPG Public Key | `download_gpg_public_key_device_gpg_get` | — | — |
| GET | `/device/license` | Get license information | `get_device_license_device_license_get` | — | — |
| GET | `/device/license/expired` | Check if license is expired | `check_license_expired_device_license_expired_get` | — | — |
| POST | `/device/license/sync` | Synchronize license | `sync_license_device_license_sync_post` | — | — |
| POST | `/device/license/upload` | Upload license | `upload_license_device_license_upload_post` | body | — |
| GET | `/device/ms2/log-level` | Get MS2 log level | `get_ms2_log_level_device_ms2_log_level_get` | — | — |
| PUT | `/device/ms2/log-level` | Set MS2 log level | `set_ms2_log_level_device_ms2_log_level_put` | body | — |
| GET | `/device/stack/info/{version_name}` | Get stack version info | `get_stack_version_info_device_stack_info__version_name__get` | — | `version_name` |
| GET | `/device/stack/mode` | Get current stack mode | `get_stack_mode_device_stack_mode_get` | — | — |
| GET | `/device/stack/status` | Get stack status | `get_stack_mode_device_stack_status_get` | — | — |
| GET | `/device/stack/version` | Get current stack version | `get_stack_version_device_stack_version_get` | — | — |

### Users

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/tokens` | Read All Token Information | `read_all_tokens_tokens_get` | — | — |
| POST | `/tokens` | Create New Token | `create_token_tokens_post` | body | — |
| DELETE | `/tokens/{token_name}` | Delete Specified User | `delete_token_tokens__token_name__delete` | — | `token_name` |
| GET | `/tokens/{token_name}` | Read Specified Token's Information | `read_token_tokens__token_name__get` | — | `token_name` |
| PUT | `/tokens/{token_name}` | Update Token information | `update_token_tokens__token_name__put` | body | `token_name` |
| GET | `/users` | Read All User Information | `read_all_users_users_get` | — | — |
| DELETE | `/users/{username}` | Delete Specified User | `delete_user_users__username__delete` | — | `username` |
| GET | `/users/{username}` | Read Specified User's Information | `read_user_users__username__get` | — | `username` |
| POST | `/users/{username}` | Create New User | `create_user_users__username__post` | body | `username` |
| PUT | `/users/{username}` | Update User information | `update_user_users__username__put` | body | `username` |

### Support

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/remote/status` | Check remote support service status | `check_ngrok_process_running_remote_status_get` | — | — |
| DELETE | `/remote/token` | Remove remote support authentication credentials | `delete_authtoken_remote_token_delete` | — | — |
| GET | `/remote/token` | Check remote support authentication status | `get_authtoken_status_remote_token_get` | — | — |
| POST | `/remote/token` | Register remote support authentication credentials | `set_authtoken_remote_token_post` | body | — |
| DELETE | `/remote/tunnel` | Deactivate remote support tunnels | `delete_tunnel_remote_tunnel_delete` | — | — |
| GET | `/remote/tunnel` | Check remote support tunnel status | `get_tunnel_status_remote_tunnel_get` | — | — |
| POST | `/remote/tunnel` | Activate remote support tunnels | `set_tunnel_remote_tunnel_post` | — | — |

### Time

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/time` | Get Current System Time | `get_time_time_get` | — | — |
| POST | `/time` | Set System Time | `set_time_time_post` | body | — |
| GET | `/time/ntp` | Get Network Time Syncronization Status | `get_ntp_status_time_ntp_get` | — | — |
| POST | `/time/ntp` | Control Network Time Syncronization | `set_ntp_time_ntp_post` | body | — |
| GET | `/time/timezone` | Get Current Device Time Zone | `get_timezone_time_timezone_get` | — | — |
| POST | `/time/timezone` | Change Device Time Zone | `set_timezone_time_timezone_post` | body | — |
| GET | `/time/timezone/list` | Get List of Configurable Time Zones | `get_timezone_list_time_timezone_list_get` | — | — |

### Network

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/network/connection` | List the Connection Settings | `get_connection_status_network_connection_get` | — | — |
| POST | `/network/connection` | Add New Connection | `add_connection_network_connection_post` | body | — |
| DELETE | `/network/connection/{name}` | Delete Network Connection Settings | `delete_connection_network_connection__name__delete` | — | `name` |
| GET | `/network/connection/{name}` | Show Detailed Connection Information | `show_connection_network_connection__name__get` | — | `name` |
| POST | `/network/connection/{name}` | Activate or Deactivate Connection | `toggle_connection_network_connection__name__post` | body | `name` |
| PUT | `/network/connection/{name}` | Modify Connection settings | `update_connection_network_connection__name__put` | body | `name` |
| GET | `/network/device` | List the Network Devices | `get_device_status_network_device_get` | — | — |
| GET | `/network/device/{name}` | Show Detailed Device Information | `show_device_network_device__name__get` | — | `name` |
| POST | `/network/device/{name}` | Activate or Deactivate Device | `toggle_device_network_device__name__post` | body | `name` |
| GET | `/network/general` | Get the Overall Network Status | `get_general_info_network_general_get` | — | — |
| GET | `/network/general/hostname` | Get the Device Hostname | `get_hostname_network_general_hostname_get` | — | — |
| GET | `/network/modem/{name}` | Get Modem Information | `get_modem_info_network_modem__name__get` | — | `name` |
| GET | `/network/radio` | Get Wireless Device Statuses | `get_wireless_info_network_radio_get` | — | — |
| POST | `/network/radio` | Toggle All Wireless Device Enabled Settings | `switch_wireless_network_radio_post` | body | — |
| GET | `/network/radio/wifi` | Get Wi-Fi Enabled Settings | `get_wifi_enabled_network_radio_wifi_get` | — | — |
| POST | `/network/radio/wifi` | Toggle Wi-Fi Enable Settings | `toggle_wifi_enabled_network_radio_wifi_post` | body | — |
| GET | `/network/radio/wwan` | Get WWAN Enabled Settings | `get_wwan_enabled_network_radio_wwan_get` | — | — |
| POST | `/network/radio/wwan` | Toggle WWAN Enable Settings | `toggle_wwan_enabled_network_radio_wwan_post` | body | — |

### System

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/health` | Health Check | `health_health_get` | — | — |
| GET | `/session-status` | Check session status | `session_status_session_status_get` | — | — |
| GET | `/system/poweroff` | Check for Device Shutdown Capability | `can_power_off_system_poweroff_get` | — | — |
| POST | `/system/poweroff` | Shutdown Device | `power_off_system_poweroff_post` | — | — |
| GET | `/system/reboot` | Check for Device Rebootability | `can_reboot_system_reboot_get` | — | — |
| POST | `/system/reboot` | Reboot Device | `reboot_system_reboot_post` | — | — |

### Metrics

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/metrics` | Get Prometheus metrics | `get_metrics_metrics_get` | — | — |
| POST | `/metrics/update` | Update Prometheus metrics | `update_metrics_endpoint_metrics_update_post` | — | — |

### Access

| Method | Path | Summary | operationId | Body? | Required params |
|--------|------|---------|-------------|-------|-----------------|
| GET | `/access/dns` | Get all DNS access providers | `get_dns_provider_access_dns_get` | — | — |
| GET | `/access/dns/providers` | Check DNS providers availability | `check_all_dns_providers_availability_access_dns_providers_get` | — | — |
| DELETE | `/access/dns/{provider_identifier}` | Delete DNS access provider | `delete_dns_provider_access_dns__provider_identifier__delete` | — | `provider_identifier` |
| PUT | `/access/dns/{provider_identifier}` | Update DNS access provider configuration | `update_dns_provider_access_dns__provider_identifier__put` | body | `provider_identifier` |
| GET | `/access/dns/{provider}` | Get specific DNS access provider status | `get_dns_provider_by_type_access_dns__provider__get` | — | `provider` |
| POST | `/access/dns/{provider}` | Create a new DNS access provider | `add_dns_provider_access_dns__provider__post` | body | `provider` |
| GET | `/access/remote` | Get all remote access providers | `get_remote_provider_access_remote_get` | — | — |
| GET | `/access/remote/providers` | Check remote providers availability | `check_all_remote_providers_availability_access_remote_providers_get` | — | — |
| DELETE | `/access/remote/{provider_identifier}` | Delete remote access provider | `delete_remote_provider_access_remote__provider_identifier__delete` | — | `provider_identifier` |
| PUT | `/access/remote/{provider_identifier}` | Update remote access provider configuration | `update_remote_provider_access_remote__provider_identifier__put` | body | `provider_identifier` |
| GET | `/access/remote/{provider}` | Get specific remote access provider status | `get_remote_provider_by_type_access_remote__provider__get` | — | `provider` |
| POST | `/access/remote/{provider}` | Create a new remote access provider | `add_remote_provider_access_remote__provider__post` | body | `provider` |
