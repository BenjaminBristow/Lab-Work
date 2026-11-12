

import os
import time
import math
import sys


def count_primes(a, b):
    """Return number of primes in range [a, b] (simple trial division)."""
    count = 0
    for num in range(a, b + 1):
        prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                prime = False
                break
        if prime:
            count += 1
    return count


def main():
    # read an integer from the command line to set the number of parallel processes
    # if no argument is given, use 1 (no parallelism)
    # For example, run `python3 prime.py 4` loads the value 4 to the variable `parallel`
    parallel = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    N = 500000  # upper limit for prime counting

    start = time.time()
    # Parent computes primes in lower half
    print(f"Parent ({os.getpid()}) counting primes from 1 to {N}")
    result = count_primes(1, N)
    print(f"Parent found {result} primes")
    end = time.time()

    # Print the total time taken
    print(f"Total time: {end - start:.6f}s")


if __name__ == "__main__":
    main()
