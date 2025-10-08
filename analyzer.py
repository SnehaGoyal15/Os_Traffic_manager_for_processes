# analyzer.py - FIXED VERSION
import psutil
from collections import defaultdict, deque

# Thresholds (more conservative)
CPU_THRESHOLD = 85
MEM_THRESHOLD = 80
DISK_THRESHOLD = 90

# Process history for trend analysis
process_history = defaultdict(lambda: {"cpu": deque(maxlen=10), "mem": deque(maxlen=10)})

def check_system_metrics(cpu, mem, disk):
    alerts = []
    if cpu > CPU_THRESHOLD:
        alerts.append(f"High CPU usage: {cpu}%")
    if mem > MEM_THRESHOLD:
        alerts.append(f"High Memory usage: {mem}%")
    if disk > DISK_THRESHOLD:
        alerts.append(f"High Disk usage: {disk}%")
    return alerts

def correlation_checks(cpu, mem, disk):
    issues = []
    if cpu > 85 and mem > 80:
        issues.append("System overload risk (CPU + Memory both high)")
    if disk > 90 and cpu > 70:
        issues.append("Heavy disk usage with high CPU load")
    if cpu > 90 and mem > 90:
        issues.append("CRITICAL: System near crash state!")
    return issues

def detect_memory_leak(processes_data):
    """Detect processes with continuously growing memory"""
    memory_leak_alerts = []
    
    for proc_data in processes_data:
        try:
            parts = proc_data.split()
            if len(parts) < 4:
                continue
                
            pid = parts[0]
            mem_usage = float(parts[-1])
            
            # Add to history
            process_history[pid]["mem"].append(mem_usage)
            
            # Check for memory leak pattern (continuous growth)
            history = list(process_history[pid]["mem"])
            if len(history) >= 5:
                # Check if memory is consistently increasing
                increasing = all(history[i] <= history[i+1] for i in range(len(history)-1))
                if increasing and history[-1] > 100:  # Only alert if using significant memory
                    memory_leak_alerts.append(f"Possible memory leak in PID {pid} - Memory: {mem_usage:.1f}MB")
                    
        except (ValueError, IndexError):
            continue
    
    return memory_leak_alerts

def detect_zombie_processes():
    """Find zombie processes"""
    zombies = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            if proc.info['status'] == psutil.STATUS_ZOMBIE:
                zombies.append(f"Zombie process: {proc.info['name']} (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return zombies

def detect_suspicious_processes():
    """Detect potentially malicious processes - FIXED VERSION"""
    suspicious = []
    suspicious_patterns = [
        'cryptominer', 'coinminer', 'miner', 'xmr', 'monero', 'bitcoin',
        'mimikatz', 'metasploit', 'payload', 'backdoor', 'keylogger'
    ]
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name'].lower()
            
            # Safely get command line if available
            cmdline = ""
            try:
                if proc.info.get('cmdline'):
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                cmdline = ""
            
            # Check name and command line for suspicious patterns
            for pattern in suspicious_patterns:
                if pattern in name or pattern in cmdline:
                    suspicious.append(f"Suspicious process: {proc.info['name']} (PID: {proc.info['pid']}) - Pattern: {pattern}")
                    break
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue
    
    return suspicious

def get_comprehensive_alerts(cpu, mem, disk, processes_data):
    """Get all types of alerts - FIXED VERSION"""
    all_alerts = []
    
    # Basic system alerts
    all_alerts.extend(check_system_metrics(cpu, mem, disk))
    
    # Correlation alerts
    all_alerts.extend(correlation_checks(cpu, mem, disk))
    
    # Memory leak detection
    all_alerts.extend(detect_memory_leak(processes_data))
    
    # Zombie processes
    all_alerts.extend(detect_zombie_processes())
    
    # Suspicious processes (with error handling)
    try:
        all_alerts.extend(detect_suspicious_processes())
    except Exception as e:
        # If suspicious process detection fails, continue without it
        all_alerts.append(f"Note: Suspicious process scan unavailable: {e}")
    
    return all_alerts