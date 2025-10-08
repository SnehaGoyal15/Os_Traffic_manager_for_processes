# test_all.py - Comprehensive testing script
import time
import psutil
import os
from collectors import get_system_usage, get_high_resource_processes
from analyzer import check_system_metrics, get_comprehensive_alerts
from automation import auto_kill_processes, get_processes_for_review
from network_scanner import scan_ports_list

def test_basic_functionality():
    print("=== TESTING BASIC FUNCTIONALITY ===")
    
    # Test system metrics
    cpu, mem, disk = get_system_usage()
    print(f"✓ System Metrics - CPU: {cpu}%, Memory: {mem}%, Disk: {disk}%")
    
    # Test process monitoring
    processes = get_high_resource_processes(limit=3)
    print(f"✓ Process Monitoring - Found {len(processes)} high-resource processes")
    for p in processes[:2]:  # Show first 2
        print(f"  - {p}")
    
    # Test alerts
    alerts = check_system_metrics(cpu, mem, disk)
    print(f"✓ Alert System - {len(alerts)} current alerts")
    for alert in alerts:
        print(f"  - {alert}")

def test_network_scanning():
    print("\n=== TESTING NETWORK SCANNING ===")
    try:
        # Quick scan of common ports
        open_ports = scan_ports_list(ports_list=[80, 443, 22], timeout=0.5)
        print(f"✓ Network Scanning - Open ports: {open_ports}")
    except Exception as e:
        print(f"✗ Network Scanning Failed: {e}")

def test_automation_safety():
    print("\n=== TESTING AUTOMATION SAFETY ===")
    # Test in dry-run mode only!
    killed_count, killed_list = auto_kill_processes(dry_run=True)
    print(f"✓ Auto-kill Safety - Would kill {killed_count} processes (dry-run)")
    
    review_processes = get_processes_for_review()
    print(f"✓ Process Review - {len(review_processes)} processes need attention")

def test_resource_usage():
    print("\n=== TESTING MONITOR RESOURCE USAGE ===")
    pid = os.getpid()
    p = psutil.Process(pid)
    memory_mb = p.memory_info().rss / 1024 / 1024
    cpu_percent = p.cpu_percent()
    print(f"✓ Self-Monitoring - Memory: {memory_mb:.1f}MB, CPU: {cpu_percent}%")
    
    # Check if resource usage is reasonable
    if memory_mb > 500:
        print("⚠️  WARNING: High memory usage detected")
    if cpu_percent > 50:
        print("⚠️  WARNING: High CPU usage detected")

if __name__ == "__main__":
    print("Starting comprehensive tests...\n")
    
    test_basic_functionality()
    test_network_scanning()
    test_automation_safety()
    test_resource_usage()
    
    print("\n=== ALL TESTS COMPLETED ===")
    print("Now test the dashboard with: streamlit run dashboard_final.py")