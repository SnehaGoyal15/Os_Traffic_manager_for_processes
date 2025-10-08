import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
def _check_port(host, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((host, port))
        s.close()
        return port if result == 0 else None
    except Exception:
        try:
            s.close()
        except Exception:
            pass
        return None
def scan_ports_range(host='127.0.0.1', start=1, end=1024, timeout=0.2, max_workers=100):
    if start < 1:
        start = 1
    if end > 65535:
        end = 65535
    ports = range(start, end + 1)
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_check_port, host, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                open_ports.append(res)
    return sorted(open_ports)
def scan_ports_list(host='127.0.0.1', ports_list=None, timeout=0.2, max_workers=100):
    if ports_list is None:
        ports_list = []
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_check_port, host, p, timeout): p for p in ports_list}
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                open_ports.append(res)
    return sorted(open_ports)
