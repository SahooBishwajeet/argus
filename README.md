# Argus

A tool to monitor WiFi uptime and bandwidth over time.

## Installation

```bash
pip install argus
```

## Usage

To start monitoring with default settings:

```bash
argus
```

Options:

- `--interval`: Time between checks in seconds (default: 300)
- `--duration`: How long to monitor in hours (default: 24)
- `--log`: Path to the CSV log file (default: argus.csv)
- `--output`: Path to save the graph (default: argus_report.png)
- `--analyze-only`: Only analyze existing data without monitoring

Example with custom settings:

```bash
argus --interval 600 --duration 48 --log my_log.csv --output my_report.png
```

To only analyze existing data:

```bash
argus --analyze-only --log my_log.csv
```

## Features

- Monitor WiFi connectivity over time
- Measure download and upload speeds
- Track ping latency
- Generate visual reports with matplotlib
- Analyze historical data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
