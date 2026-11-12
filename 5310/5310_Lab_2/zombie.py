import os
import time

pid = os.fork()
if pid == 0:
    print(f"Child PID: {os.getpid()}", flush=True)
    os._exit(0)
else:
    print(f"Parent PID: {os.getpid()}")
    print(f"Child PID: {pid}")
    print("Parent delaying wait() for 30 seconds...", flush=True)
    time.sleep(30)
    finished_pid, status = os.waitpid(pid, 0)
    print(
        f"Child {finished_pid} reaped; exit status={os.waitstatus_to_exitcode(status)}")
