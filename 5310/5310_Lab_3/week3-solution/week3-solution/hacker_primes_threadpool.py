#!/usr/bin/env python3

import os
import threading
import math
import time
import argparse

# -------------------------
# Simple ThreadPool
# -------------------------
class ThreadPool:
    def __init__(self, n_workers, maxsize=None):
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full  = threading.Condition(self.lock)
        self.tasks = []              # list of (fn, args, kwargs)
        self.closed = False
        self.maxsize = maxsize
        self.workers = []
        for wid in range(n_workers):
            t = threading.Thread(target=self._worker, args=(wid,), daemon=True)
            t.start()
            self.workers.append(t)

    def submit(self, fn, *args, **kwargs):
        with self.lock:
            while self.maxsize is not None and len(self.tasks) >= self.maxsize and not self.closed:
                self.not_full.wait()
            if self.closed:
                raise RuntimeError("ThreadPool is closed")
            self.tasks.append((fn, args, kwargs))
            self.not_empty.notify()

    def _worker(self, wid):
        while True:
            with self.lock:
                while not self.tasks and not self.closed:
                    self.not_empty.wait()
                if not self.tasks and self.closed:
                    return
                fn, args, kwargs = self.tasks.pop(0)
                if self.maxsize is not None:
                    self.not_full.notify()
            try:
                fn(*args, **kwargs)
            except Exception as e:
                print(f"[W{wid}] task error: {e}")

    def close(self, wait=True):
        with self.lock:
            self.closed = True
            self.not_empty.notify_all()
            self.not_full.notify_all()
        if wait:
            for t in self.workers:
                t.join()

# -------------------------
# Prime helper
# -------------------------
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    r = int(math.isqrt(n))
    for d in range(3, r+1, 2):
        if n % d == 0:
            return False
    return True

def count_primes_in_range(start: int, end: int, result_container: dict, idx: int):
    """Count primes in [start, end) and store the result at result_container[idx]."""
    cnt = 0
    for x in range(start, end):
        if is_prime(x):
            cnt += 1
    result_container[idx] = cnt

# -------------------------
# Demo driver
# -------------------------
def run_threaded_prime_search(total: int, tasks: int, workers: int, maxqueue: int = None):
    """
    total: search numbers in [2, total)
    tasks: how many chunks to split into
    workers: number of worker threads in the pool
    maxqueue: optional bound on pending tasks (None = unbounded)
    """
    chunk = max(1, total // tasks)
    pool = ThreadPool(n_workers=workers, maxsize=maxqueue)
    results = [0] * tasks

    t0 = time.perf_counter()
    for i in range(tasks):
        s = 2 + i * chunk
        e = min(total, s + chunk)
        pool.submit(count_primes_in_range, s, e, results, i)
    pool.close(wait=True)
    elapsed = time.perf_counter() - t0
    total_primes = sum(results)
    return elapsed, total_primes

# -------------------------
# Multiprocess version (fork + one pipe per worker, as in Part 1)
# -------------------------
def run_forked_prime_search(total: int, tasks: int, processes: int):
    """
    Same decomposition as the threaded version (same 'tasks' chunks),
    but the chunks are shared out across 'processes' forked children.
    Child w handles chunks w, w+P, w+2P, ... and writes its count back
    to the parent through its own pipe.
    """
    chunk = max(1, total // tasks)
    t0 = time.perf_counter()

    children = []                         # list of (pid, rfd)
    for wid in range(processes):
        rfd, wfd = os.pipe()
        pid = os.fork()
        if pid == 0:
            # ---- child: writer ----
            os.close(rfd)                 # child only writes
            local = {}
            for i in range(wid, tasks, processes):
                s = 2 + i * chunk
                e = min(total, s + chunk)
                count_primes_in_range(s, e, local, i)
            os.write(wfd, str(sum(local.values())).encode())
            os.close(wfd)                 # EOF for the parent
            os._exit(0)
        # ---- parent: reader ----
        os.close(wfd)                     # parent only reads
        children.append((pid, rfd))

    total_primes = 0
    for pid, rfd in children:
        buf = b""
        while True:                       # read until EOF 
            data = os.read(rfd, 4096)
            if not data:
                break
            buf += data
        os.close(rfd)
        os.waitpid(pid, 0)
        total_primes += int(buf.decode())

    elapsed = time.perf_counter() - t0
    return elapsed, total_primes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=int, default=200000, help="search numbers in [2,total)")
    parser.add_argument("--tasks", type=int, default=8, help="number of chunks/tasks")
    parser.add_argument("--workers", type=int, default=4, help="number of worker threads")
    parser.add_argument("--maxqueue", type=int, default=0, help="optional maxsize for task queue (0 = unbounded)")
    parser.add_argument("--processes", type=int, default=0,
                        help="if > 0, run the multiprocess version with this many processes instead of threads")
    args = parser.parse_args()

    if args.processes > 0:
        print(f"Multiprocess: total={args.total} tasks={args.tasks} processes={args.processes}")
        t, total_primes = run_forked_prime_search(args.total, args.tasks, args.processes)
    else:
        maxqueue = args.maxqueue if args.maxqueue > 0 else None
        print(f"Threaded baseline: total={args.total} tasks={args.tasks} workers={args.workers} maxqueue={maxqueue}")
        t, total_primes = run_threaded_prime_search(args.total, args.tasks, args.workers, maxqueue)
    print(f"RESULT: elapsed={t:.3f}s primes={total_primes}")

if __name__ == "__main__":
    main()
