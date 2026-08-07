import subprocess
import time
import re
import signal
import sys
import os

NEXT_CONFIG_PATH = r"C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\frontend\next.config.ts"
FRONTEND_DIR = r"C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\frontend"
BACKEND_DIR = r"C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\backend"

processes = []

def cleanup(*_):
    print("\nBeende Server...", flush=True)
    for p in processes:
        try:
            p.kill()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def update_next_config(hostname):
    """Inject the Serveo hostname into next.config.ts allowedDevOrigins."""
    try:
        with open(NEXT_CONFIG_PATH, "r") as f:
            content = f.read()
        new_origins = f"allowedDevOrigins: ['localhost', 'localhost:3000', 'localhost:3001', '127.0.0.1', '127.0.0.1:3000', '127.0.0.1:3001', '192.168.5.20', '*.serveousercontent.com', '{hostname}']"
        new_content = re.sub(
            r"allowedDevOrigins:\s*\[.*?\]",
            new_origins,
            content,
            flags=re.DOTALL
        )
        with open(NEXT_CONFIG_PATH, "w") as f:
            f.write(new_content)
        print(f"  -> next.config.ts aktualisiert mit: {hostname}", flush=True)
    except Exception as e:
        print(f"  -> WARNUNG: next.config.ts konnte nicht aktualisiert werden: {e}", flush=True)

def wait_for_serveo_url(serveo_process, timeout=30):
    """Read Serveo stdout until we get the forwarding URL."""
    start = time.time()
    while time.time() - start < timeout:
        line = serveo_process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        decoded = line.decode('utf-8', errors='ignore').strip()
        if "Forwarding HTTP traffic from" in decoded:
            url = decoded.split("Forwarding HTTP traffic from")[1].strip()
            return url
    return None

if __name__ == "__main__":
    # 1. Start Backend
    print("[1/4] Starte Backend (FastAPI)...", flush=True)
    backend_log = open("backend.log", "w")
    python_exe = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"
    backend = subprocess.Popen(
        [python_exe, "-u", "main.py"],
        cwd=BACKEND_DIR,
        stdout=backend_log,
        stderr=backend_log
    )
    processes.append(backend)

    # 2. Start Serveo Tunnel (before Next.js so we know the hostname)
    print("[2/4] Starte Serveo Tunnel...", flush=True)
    serveo = subprocess.Popen(
        ["ssh", "-o", "ServerAliveInterval=60", "-R", "80:127.0.0.1:3001", "serveo.net", "-o", "StrictHostKeyChecking=no"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    processes.append(serveo)

    # Wait for URL
    tunnel_url = wait_for_serveo_url(serveo)
    if not tunnel_url:
        print("FEHLER: Serveo-Tunnel konnte nicht gestartet werden!", flush=True)
        cleanup()

    hostname = tunnel_url.replace("https://", "").replace("http://", "")
    with open("tunnel_url.txt", "w") as f:
        f.write(tunnel_url)

    # 3. Update next.config.ts with the new hostname
    print("[3/4] Aktualisiere next.config.ts...", flush=True)
    update_next_config(hostname)

    # 4. Start Next.js Frontend
    print("[4/4] Starte Frontend (Next.js)...", flush=True)
    frontend_log = open("frontend.log", "w")
    npm_cmd = r"C:\Program Files\nodejs\npm.cmd"
    frontend = subprocess.Popen(
        [npm_cmd, "run", "dev", "--", "-p", "3001"],
        cwd=FRONTEND_DIR,
        stdout=frontend_log,
        stderr=frontend_log
    )
    processes.append(frontend)

    # Wait for Next.js to be ready
    time.sleep(6)

    print("\n" + "=" * 70, flush=True)
    print("  AutoShorts Dev Server ist online!", flush=True)
    print("=" * 70, flush=True)
    print(f"\n  OEFFNE DIESEN LINK AUF DEM HANDY:", flush=True)
    print(f"  {tunnel_url}", flush=True)
    print("\n" + "=" * 70 + "\n", flush=True)

    # Keep alive
    try:
        while True:
            # Check if any critical process died
            if backend.poll() is not None:
                print("WARNUNG: Backend ist abgestuerzt! Starte neu...", flush=True)
                backend = subprocess.Popen(
                    [python_exe, "-u", "main.py"],
                    cwd=BACKEND_DIR,
                    stdout=backend_log,
                    stderr=backend_log
                )
                processes.append(backend)
            if frontend.poll() is not None:
                print("WARNUNG: Frontend ist abgestuerzt! Starte neu...", flush=True)
                frontend = subprocess.Popen(
                    ["cmd.exe", "/c", "npm run dev -- -p 3001"],
                    cwd=FRONTEND_DIR,
                    stdout=frontend_log,
                    stderr=frontend_log
                )
                processes.append(frontend)
            time.sleep(5)
    except KeyboardInterrupt:
        cleanup()
