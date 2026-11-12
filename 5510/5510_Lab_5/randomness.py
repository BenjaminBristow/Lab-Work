"""
Lab 5, Task 1, Question 4 - TEMPLATE
Secure randomness with os.urandom and secrets.
Fill in the sections marked TODO, then run with:
    python3 randomness.py

Useful documentation:
  os.urandom: https://docs.python.org/3/library/os.html#os.urandom
  secrets:    https://docs.python.org/3/library/secrets.html
  random:     https://docs.python.org/3/library/random.html
"""

import os
import secrets
import random


def main():
    # Part 1: os.urandom for a key and a nonce.
    # TODO: generate a 16-byte key and a 12-byte nonce with os.urandom,
    #       and print each as a hex string.
    key = os.urandom(16)
    nonce = os.urandom(12)
    print(key)
    print(nonce)

    # Part 2: secrets as an alternative.
    # TODO: generate a 16-byte secret with secrets
    #       and a hex string; print both.
    secret_bytes = secrets.token_bytes(16)
    secret_hex = secrets.token_hex(16)

    # Part 3: the random module (NOT for cryptographic use).
    # TODO: generate a value with the random module.
    rand = random.random()

    # Q4: two os.urandom calls should essentially never match.
    # TODO: call os.urandom twice and print whether the two results are equal.
    urandom_1 = os.urandom(16)
    urandom_2 = os.urandom(16)
    print("Do os.urandom calls match?:", urandom_1 == urandom_2)


if __name__ == "__main__":
    main()
