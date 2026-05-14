import json

def load_vulns():
    try:
        with open("vulns.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"DEBUG: Error al cargar vulns.json: {e}")
        return {}

def check_vuln(banner, vulns_db):
    if not banner or banner == "Sin información":
        return None
    banner_lower = banner.lower()
    for key, value in vulns_db.items():
        if key.lower() in banner_lower:
            return value
    return None

def run_scan(target, progress_callback=None):
    processed_results = []
    
    try:
        # 1. Cargar DB
        vulns_db = load_vulns()
        
        # 2. Ejecutar Nmap (Asegúrate que run_nmap_realtime devuelva la lista de puertos)
        # Esta función debe esperar los ~120 segundos que tarda Nmap
        raw_results = run_nmap_realtime(target, progress_callback)
        
        if not raw_results:
            print("DEBUG: Nmap terminó pero no devolvió datos.")
            return []

        # 3. PROCESAR CADA RESULTADO (Aquí es donde estaba el fallo)
        for r in raw_results:
            # Extraer datos con valores por defecto
            port = str(r.get("port", "0"))
            banner = r.get("banner", "Sin información")
            
            # Intentar detectar vuln por banner primero
            vuln_text = check_vuln(banner, vulns_db)

            # Si el banner no dijo nada, forzamos por puerto (Fallback)
            if not vuln_text:
                if port == "22":
                    vuln_text = "SSH abierto - Posible vector de fuerza bruta"
                elif port == "80":
                    vuln_text = "Servidor HTTP detectado - Revisar vulnerabilidades web"
                elif port in ["139", "445"]:
                    vuln_text = "Samba/SMB detectado - Riesgo de exploits de red"
                elif port == "3306":
                    vuln_text = "Base de datos MySQL expuesta"
                elif port == "10000":
                    vuln_text = "Panel de control Webmin detectado"
                elif port == "631":
                    vuln_text = "Servicio de impresión CUPS activo"
                else:
                    vuln_text = "Ninguna"

            # Creamos un NUEVO diccionario con la información limpia
            item = {
                "port": port,
                "banner": banner,
                "vuln": vuln_text
            }
            processed_results.append(item)

        print(f"DEBUG: Procesamiento finalizado. Enviando {len(processed_results)} resultados a la tabla.")
        
    except Exception as e:
        print(f"ERROR CRÍTICO en run_scan: {e}")
    
    return processed_results # <--- Esto es lo que recibe tu Flask