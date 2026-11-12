import os
import time
import random
import select

N_CHILDREN = 3

def child_writer(wfd, cid):
    """Each child writes a few messages to its pipe and exits."""
    for i in range(5):
        msg = f"child {cid} msg {i}\n".encode()
        os.write(wfd, msg)
        time.sleep(random.uniform(0.05, 0.3))  # simulate variable work
    os.close(wfd)  # signal EOF

def parent_event_loop(read_fds):
    """Parent monitors multiple pipes using select()."""
    while read_fds:
        # TODO: Use select() to wait for any of the FDs to become readable
        rlist, _, _ = select.select(read_fds, [], [])

        for fd in rlist:
            data = os.read(fd, 4096)
            if not data:
                print(f"[parent] fd {fd} EOF, closing")
                os.close(fd)
                read_fds.remove(fd)
            else:
                print(f"[parent] fd {fd} -> {data.decode().rstrip()}")

def main():
    children = []
    read_fds = []

    for cid in range(N_CHILDREN):
        rfd, wfd = os.pipe()
        pid = os.fork()

        if pid == 0:
            # Child process
            os.close(rfd)  # close unused read end
            child_writer(wfd, cid)
            os._exit(0)
        else:
            # Parent process
            os.close(wfd)  # close unused write end
            read_fds.append(rfd)
            children.append(pid)

    parent_event_loop(read_fds)

    # Reap all children
    for pid in children:
        os.waitpid(pid, 0)

    print("[parent] all children done")

if __name__ == "__main__":
    main()