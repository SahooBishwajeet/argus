# Argus

A tool to monitor WiFi uptime and bandwidth over time.

## Installation

```bash
pip install argus-wifi
```

## Usage

### Regular Mode

To start monitoring with default settings:

```bash
argus monitor
```

Options:

- `--interval`: Time between checks in seconds (default: 300)
- `--duration`: How long to monitor in hours (default: 24)
- `--log`: Path to the CSV log file (default: argus.csv)
- `--output`: Path to save the graph (default: argus_report.png)
- `--analyze-only`: Only analyze existing data without monitoring

Example with custom settings:

```bash
argus monitor --interval 600 --duration 48 --log my_log.csv --output my_report.png
```

### Daemon Mode

Run Argus in the background:

```bash
# Start the daemon
argus start --interval 300 --duration 24

# Check status and configuration
argus status

# Stop the daemon
argus stop
```

When running in daemon mode, all files (logs, data, and reports) are stored in `~/.argus/` directory.

## Features

- Monitor WiFi connectivity over time
- Measure download and upload speeds
- Track ping latency
- Generate visual reports with matplotlib
- Analyze historical data
- Run in background (daemon mode)
- CLI commands for process management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
