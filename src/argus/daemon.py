"""Daemon functionality for Argus WiFi monitor."""

import os
import sys
import json
import signal
import datetime
import logging
from pathlib import Path
import psutil
from .core import WiFiMonitor

class ArgusDaemon:
    def __init__(self):
        self.data_dir = Path.home() / ".argus"
        self.pid_file = self.data_dir / "argus.pid"
        self.status_file = self.data_dir / "status.json"
        self.log_file = self.data_dir / "argus.log"
        self.ensure_dirs()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def ensure_dirs(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_data_path(self, filename):
        if os.path.isabs(filename):
            return filename
        return str(self.data_dir / filename)

    def _redirect_file_descriptors(self):
        # Redirect stdout and stderr to /dev/null
        sys.stdout.flush()
        sys.stderr.flush()
        with open(os.devnull, 'w') as dev_null:
            os.dup2(dev_null.fileno(), sys.stdout.fileno())
            os.dup2(dev_null.fileno(), sys.stderr.fileno())

    def start(self, monitor_args):
        if self.is_running():
            print("Argus is already running.")
            return False

        # Convert relative paths to absolute paths in data directory
        monitor_args['log'] = self.get_data_path(monitor_args['log'])
        monitor_args['output'] = self.get_data_path(monitor_args['output'])

        # First fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as err:
            print(f'Fork failed: {err}')
            sys.exit(1)

        # Decouple from parent environment
        os.chdir('/')
        os.umask(0)
        os.setsid()

        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            print(f'Fork failed: {err}')
            sys.exit(1)

        # Configure logging
        self.setup_logging()

        # Redirect file descriptors
        self._redirect_file_descriptors()

        # Start monitoring
        pid = os.getpid()
        self.write_pid(pid)
        self.update_status("running", monitor_args)

        logging.info("Starting Argus daemon")
        logging.info(f"Configuration: {monitor_args}")

        class DaemonMonitor(WiFiMonitor):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            def run_check(self):
                connection_status = self.check_connection()
                self.total_checks += 1
                if connection_status:
                    self.connected_checks += 1
                    logging.info("WiFi Status: Connected ✓")
                    logging.info("Measuring bandwidth...")
                    download_mbps, upload_mbps, ping_ms = self.measure_bandwidth()
                    if download_mbps is not None:
                        logging.info(f"Download: {download_mbps:.2f} Mbps")
                        logging.info(f"Upload: {upload_mbps:.2f} Mbps")
                        logging.info(f"Ping: {ping_ms:.2f} ms")
                    else:
                        logging.warning("Failed to measure bandwidth.")
                else:
                    logging.warning("WiFi Status: Disconnected ✗")
                    download_mbps, upload_mbps, ping_ms = None, None, None
                self.log_results(connection_status, download_mbps, upload_mbps, ping_ms)

        monitor = DaemonMonitor(
            check_interval=monitor_args.get('interval', 300),
            log_file=monitor_args['log'],
            output_file=monitor_args['output']
        )

        def handle_stop(signum, frame):
            logging.info("Stopping Argus daemon")
            self.update_status("stopped")
            self.remove_pid()
            sys.exit(0)

        signal.signal(signal.SIGTERM, handle_stop)
        monitor.run_monitor(duration_hours=monitor_args.get('duration', 24))
        return True

    def stop(self):
        pid = self.get_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                self.remove_pid()
                self.update_status("stopped")
                return True
            except ProcessLookupError:
                self.remove_pid()
                return False
        return False

    def status(self):
        """Get the current status of Argus monitor."""
        pid = self.get_pid()
        if pid is None:
            return {"status": "not running"}

        try:
            process = psutil.Process(pid)
            if process.is_running() and "argus" in process.name().lower():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except (psutil.NoSuchProcess, FileNotFoundError, json.JSONDecodeError):
            self.remove_pid()
            return {"status": "not running"}

        return {"status": "not running"}

    def is_running(self):
        return self.status()["status"] == "running"

    def write_pid(self, pid):
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))

    def get_pid(self):
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return None

    def remove_pid(self):
        try:
            os.unlink(self.pid_file)
        except FileNotFoundError:
            pass

    def update_status(self, status, args=None):
        status_data = {
            "status": status,
            "last_updated": datetime.datetime.now().isoformat(),
            "pid": self.get_pid()
        }
        if args:
            status_data["config"] = args

        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
