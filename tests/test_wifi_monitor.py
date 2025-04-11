"""Basic tests for the wifi-monitor package."""

import pytest
from wifi_monitor.core import WiFiMonitor


def test_wifi_monitor_init():
    """Test that the WiFiMonitor class can be initialized."""
    monitor = WiFiMonitor()
    assert monitor.check_interval == 300
    assert monitor.log_file == "wifi_monitor.csv"
    assert monitor.output_file == "wifi_monitoring_report.png"

    # Test with custom parameters
    custom_monitor = WiFiMonitor(
        check_interval=600, log_file="custom_log.csv", output_file="custom_report.png"
    )
    assert custom_monitor.check_interval == 600
    assert custom_monitor.log_file == "custom_log.csv"
    assert custom_monitor.output_file == "custom_report.png"
