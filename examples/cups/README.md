# cups-admin

A command-line toolkit for managing CUPS (Common UNIX Printing System) printers, queues, and configurations.

## Features

- List, add, and remove printers
- Manage print queues and jobs
- Configure printer options and defaults
- Monitor printer status and errors
- Backup and restore CUPS configurations
- Troubleshoot common printing issues

## Installation

```bash
pip install cups-admin
```

## Quick Start

```bash
# List all printers
cups-admin list

# Check printer status
cups-admin status HP-LaserJet

# Add a new printer
cups-admin add --name "Office-Printer" --uri "ipp://192.168.1.100/ipp/print" --driver "everywhere"

# View print queue
cups-admin queue

# Cancel all jobs for a printer
cups-admin cancel --printer HP-LaserJet --all
```

## Configuration

Configuration is stored in `~/.cups-admin/config.toml`:

```toml
[server]
host = "localhost"
port = 631
use_ssl = true

[defaults]
printer = "HP-LaserJet"
format = "table"
```

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues.

## License

MIT
