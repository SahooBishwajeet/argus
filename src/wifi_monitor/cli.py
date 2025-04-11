"""Command-line interface for argus."""

import argparse
from .core import WiFiMonitor


def main():
    """Run the Argus WiFi monitor command-line interface."""
    parser = argparse.ArgumentParser(
        description="Argus: WiFi Uptime and Bandwidth Monitor"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between checks in seconds (default: 300)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=24,
        help="Duration of monitoring in hours (default: 24)",
    )
    parser.add_argument(
        "--log",
        type=str,
        default="argus.csv",
        help="Path to log file (default: argus.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="argus_report.png",
        help="Path to output file for plots (default: argus_report.png)",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze existing data without running monitoring",
    )

    args = parser.parse_args()
    monitor = WiFiMonitor(
        check_interval=args.interval, log_file=args.log, output_file=args.output
    )

    if args.analyze_only:
        monitor.analyze_results(from_file=True)
    else:
        monitor.run_monitor(duration_hours=args.duration)


if __name__ == "__main__":
    main()
