import subprocess
import time
import os
import sys

LOG_FILE = "run.log"

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def run_command(cmd, cwd=None):
    log(f"Execution: {cmd}")
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
            encoding="utf-8"
        )
        for line in process.stdout:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
            sys.stdout.write(line)
        process.wait()
        log(f"Return code: {process.returncode}\n")
        return process.returncode == 0
    except Exception as e:
        log(f"Error executing: {e}\n")
        return False

def main():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    log("=== STARTING AUTONOMOUS RESEARCH CYCLE ===")
    
    # 1. Evaluate Train
    log("--- 1. Evaluating SemanticEngine Accuracy ---")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    run_command("uv run train.py", cwd="autoresearch")
    
    # 2. Start Backend
    log("--- 2. Launching Backend Server for Validation ---")
    # Using python backend/main.py directly
    server_process = subprocess.Popen(
        "uv run python backend/main.py",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd="."
    )
    
    # Wait for health check
    time.sleep(5)  # wait for startup
    log("Waiting for backend health check...")
    
    import requests
    healthy = False
    for i in range(15):
        try:
            res = requests.get("http://localhost:8000/health")
            if res.status_code == 200:
                log(f"Backend online after {i+1}s ✓")
                healthy = True
                break
        except Exception:
            time.sleep(1)
            
    if not healthy:
        log("❌ FAIL: Backend failed to respond to /health in 15 seconds")
        server_process.terminate()
        sys.exit(1)
        
    # 3. Run Test Agents
    log("--- 3. Running test_all_agents.py ---")
    run_command("uv run python backend/tests/test_all_agents.py")
    
    # 4. Cleanup
    log("--- 4. Stopping Backend ---")
    # On Windows, taskkill might be required if shells are nested
    try:
        # Just terminate first
        server_process.terminate()
        server_process.wait(timeout=5)
    except Exception:
        log("Forcing backend shutdown...")
        subprocess.run("taskkill /F /IM python.exe /T", shell=True, stdout=subprocess.DEVNULL)
        
    log("=== CYCLE COMPLETE ===")

if __name__ == "__main__":
    main()
