import os
import time

BOLD  = "\033[1m"
RED   = "\033[31m"
RESET = "\033[0m"

# ---------- Tunables ----------
CHUNK_SIZE  = 4096           # bytes per write from the producer (4 KiB)
TOTAL_BYTES = 256 * 1024     # total bytes to send (256 KiB, > typical pipe capacity ~64 KiB)
READ_SIZE   = 1024           # bytes per read in the consumer (for when it loops properly)
READ_DELAY  = 0.05           # seconds to sleep after each read (for pacing; used once you fix the reader)
# ------------------------------

def write_chunked(fd, total_bytes, chunk_size):
    """
    Write 'total_bytes' to pipe 'fd' in fixed 'chunk_size' chunks.
    Blocks when the pipe is full.
    Catches BrokenPipeError (EPIPE signal) if the reader closes early.
    Returns the total number of bytes successfully written.
    """
    sent_total = 0
    chunk = b"x" * chunk_size
    chunk_idx = 0

    while sent_total < total_bytes:
        try:
            before = time.perf_counter()
            n = os.write(fd, chunk)  # may block when pipe is full but reader still open
            after = time.perf_counter()
            chunk_idx += 1
            sent_total += n
            print(
                f"[parent {os.getpid()}] wrote chunk {chunk_idx} ({n} bytes) "
                f"Δt={(after - before) * 1000:.1f} ms; total={sent_total}/{total_bytes}"
            )
        except BrokenPipeError:
            # Reader closed its read end; no further writes are possible.
            print(f"{BOLD}{RED}[parent {os.getpid()}] BrokenPipe during chunk {chunk_idx + 1}: "
                  f"sent_total={sent_total}/{total_bytes}; reader closed{RESET}")
            break

    return sent_total


def main():
    rfd, wfd = os.pipe()
    pid = os.fork()

    if pid == 0:
        # -----------------------
        # Child (consumer)
        # -----------------------
        os.close(wfd)  # close unused write end

        # Below is the fixed part:
        total_read = 0
        while True:
            data = os.read(rfd, READ_SIZE)   # blocks until data or EOF
            if not data:                     # b'' => all writers closed => EOF
                break
            total_read += len(data)
            print(f"[child {os.getpid()}] read {len(data)} bytes; total={total_read}", flush=True)
            time.sleep(READ_DELAY)           # slow consumer -> pipe fills -> writer blocks
        print(f"[child {os.getpid()}] EOF after {total_read} bytes", flush=True)

        os.close(rfd)

        os._exit(0)

    else:
        # -----------------------
        # Parent (producer)
        # -----------------------
        os.close(rfd)  # close unused read end

        print(
            f"[parent {os.getpid()}] starting chunked writes: "
            f"TOTAL_BYTES={TOTAL_BYTES}, CHUNK_SIZE={CHUNK_SIZE}"
        )
        sent_total = write_chunked(wfd, TOTAL_BYTES, CHUNK_SIZE)
        print(f"[parent {os.getpid()}] finished writes (sent_total={sent_total})")

        # Close write end (signals EOF to reader if it's still open).
        os.close(wfd)

        # Reap child.
        os.waitpid(pid, 0)
        print(f"[parent {os.getpid()}] child reaped, exiting")

if __name__ == "__main__":
    main()
