# CLI AI Registry Documentation

This document describes all Windows Registry keys and values used by CLI AI.

## Registry Files

| File | Purpose |
|------|---------|
| `cli-ai-registry.reg` | Installs all CLI AI registry entries |
| `cli-ai-registry-uninstall.reg` | Removes all CLI AI registry entries |

## How to Use

### Installation

1. **Right-click** `cli-ai-registry.reg`
2. Select **"Merge"** or **"Open"**
3. Click **"Yes"** when prompted by User Account Control
4. Click **"Yes"** to confirm the registry modification
5. Click **"OK"** when the operation completes

**OR** use command line:

```cmd
reg import cli-ai-registry.reg
```

### Uninstallation

1. **Right-click** `cli-ai-registry-uninstall.reg`
2. Select **"Merge"** or **"Open"**
3. Follow the prompts to remove registry entries

**OR** use command line:

```cmd
reg import cli-ai-registry-uninstall.reg
```

## Registry Structure

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI

**Root key for all CLI AI settings (machine-wide).**

#### Main Keys

| Value Name | Type | Description | Example |
|------------|------|-------------|---------|
| `DisplayName` | String | Application display name | "CLI AI" |
| `Version` | String | Current version | "0.1.0" |
| `Publisher` | String | Application publisher | "CLI AI Contributors" |
| `InstallLocation` | String | Installation directory path | "C:\Users\usuario\Business\CLI_A1_GHR\CLI-main" |
| `InstallDate` | String | Installation date (YYYYMMDD) | "20251229" |
| `HelpLink` | String | URL to help documentation | GitHub repository URL |
| `URLInfoAbout` | String | URL to application info | GitHub repository URL |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Settings

**Application-specific configuration settings.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `DataDirectory` | String | Path to data storage | "{InstallLocation}\data" |
| `ConfigDirectory` | String | Path to configuration files | "{InstallLocation}\configs" |
| `LogDirectory` | String | Path to log files | "{InstallLocation}\logs" |
| `PromptDirectory` | String | Path to agent prompts | "{InstallLocation}\prompts" |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Database

**Database and knowledge base configuration.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `KnowledgeBasePath` | String | SQLite database file path | "{DataDirectory}\kb.db" |
| `HierarchicalMemoryPath` | String | H-Net memory storage path | "{DataDirectory}\hier_mem" |
| `JournalMode` | String | SQLite journal mode | "WAL" |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Server

**Server and network configuration.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `BusServerPort` | DWORD | Bus server port number | 7088 (0x00001BB8) |
| `BusServerHost` | String | Bus server host address | "127.0.0.1" |
| `RedisURL` | String | Redis connection URL | "redis://localhost:6379/0" |
| `AgentPortStart` | DWORD | Starting port for agents | 7001 (0x00001B59) |
| `AgentPortEnd` | DWORD | Ending port for agents | 7009 (0x00001B61) |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Models

**AI model configuration.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `RouterBaseURL` | String | Router model API endpoint | "http://localhost:11434/v1" |
| `RouterModel` | String | Router model name | "qwen2:latest" |
| `QwenBaseURL` | String | Qwen model API endpoint | "http://localhost:11434/v1" |
| `QwenModel` | String | Qwen model name | "qwen2:latest" |
| `DeepSeekBaseURL` | String | DeepSeek model API endpoint | "http://localhost:11434/v1" |
| `DeepSeekModel` | String | DeepSeek model name | "codegemma:latest" |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Features

**Optional feature flags.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `UseOpenVINO` | DWORD | Enable OpenVINO optimization | 0 (disabled) |
| `UseFAISS` | DWORD | Enable FAISS vector search | 0 (disabled) |
| `EnableObservability` | DWORD | Enable observability features | 0 (disabled) |
| `EnableTokenCounter` | DWORD | Enable token counting | 0 (disabled) |

**DWORD Values:**
- `0` = Disabled/False
- `1` = Enabled/True

### HKEY_CURRENT_USER\Software\CLI-AI

**User-specific settings (per-user configuration).**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `FirstRun` | DWORD | First run indicator | 1 (true) |
| `LastUsed` | String | Last usage timestamp | "" (empty) |
| `UserDataPath` | String | User-specific data path | "%APPDATA%\CLI-AI" |

### HKEY_CURRENT_USER\Software\CLI-AI\Preferences

**User preferences.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `EnableLogging` | DWORD | Enable application logging | 1 (enabled) |
| `LogLevel` | String | Logging level | "INFO" |
| `AutoUpdate` | DWORD | Enable automatic updates | 0 (disabled) |
| `TelemetryEnabled` | DWORD | Enable telemetry | 0 (disabled) |

**Log Levels:**
- `DEBUG` - Detailed debug information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors only

### HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment

**System environment variables.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `CLI_AI_HOME` | String | CLI AI installation path | "{InstallLocation}" |
| `CLI_AI_VERSION` | String | Installed version | "0.1.0" |

### HKEY_CLASSES_ROOT\.cliai

**File association for .cliai files.**

| Value | Description |
|-------|-------------|
| Default | Links to CLI.AI.Workflow handler |
| Content Type | MIME type for .cliai files |

### HKEY_CLASSES_ROOT\CLI.AI.Workflow

**File type handler for CLI AI workflow files.**

Subkeys:
- `DefaultIcon` - Icon for .cliai files
- `shell\open\command` - Command to open .cliai files

### HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CLI-AI

**Uninstall information (appears in Windows Programs and Features).**

