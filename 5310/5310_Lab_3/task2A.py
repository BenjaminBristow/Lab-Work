import threading
import queue
import time
import hashlib

# ---------------- Tunables ----------------
N_TASKS      = 12          # number of "download+compute" tasks
IO_DELAY     = 0.5         # seconds of simulated I/O wait per task
NUM_THREADS  = 4           # number of consumer threads
COMPUTE_SIZE = 200_000     # small CPU work to follow the I/O wait
VERBOSE      = True        # set False for quieter output
# ------------------------------------------

def cpu_work(n=COMPUTE_SIZE) -> str:
    """Small CPU-bound step after the I/O wait; returns hex digest."""
    h = hashlib.sha256()
    for i in range(1, n, 1000):  # modest CPU loop so I/O overlap dominates
        h.update(i.to_bytes(4, "little"))
    return h.hexdigest()

def one_task(task_id: int, io_delay: float, t0: float) -> None:
    """Simulated 'download': block on I/O (sleep) then do a small CPU step."""
    t = time.perf_counter() - t0
    if VERBOSE:
        print(f"[consumer {threading.get_ident()}] task {task_id:02d}: start (t={t*1000:.0f}ms) → I/O wait {io_delay:.2f}s")
    time.sleep(io_delay)  # simulated blocking I/O (releases the GIL)
    digest = cpu_work()
    t = time.perf_counter() - t0
    if VERBOSE:
        print(f"[consumer {threading.get_ident()}] task {task_id:02d}: done (t={t*1000:.0f}ms) sha256[:8]={digest[:8]}")

def sequential_run(n_tasks=N_TASKS, io_delay=IO_DELAY):
    print("\n=== SEQUENTIAL RUN ===")
    t0 = time.perf_counter()
    for k in range(n_tasks):
        # Producer "submits" and immediately consumes (no concurrency)
        one_task(k, io_delay, t0)
    elapsed = time.perf_counter() - t0
    print(f"[sequential] tasks={n_tasks} delay={io_delay:.2f}s  elapsed={elapsed:.2f}s")
    return elapsed

def threaded_run(n_tasks=N_TASKS, io_delay=IO_DELAY, num_threads=NUM_THREADS):
    print("\n=== THREADED RUN (producer + consumers with shared queue) ===")
    q: queue.Queue[int] = queue.Queue()

    # --- Producer: enqueue all tasks (conceptual critical section lives inside q.put) ---
    t0 = time.perf_counter()
    for k in range(n_tasks):
        # Conceptual critical section: enqueue into shared buffer
        # In Python, queue.put() handles locking & signaling internally.
        q.put(k)

    print_lock = threading.Lock()  # optional: tidy print output

    def consumer():
        while True:
            try:
                # Conceptual critical section: dequeue from shared buffer
                # In Python, queue.get() handles locking & signaling internally.
                k = q.get_nowait()
            except queue.Empty:
                return
            if VERBOSE:
                with print_lock:
                    print(f"[consumer {threading.get_ident()}] got task {k:02d}")
            one_task(k, io_delay, t0)
            q.task_done()

    consumers = [threading.Thread(target=consumer, daemon=True) for _ in range(num_threads)]
    for t in consumers:
        t.start()

    # Wait until all queued tasks are processed
    q.join()
    elapsed = time.perf_counter() - t0
    print(f"[threaded]  tasks={n_tasks} delay={io_delay:.2f}s threads={num_threads}  elapsed={elapsed:.2f}s")
    return elapsed

if __name__ == "__main__":
    # Run both modes back to back for easy comparison
    seq = sequential_run()
    thr = threaded_run()
    print("\n=== SUMMARY ===")
    print(f"sequential: {seq:.2f}s")
    print(f"threaded:   {thr:.2f}s  (speedup ×{seq/max(thr,1e-9):.2f})")

    # Experiments to try:
    # - Increase N_TASKS; keep IO_DELAY fixed.
    # - Change NUM_THREADS to 1, 2, 4, 8 and observe diminishing returns.
    # - Set IO_DELAY near zero to see that threads no longer help (now it's CPU-bound).