import os
import signal
import psutil
from typing import Tuple

# Protected System PIDs that must NEVER be terminated
PROTECTED_PIDS = {1, 2}  # Systemd / init process, kernel threads

def kill_process(pid: int) -> Tuple[bool, str]:
    """
    Safely attempts to terminate a process by PID.
    Returns (success: bool, message: str)
    """
    # 1. Protect critical System PIDs
    if pid in PROTECTED_PIDS:
        return False, f"Permission Denied: PID {pid} is a critical system process!"

    try:
        # Check if process exists
        proc = psutil.Process(pid)
        proc_name = proc.name()

        # Try SIGTERM (Graceful shutdown) first
        proc.terminate()
        proc.wait(timeout=3)
        return True, f"Successfully terminated process '{proc_name}' (PID: {pid})."

    except psutil.NoSuchProcess:
        return False, f"Error: No active process found with PID {pid}."

    except psutil.TimeoutExpired:
        # If graceful shutdown fails, force kill with SIGKILL
        try:
            proc.kill()
            return True, f"Process '{proc_name}' (PID: {pid}) forced to kill (SIGKILL)."
        except Exception as e:
            return False, f"Failed to force kill process {pid}: {str(e)}"

    except psutil.AccessDenied:
        return False, f"Access Denied: Insufficient permissions to terminate PID {pid}. Try running as root."

    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"