# KaalSec Plugins

This directory contains YAML plugin files that define tool knowledge bases for KaalSec.

## Plugin Format

Each plugin is a YAML file with the following structure:

```yaml
tool: <tool_name>
description: "<tool description>"

categories:
  - name: "<category_name>"
    examples:
      - cmd: "<example_command>"
        desc: "<command_description>"

failure_cases:
  - "<common_error_message>"

docs: "<link_to_official_docs>"
```

## Adding New Plugins

1. Create a new YAML file named `<tool>.yml` in this directory
2. Follow the format above
3. KaalSec will automatically load it on next run

## Example Tools

- `nmap.yml` - Network mapper
- `nikto.yml` - Web server scanner
- `gobuster.yml` - Directory/file brute-forcer

