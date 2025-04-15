#!/usr/bin/env python
"""Command-line interface for Argus."""

import argparse
from argus.core import WiFiMonitor
from argus.daemon import ArgusDaemon
import json

def main():
    """Run the Argus WiFi monitor CLI."""
    parser = argparse.ArgumentParser(description="WiFi Uptime and Bandwidth Monitor")

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Run WiFi monitoring')
    monitor_parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between checks in seconds (default: 300)",
    )
    monitor_parser.add_argument(
        "--duration",
        type=float,
        default=24,
        help="Duration of monitoring in hours (default: 24)",
    )
    monitor_parser.add_argument(
        "--log",
        type=str,
        default="argus.csv",
        help="Path to log file (default: argus.csv)",
    )
    monitor_parser.add_argument(
        "--output",
        type=str,
        default="argus_report.png",
        help="Path to output file for plots (default: argus_report.png)",
    )
    monitor_parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze existing data without running monitoring",
    )
    monitor_parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run in daemon mode",
    )

    # Start command
    start_parser = subparsers.add_parser('start', help='Start Argus daemon')
    start_parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval between checks in seconds (default: 300)",
    )
    start_parser.add_argument(
        "--duration",
        type=float,
        default=24,
        help="Duration of monitoring in hours (default: 24)",
    )
    start_parser.add_argument(
        "--log",
        type=str,
        default="argus.csv",
        help="Path to log file (default: argus.csv)",
    )
    start_parser.add_argument(
        "--output",
        type=str,
        default="argus_report.png",
        help="Path to output file for plots (default: argus_report.png)",
    )

    # Stop command
    subparsers.add_parser('stop', help='Stop Argus daemon')

    # Status command
    subparsers.add_parser('status', help='Get Argus daemon status')

    args = parser.parse_args()

    if args.command == 'monitor' or args.command is None:
        if args.daemon:
            daemon = ArgusDaemon()
            config = {
                'interval': args.interval,
                'duration': args.duration,
                'log': args.log,
                'output': args.output
            }
            if daemon.start(config):
                print("Argus started in daemon mode.")
                print(f"Logs are available at: {daemon.log_file}")
                print(f"Status: argus status")
            else:
                print("Failed to start Argus daemon.")
        else:
            monitor = WiFiMonitor(
                check_interval=args.interval,
                log_file=args.log,
                output_file=args.output
            )
            if args.analyze_only:
                monitor.analyze_results(from_file=True)
            else:
                monitor.run_monitor(duration_hours=args.duration)

    elif args.command == 'start':
        daemon = ArgusDaemon()
        config = {
            'interval': args.interval,
            'duration': args.duration,
            'log': args.log,
            'output': args.output
        }
        if daemon.start(config):
            print("Argus started in daemon mode.")
            print(f"Logs are available at: {daemon.log_file}")
            print(f"Status: argus status")
        else:
            print("Failed to start Argus daemon.")

    elif args.command == 'stop':
        daemon = ArgusDaemon()
        if daemon.stop():
            print("Argus daemon stopped.")
        else:
            print("No running Argus daemon found.")

    elif args.command == 'status':
        daemon = ArgusDaemon()
        status = daemon.status()
        if status['status'] == 'running':
            print("Argus is running.")
            config = status.get('config', {})
            print(f"Process ID: {status.get('pid')}")
            print(f"Configuration:")
            print(f"  Interval: {config.get('interval')} seconds")
            print(f"  Duration: {config.get('duration')} hours")
            print(f"  Log file: {config.get('log')}")
            print(f"  Output file: {config.get('output')}")
        else:
            print("Argus is not running.")

if __name__ == "__main__":
    main()
