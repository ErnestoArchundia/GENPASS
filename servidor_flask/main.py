from servidor_flask.nmap import run_nmap_realtime
from servidor_flask.report import load_vulns, check_vuln

def run_scan(target, progress_callback=None):

    vulns_db = load_vulns()

    raw_results = run_nmap_realtime(target, progress_callback)

    results = []

    for r in raw_results:
        vuln = check_vuln(r["banner"], vulns_db)

        results.append({
            "port": r["port"],
            "banner": r["banner"],
            "vuln": vuln if vuln else "Ninguna"
        })

    return results