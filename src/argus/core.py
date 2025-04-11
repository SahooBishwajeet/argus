"""Core functionality for Argus WiFi monitoring."""

import time
import datetime
import subprocess
import socket
import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
import json


class WiFiMonitor:
    def __init__(
        self,
        check_interval=300,
        log_file="argus.csv",
        output_file="argus_report.png",
    ):
        self.check_interval = check_interval
        self.log_file = log_file
        self.output_file = output_file
        self.start_time = datetime.datetime.now()
        self.total_checks = 0
        self.connected_checks = 0

        if not os.path.exists(log_file):
            with open(log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "connection_status",
                        "download_mbps",
                        "upload_mbps",
                        "ping_ms",
                    ]
                )

    def check_connection(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except (socket.timeout, socket.error):
            return False

    def measure_bandwidth(self):
        try:
            print("Running speedtest...")
            try:
                import speedtest

                s = speedtest.Speedtest()
                s.get_servers()
                s.get_best_server()
                s.download()
                s.upload()
                results = s.results.dict()
                download_mbps = results["download"] / 1_000_000
                upload_mbps = results["upload"] / 1_000_000
                ping_ms = results["ping"]
                return download_mbps, upload_mbps, ping_ms
            except (ImportError, AttributeError):
                print("Falling back to alternative method...")
                result = subprocess.run(
                    ["python", "-m", "speedtest", "--json"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                data = json.loads(result.stdout)
                download_mbps = data["download"] / 1_000_000
                upload_mbps = data["upload"] / 1_000_000
                ping_ms = data["ping"]
                return download_mbps, upload_mbps, ping_ms
        except Exception as e:
            print(f"Error measuring bandwidth: {e}")
            return None, None, None

    def log_results(self, connection_status, download_mbps, upload_mbps, ping_ms):
        timestamp = datetime.datetime.now()
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    int(connection_status),
                    download_mbps if download_mbps is not None else "",
                    upload_mbps if upload_mbps is not None else "",
                    ping_ms if ping_ms is not None else "",
                ]
            )

    def run_check(self):
        print(
            f"\n=== Check at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
        )
        connection_status = self.check_connection()
        self.total_checks += 1
        if connection_status:
            self.connected_checks += 1
            print("WiFi Status: Connected ✓")
            print("Measuring bandwidth...")
            download_mbps, upload_mbps, ping_ms = self.measure_bandwidth()
            if download_mbps is not None:
                print(f"Download: {download_mbps:.2f} Mbps")
                print(f"Upload: {upload_mbps:.2f} Mbps")
                print(f"Ping: {ping_ms:.2f} ms")
            else:
                print("Failed to measure bandwidth.")
        else:
            print("WiFi Status: Disconnected ✗")
            download_mbps, upload_mbps, ping_ms = None, None, None
        self.log_results(connection_status, download_mbps, upload_mbps, ping_ms)

    def analyze_results(self, from_file=False):
        print("\n" + "=" * 50)
        print("WiFi Monitoring Report")
        print("=" * 50)

        if from_file:
            if not os.path.exists(self.log_file):
                print(f"Error: Log file '{self.log_file}' not found.")
                return
            print(f"Analyzing existing data from '{self.log_file}'")
        else:
            end_time = datetime.datetime.now()
            duration = end_time - self.start_time
            hours = duration.total_seconds() / 3600
            uptime_percentage = (
                (self.connected_checks / self.total_checks) * 100
                if self.total_checks > 0
                else 0
            )

            print(
                f"Monitoring period: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"Total duration: {duration}")
            print(f"Total checks: {self.total_checks}")
            print(f"Connected checks: {self.connected_checks}")
            print(f"Uptime percentage: {uptime_percentage:.2f}%")

        try:
            df = pd.read_csv(self.log_file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            if from_file:
                total_records = len(df)
                connected_records = df["connection_status"].sum()
                uptime_percentage = (
                    (connected_records / total_records) * 100
                    if total_records > 0
                    else 0
                )

                start_time = df["timestamp"].min()
                end_time = df["timestamp"].max()
                duration = end_time - start_time

                print(
                    f"Monitoring period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print(f"Total duration: {duration}")
                print(f"Total records: {total_records}")
                print(f"Connected records: {connected_records}")
                print(f"Uptime percentage: {uptime_percentage:.2f}%")

            bandwidth_df = df.dropna(subset=["download_mbps", "upload_mbps"])

            if not bandwidth_df.empty:
                avg_download = bandwidth_df["download_mbps"].mean()
                avg_upload = bandwidth_df["upload_mbps"].mean()
                max_download = bandwidth_df["download_mbps"].max()
                max_upload = bandwidth_df["upload_mbps"].max()
                min_download = bandwidth_df["download_mbps"].min()
                min_upload = bandwidth_df["upload_mbps"].min()

                print("\nBandwidth Statistics:")
                print(f"Average Download: {avg_download:.2f} Mbps")
                print(f"Average Upload: {avg_upload:.2f} Mbps")
                print(f"Maximum Download: {max_download:.2f} Mbps")
                print(f"Maximum Upload: {max_upload:.2f} Mbps")
                print(f"Minimum Download: {min_download:.2f} Mbps")
                print(f"Minimum Upload: {min_upload:.2f} Mbps")
                self.generate_plots(df, bandwidth_df)
            else:
                print("\nNo bandwidth data available for analysis.")
        except Exception as e:
            print(f"Error analyzing results: {e}")

    def generate_plots(self, df, bandwidth_df):
        try:
            # Set a modern style
            plt.style.use("ggplot")

            # Create figure with improved layout
            fig = plt.figure(figsize=(12, 18))

            # Define grid specification for more control
            gs = fig.add_gridspec(3, 1, hspace=0.3)

            # Connection status plot
            ax1 = fig.add_subplot(gs[0, 0])
            ax1.plot(
                df["timestamp"],
                df["connection_status"],
                "o-",
                color="#3498db",
                linewidth=2,
                markersize=4,
                alpha=0.7,
            )
            ax1.set_title(
                "WiFi Connection Status Over Time", fontsize=16, fontweight="bold"
            )
            ax1.set_ylabel("Connected (1) / Disconnected (0)", fontsize=12)
            ax1.set_ylim(-0.1, 1.1)
            ax1.fill_between(
                df["timestamp"], df["connection_status"], color="#3498db", alpha=0.2
            )
            ax1.grid(True, linestyle="--", alpha=0.7)

            # Format x-axis dates
            ax1.xaxis.set_major_formatter(
                plt.matplotlib.dates.DateFormatter("%m-%d %H:%M")
            )
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")

            # Bandwidth plot
            ax2 = fig.add_subplot(gs[1, 0])
            ax2.plot(
                bandwidth_df["timestamp"],
                bandwidth_df["download_mbps"],
                "o-",
                color="#2ecc71",
                linewidth=2,
                markersize=4,
                alpha=0.7,
                label="Download",
            )
            ax2.plot(
                bandwidth_df["timestamp"],
                bandwidth_df["upload_mbps"],
                "o-",
                color="#e74c3c",
                linewidth=2,
                markersize=4,
                alpha=0.7,
                label="Upload",
            )
            ax2.set_title(
                "Download and Upload Speeds Over Time", fontsize=16, fontweight="bold"
            )
            ax2.set_ylabel("Speed (Mbps)", fontsize=12)

            # Fill between lines and axis
            ax2.fill_between(
                bandwidth_df["timestamp"],
                bandwidth_df["download_mbps"],
                color="#2ecc71",
                alpha=0.2,
            )
            ax2.fill_between(
                bandwidth_df["timestamp"],
                bandwidth_df["upload_mbps"],
                color="#e74c3c",
                alpha=0.2,
            )

            ax2.legend(fontsize=12, loc="upper right", framealpha=0.9)
            ax2.grid(True, linestyle="--", alpha=0.7)

            # Format x-axis dates
            ax2.xaxis.set_major_formatter(
                plt.matplotlib.dates.DateFormatter("%m-%d %H:%M")
            )
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha="right")

            # Ping latency plot
            ax3 = fig.add_subplot(gs[2, 0])
            if "ping_ms" in bandwidth_df.columns:
                ax3.plot(
                    bandwidth_df["timestamp"],
                    bandwidth_df["ping_ms"],
                    "o-",
                    color="#9b59b6",
                    linewidth=2,
                    markersize=4,
                    alpha=0.7,
                )
                ax3.fill_between(
                    bandwidth_df["timestamp"],
                    bandwidth_df["ping_ms"],
                    color="#9b59b6",
                    alpha=0.2,
                )
                ax3.set_title("Ping Latency Over Time", fontsize=16, fontweight="bold")
                ax3.set_ylabel("Latency (ms)", fontsize=12)
                ax3.grid(True, linestyle="--", alpha=0.7)

                # Format x-axis dates
                ax3.xaxis.set_major_formatter(
                    plt.matplotlib.dates.DateFormatter("%m-%d %H:%M")
                )
                plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha="right")

                # Add average ping line
                avg_ping = bandwidth_df["ping_ms"].mean()
                ax3.axhline(
                    y=avg_ping,
                    color="#f39c12",
                    linestyle="--",
                    label=f"Avg: {avg_ping:.1f}ms",
                )
                ax3.legend(fontsize=12, loc="upper right", framealpha=0.9)

            # Add timestamp and info footer
            plt.figtext(
                0.5,
                0.01,
                f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ha="center",
                fontsize=10,
                style="italic",
            )

            plt.tight_layout(rect=[0, 0.02, 1, 0.98])
            plt.savefig(self.output_file, dpi=300, bbox_inches="tight")
            print(f"\nPlots saved to '{self.output_file}'")
        except Exception as e:
            print(f"Error generating plots: {e}")

    def run_monitor(self, duration_hours=24):
        print(f"Starting WiFi monitoring for {duration_hours} hours...")
        print(f"Data will be logged to '{self.log_file}'")
        print(f"Check interval: {self.check_interval} seconds")

        end_time = self.start_time + datetime.timedelta(hours=duration_hours)

        try:
            while datetime.datetime.now() < end_time:
                self.run_check()
                next_check_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=self.check_interval
                )
                time_until_next = (
                    next_check_time - datetime.datetime.now()
                ).total_seconds()
                if time_until_next > 0:
                    print(
                        f"Next check at {next_check_time.strftime('%H:%M:%S')} (in {time_until_next:.0f} seconds)"
                    )
                    time.sleep(time_until_next)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        finally:
            self.analyze_results()
