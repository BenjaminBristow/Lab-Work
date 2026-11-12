import os

counter = 10
pid = os.fork()
if pid == 0:
    counter = 20
    print(f"Child ({os.getpid()}): counter = {counter}", flush=True)
    os._exit(0)
else:
    os.wait()
    print(f"Parent ({os.getpid()}): counter = {counter}")
