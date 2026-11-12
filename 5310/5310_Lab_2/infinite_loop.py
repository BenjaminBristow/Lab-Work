import time
import os
import time
import signal
import sys


def signal_handler(sig, frame):
    print("\nReceived interrupt signal. Exiting gracefully...")
    # sys.exit(0)

def main() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGKILL, signal_handler)

    # Repeat the loop 40 times
    count = 40
    sleep = 1    # Modify this value to change the sleep duration
    # Grab the current process ID
    pid = os.getpid()
    # Stop the infinite loop after count reaches 0
    while count > 0:
        # Print process details
        print("{:.06f}: {} This is an infinite loop.".format(time.time(), pid))
        time.sleep(sleep)  # Sleep for 0.01 seconds
        count -= 1 # Decrement the remaining iterations

if __name__ == "__main__":
    main()



