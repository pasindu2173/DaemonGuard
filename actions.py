import os
import subprocess
import psutil

# Define system critical processes and PIDs that must never be terminated
CRITICAL_PIDS = {1, 2}
CRITICAL_NAMES = {"systemd", "init", "gnome-shell", "Xorg", "wayland", "explorer.exe"}

def is_safe_process(pid):
    """
    Check if a process is safe from termination based on PID and name.
    Returns True if the process is critical/protected, False otherwise.
    """
    try:
        if pid in CRITICAL_PIDS:
            return True
        
        proc = psutil.Process(pid)
        name = proc.name().lower()
        
        for critical in CRITICAL_NAMES:
            if critical in name:
                return True
                
        return False
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return True  # Treat inaccessible processes as safe to prevent accidental errors

def safe_terminate(pid):
    """
    Safely terminate a process after verifying it is not a critical system process.
    Returns True if termination succeeded, False otherwise.
    """
    if is_safe_process(pid):
        print(f"[-] Protection Alert: PID {pid} is protected by safe-list. Termination blocked.")
        return False
        
    try:
        proc = psutil.Process(pid)
        proc.terminate()  # Send SIGTERM signal
        proc.wait(timeout=3)
        print(f"[+] Successfully terminated PID {pid} ({proc.name()})")
        return True
    except psutil.NoSuchProcess:
        print(f"[!] Process PID {pid} no longer exists.")
        return False
    except psutil.AccessDenied:
        print(f"[x] Permission denied to terminate PID {pid}.")
        return False
    except Exception as e:
        print(f"[x] Error terminating process PID {pid}: {e}")
        return False

def show_zenity_action_dialog(pid, process_name, waste_score):
    """
    Display an interactive Zenity graphical dialog alert to the user when a high waste score is detected.
    Provides options to terminate the process or ignore it.
    """
    zenity_cmd = [
        "zenity",
        "--question",
        "--title=🛡️ DaemonGuard Resource Protection",
        f"--text=High Resource Waste Detected!\n\nProcess: {process_name}\nPID: {pid}\nWaste Score: {waste_score}\n\nDo you want to terminate this process?",
        "--ok-label=Terminate Process",
        "--cancel-label=Ignore"
    ]
    
    try:
        # Run the Zenity dialog and check user response
        response = subprocess.run(zenity_cmd)
        
        # If user clicks 'Terminate Process' (Exit code 0)
        if response.returncode == 0:
            success = safe_terminate(pid)
            if success:
                subprocess.run(["notify-send", "🛡️ DaemonGuard", f"Process {process_name} (PID: {pid}) terminated successfully."])
            else:
                subprocess.run(["notify-send", "🛡️ DaemonGuard", f"Failed to terminate {process_name}. Protected process!"])
    except Exception as e:
        print(f"[x] Error displaying Zenity dialog: {e}")