import subprocess
import re

def run_nmap_realtime(target, progress_callback=None):

    command = ["nmap", "-sV", "--stats-every", "1s", target]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    results = []

    for line in process.stdout:

        # 🔥 Detectar progreso
        match = re.search(r"(\d+)% done", line)
        if match:
            percent = int(match.group(1))

            if progress_callback:
                progress_callback(percent)

        # 🔥 Detectar puertos abiertos
        if "/tcp" in line and "open" in line:
            parts = line.split()

            port = parts[0]
            service = parts[2] if len(parts) > 2 else "unknown"

            results.append({
                "port": port,
                "banner": service,
                "vuln": "Ninguna"
            })

    if progress_callback:
        progress_callback(100)

    return results