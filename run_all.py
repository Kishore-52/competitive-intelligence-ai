import subprocess
import sys
import os
import signal
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    backend_script = os.path.join(root_dir, "backend", "run.py")
    frontend_dir = os.path.join(root_dir, "frontend")
    
    processes = []
    
    print("=" * 60)
    print("      LAUNCHING MULTI-AGENT COMPETITIVE INTELLIGENCE SYSTEM      ")
    print("=" * 60)
    print("Starting FastAPI backend...")
    
    # 1. Start backend process
    backend_proc = subprocess.Popen(
        [sys.executable, backend_script],
        cwd=os.path.join(root_dir, "backend"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(("Backend", backend_proc))
    
    print("Starting Vite React frontend...")
    
    # Check if npm cmd exists on Windows vs unix
    shell = os.name == 'nt'
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
    
    # 2. Start frontend process
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=shell
    )
    processes.append(("Frontend", frontend_proc))
    
    # Put streams into non-blocking mode
    import threading
    
    def log_reader(name, process):
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.strip()}")
        process.stdout.close()

    # Create worker threads to read logs concurrently
    threads = []
    for name, proc in processes:
        t = threading.Thread(target=log_reader, args=(name, proc), daemon=True)
        t.start()
        threads.append(t)

    print("\nSystem running! Access the services below:")
    print("  - Backend API: http://127.0.0.1:8000")
    print("  - Backend Docs: http://127.0.0.1:8000/docs")
    print("  - Frontend UI: http://localhost:5173")
    print("-" * 60)
    print("Press Ctrl+C to terminate both servers...\n")
    
    try:
        while True:
            # Check if any process has terminated early
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n[System] {name} process terminated unexpectedly (exit code {proc.returnvalue}).")
                    raise KeyboardInterrupt
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        for name, proc in processes:
            print(f"Stopping {name}...")
            if os.name == 'nt':
                # On Windows, kill subprocesses cleanly
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
