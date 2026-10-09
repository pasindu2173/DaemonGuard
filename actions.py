import psutil

def kill_process(pid):
    """
    Safely terminates a target process using its PID.
    Returns (success_boolean, message_string)
    """
    try:
        proc = psutil.Process(pid)
        proc.terminate() # SIGTERM signal
        proc.wait(timeout=3)
        return True, f"Process {pid} ({proc.name()}) successfully terminated."
    except psutil.NoSuchProcess:
        return False, f"Process {pid} no longer exists."
    except psutil.AccessDenied:
        return False, f"Permission denied to terminate PID {pid}. Try running as root."
    except Exception as e:
        return False, f"Failed to terminate PID {pid}: {str(e)}"