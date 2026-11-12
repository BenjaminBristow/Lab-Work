"""
Lab 5, Task 3 [Stretch] - TEMPLATE
One-Time Pad with XOR, and why a key must never be reused.
Fill in the sections marked TODO, then run with:
    python3 one_time_pad.py

Useful documentation:
  os.urandom: https://docs.python.org/3/library/os.html#os.urandom
  One-Time Pad: https://en.wikipedia.org/wiki/One-time_pad

Hint: to XOR two equal-length byte strings a and b:
    bytes(x ^ y for x, y in zip(a, b))
"""

import os


def xor(a: bytes, b: bytes) -> bytes:
    """XOR two equal-length byte strings together."""
    # TODO: return the byte-by-byte XOR of a and b.
    pass


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    # TODO: OTP encryption is XOR of plaintext and key.
    pass


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    # TODO: OTP decryption is XOR of ciphertext and key.
    pass


def main():
    # Q2: basic OTP round-trip with a fresh random key.
    # TODO: encode a message to bytes, generate a key the same length with
    #       os.urandom, encrypt, decrypt, and check you recover the message.

    # Q3: reuse the SAME key for two different messages of equal length.
    # TODO: encrypt two different same-length messages m1 and m2 with one key.
    # TODO: XOR the two ciphertexts together and show the result equals m1 XOR m2
    #       (the key cancels out - you did not need it).
    # TODO: assuming you know m1, recover m2 from the two ciphertexts alone.

    pass  # TODO: remove this once you have added your code above


if __name__ == "__main__":
    main()