| Value Name | Type | Description |
|------------|------|-------------|
| `DisplayName` | String | Name shown in Programs and Features |
| `DisplayVersion` | String | Version shown in Programs and Features |
| `Publisher` | String | Publisher name |
| `InstallLocation` | String | Installation directory |
| `DisplayIcon` | String | Icon file path |
| `UninstallString` | String | Command to uninstall |
| `URLInfoAbout` | String | Application website URL |
| `HelpLink` | String | Help/support URL |
| `NoModify` | DWORD | Disable "Modify" button (1=disabled) |
| `NoRepair` | DWORD | Disable "Repair" button (1=disabled) |
| `EstimatedSize` | DWORD | Estimated size in KB |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Capabilities

**Application capabilities for Windows 10/11.**

| Subkey | Purpose |
|--------|---------|
| `FileAssociations` | Maps file extensions to handlers |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Performance

**Performance tuning settings.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `MaxWorkers` | DWORD | Maximum worker threads | 4 |
| `ChunkSize` | DWORD | Text chunk size (tokens) | 800 (0x320) |
| `ChunkOverlap` | DWORD | Overlap between chunks | 80 (0x50) |
| `MaxTokenBudget` | DWORD | Maximum token budget | 8192 (0x2000) |

### HKEY_LOCAL_MACHINE\SOFTWARE\CLI-AI\Security

**Security settings.**

| Value Name | Type | Description | Default Value |
|------------|------|-------------|---------------|
| `RequireBusToken` | DWORD | Require authentication token | 1 (required) |
| `ValidateCertificates` | DWORD | Validate SSL certificates | 1 (validate) |
| `AllowExternalConnections` | DWORD | Allow external connections | 0 (deny) |

## Customization

### Modifying Registry Values

You can modify registry values using:

1. **Registry Editor (regedit.exe)**
   - Press `Win+R`, type `regedit`, press Enter
   - Navigate to the desired key
   - Double-click the value to edit

2. **Command Line**
   ```cmd
   reg add "HKLM\SOFTWARE\CLI-AI\Settings" /v LogDirectory /t REG_SZ /d "C:\Logs\CLI-AI" /f
   ```

3. **PowerShell**
   ```powershell
   Set-ItemProperty -Path "HKLM:\SOFTWARE\CLI-AI\Settings" -Name "LogDirectory" -Value "C:\Logs\CLI-AI"
   ```

### Common Customizations

#### Change Installation Path

```cmd
reg add "HKLM\SOFTWARE\CLI-AI" /v InstallLocation /t REG_SZ /d "C:\Your\Custom\Path" /f
```

#### Enable OpenVINO

```cmd
reg add "HKLM\SOFTWARE\CLI-AI\Features" /v UseOpenVINO /t REG_DWORD /d 1 /f
```

#### Change Bus Server Port

```cmd
reg add "HKLM\SOFTWARE\CLI-AI\Server" /v BusServerPort /t REG_DWORD /d 8088 /f
```

#### Change Log Level

```cmd
reg add "HKCU\Software\CLI-AI\Preferences" /v LogLevel /t REG_SZ /d "DEBUG" /f
```

## Registry Value Types

| Type | Description | Example |
|------|-------------|---------|
| `REG_SZ` | String value | "Hello World" |
| `REG_DWORD` | 32-bit integer | 0x00000001 (1) |
| `REG_MULTI_SZ` | Multi-string value | Multiple lines |
| `REG_EXPAND_SZ` | Expandable string | "%APPDATA%\CLI-AI" |

## Security Considerations

### User Account Control (UAC)

- Modifying `HKEY_LOCAL_MACHINE` requires **Administrator privileges**
- Modifying `HKEY_CURRENT_USER` does **not** require Administrator privileges

### Registry Backup

Before making changes, backup the registry:

```cmd
reg export HKLM\SOFTWARE\CLI-AI cli-ai-backup.reg
```

To restore:

```cmd
reg import cli-ai-backup.reg
```

### Recommended Practices

1. **Always backup** before modifying registry
2. **Use .reg files** for batch modifications
3. **Test changes** in a development environment first
4. **Document** any custom modifications
5. **Restart applications** after registry changes

## Troubleshooting

### Registry Changes Not Taking Effect

1. **Restart the application** - Most applications read registry on startup
2. **Restart Windows** - Some system-level changes require reboot
3. **Check permissions** - Ensure you have proper rights to modify the registry
4. **Verify the path** - Ensure the registry path is correct

### Permission Denied Errors

Run the command prompt or PowerShell **as Administrator**:

1. Right-click **Command Prompt** or **PowerShell**
2. Select **"Run as administrator"**
3. Re-run the registry modification command

### Registry File Won't Import

1. Check file encoding (should be UTF-16 LE or ANSI)
2. Verify the first line is: `Windows Registry Editor Version 5.00`
3. Check for syntax errors in the .reg file
4. Ensure backslashes are properly escaped (`\\` instead of `\`)

## Environment Variables Access

After setting system environment variables, they can be accessed:

### Command Prompt
```cmd
echo %CLI_AI_HOME%
echo %CLI_AI_VERSION%
```

### PowerShell
```powershell
$env:CLI_AI_HOME
$env:CLI_AI_VERSION
```

### Python
```python
import os
cli_home = os.environ.get('CLI_AI_HOME')
cli_version = os.environ.get('CLI_AI_VERSION')
```

## Additional Resources

- [Microsoft Registry Documentation](https://docs.microsoft.com/windows/win32/sysinfo/registry)
- [REG Command Reference](https://docs.microsoft.com/windows-server/administration/windows-commands/reg)
- [PowerShell Registry Provider](https://docs.microsoft.com/powershell/module/microsoft.powershell.src/core/about/about_registry)

---

**Last Updated:** 2025-12-29
**CLI AI Version:** 0.1.0
