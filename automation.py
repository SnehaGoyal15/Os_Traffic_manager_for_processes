# automation.py - SAFER VERSION (No Emojis)
import psutil
import time

# Comprehensive whitelist of safe processes
SAFE_PROCESSES = [
    # Windows System Processes
    "System", "svchost.exe", "explorer.exe", "winlogon.exe", "csrss.exe",
    "lsass.exe", "services.exe", "smss.exe", "taskhostw.exe", "dwm.exe",
    "ctfmon.exe", "fontdrvhost.exe", "RuntimeBroker.exe", "wininit.exe",
    
    # Streamlit & Python (your own processes)
    "python.exe", "pythonw.exe", "streamlit.exe",
    
    # Browser processes (common)
    "chrome.exe", "firefox.exe", "msedge.exe", "browser.exe",
    
    # Development tools
    "code.exe", "vscode.exe", "devenv.exe", "pycharm.exe",
    
    # System UI
    "sihost.exe", "ShellExperienceHost.exe", "StartMenuExperienceHost.exe",
    
    # Antivirus and security
    "msmpeng.exe", "securityhealthservice.exe", "defender.exe"
]

# Processes that should NEVER be killed
CRITICAL_SYSTEM_PROCESSES = ["System", "smss.exe", "csrss.exe", "wininit.exe", "lsass.exe", "services.exe"]

def is_process_safe(process_name, pid):
    """Check if process is safe to kill"""
    process_name_lower = process_name.lower()
    
    # Check safe list
    if process_name in SAFE_PROCESSES:
        return True
        
    # Check critical system processes
    if process_name in CRITICAL_SYSTEM_PROCESSES:
        return True
    
    # Additional safety checks
    try:
        process = psutil.Process(pid)
        
        # Don't kill your own monitoring process!
        if "python" in process_name_lower or "streamlit" in process_name_lower:
            return True
            
        # Don't kill parent processes
        if process.ppid() in [0, 1, 4]:  # System PID
            return True
            
        # Check if process is running as SYSTEM
        username = process.username()
        if 'SYSTEM' in username or 'NT AUTHORITY\\SYSTEM' in username:
            return True
            
        # Don't kill Windows Store or UWP apps
        if "Microsoft" in process_name or "Windows" in process_name:
            return True
            
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return True  # When in doubt, don't kill
    
    return False

def analyze_process_for_killing(pid, name, cpu, memory_mb):
    """
    Analyze if a process should be considered for killing
    Returns: (should_kill, reason)
    """
    # Skip safe processes
    if is_process_safe(name, pid):
        return False, "Safe process"
    
    # Very high CPU for extended period
    if cpu > 85:
        return True, f"Very high CPU usage: {cpu}%"
    
    # Extreme memory usage
    if memory_mb > 1500:  # 1.5GB threshold
        return True, f"Extreme memory usage: {memory_mb:.1f}MB"
    
    # Suspicious behavior patterns
    suspicious_keywords = ['cryptominer', 'coinminer', 'miner', 'malware', 'virus', 'trojan']
    if any(keyword in name.lower() for keyword in suspicious_keywords):
        return True, f"Suspicious process name: {name}"
    
    return False, "Normal process"

def get_processes_for_review():
    """
    Get list of processes that might need user attention
    """
    review_list = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cpu = proc.info['cpu_percent'] or 0
            memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
            
            should_kill, reason = analyze_process_for_killing(pid, name, cpu, memory_mb)
            
            if should_kill:
                review_list.append({
                    'pid': pid,
                    'name': name,
                    'cpu': cpu,
                    'memory_mb': memory_mb,
                    'reason': reason
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Sort by CPU usage (highest first)
    return sorted(review_list, key=lambda x: x['cpu'], reverse=True)

def auto_kill_processes(dry_run=True):
    """
    SAFER version: Only kills clearly problematic, non-essential processes
    """
    killed_count = 0
    processes_killed = []
    
    review_processes = get_processes_for_review()
    
    for proc_info in review_processes:
        pid = proc_info['pid']
        name = proc_info['name']
        reason = proc_info['reason']
        
        if dry_run:
            msg = f"[DRY RUN] Would kill {name} (PID={pid}) - Reason: {reason}"
            print(msg)
            processes_killed.append(f"DRY RUN: {name} (PID={pid})")
        else:
            try:
                # Try graceful termination first
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait a bit
                time.sleep(1)
                
                # Check if still running and force kill if needed
                if process.is_running():
                    process.kill()
                    time.sleep(0.5)
                
                print(f"Killed {name} (PID={pid}) - Reason: {reason}")
                killed_count += 1
                processes_killed.append(f"KILLED: {name} (PID={pid})")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Failed to kill {name} (PID={pid}): {e}")
                processes_killed.append(f"FAILED: {name} (PID={pid})")
    
    return killed_count, processes_killed