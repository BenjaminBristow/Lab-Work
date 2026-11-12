"""
Lab 5, Task 1, Questions 2 and 3 - TEMPLATE
Hashing fundamentals and collisions.
Fill in the sections marked TODO, then run with:
    python3 hashing.py

Useful documentation:
  hashlib: https://docs.python.org/3/library/hashlib.html
  (hashlib.sha256(data).hexdigest() gives a hex string;
   hashlib.sha256(data).digest() gives the raw 32 bytes;
   hashlib.md5(data).hexdigest() gives an MD5 hex digest.)
  os.urandom: https://docs.python.org/3/library/os.html#os.urandom
"""

import hashlib
import os


def sha256_hex(message: bytes) -> str:
    """Return the SHA-256 digest of a message as a hex string."""

    # TODO: return the SHA-256 digest of `message` as a hex string.
    return hashlib.sha256(message).hexdigest()


def main():
    # ---- Question 2: hashing fundamentals --------------------------------
    data = b"The quick brown fox!"
    
    # Part 1: test the function.
    hex_data = sha256_hex(data)
    print(hex_data)

    # Keep only the last 4 bytes of the raw digest and print them as hex.
    # TODO: take the raw SHA-256 digest of a message, slice the last 4 bytes,
    #       and print them as a hex string.
    rawsha256 = hashlib.sha256(data).digest()[-4:].hex()
    print(rawsha256)

    
    # Q1: avalanche effect - hash two messages differing by one character
    #     and compare the digests.
    # TODO: hash b"The quick brown fox" and b"The quick brown fox!" and print both.
    #bristowb@infc079tch034:~/Downloads/Python Files for Lab 5-20261105$ python3 hashing.py
    #5cac4f980fedc3d3f1f99b4be3472c9b30d56523e632d151237ec9309048bda9
    #9048bda9
    #bristowb@infc079tch034:~/Downloads/Python Files for Lab 5-20261105$ python3 hashing.py
    #0452ba1c161cc328e963fb7620324ef53ce1ee60b6455edd424450fbd7fe59b4
    #d7fe59b4


    # Q2: digest length is fixed regardless of input length.
    # TODO: print the length (in bytes) of the raw digest of a 5-byte message
    #       and of a 5000-byte message. (Hint: use .digest(), not .hexdigest().)
    len_short = len(hashlib.sha256(b"a"*5).digest())
    len_long = len(hashlib.sha256(b"a"*5001).digest())

    print(len_short)
    print(len_long)

    print(" ---- Question 3: collisions ------------------------------------------ ")
    # Part 1: try to find a SHA-256 collision by chance.
    # TODO: hash a large number of random inputs (e.g. os.urandom(8)),
    #       store the digests you have seen, and report whether any two
    #       different inputs produced the same digest.
    seen = {}
    collision_found = False

    for i in range(50000):
        rand_input = os.urandom(8)
        data = hashlib.sha256(rand_input).digest()
        if data in seen:
            if seen[data] != rand_input:
                print(f"Data collision detected!")
                print(f"Input 1: {seen[data].hex()}")
                print(f"Input 2: {rand_input.hex()}")
                print(f"Shared Hash: {data.hex()}")
                collision_found = True
                break
        else:
            seen[data] = rand_input

    if not collision_found:
        print("Collision detection finished. No collisions found")

    # Part 2: a known MD5 collision - two different strings, same MD5.
    s1 = b"TEXTCOLLBYfGiJUETHQ4hAcKSMd5zYpgqf1YRDhkmxHkhPWptrkoyz28wnI9V0aHeAuaKnak"
    s2 = b"TEXTCOLLBYfGiJUETHQ4hEcKSMd5zYpgqf1YRDhkmxHkhPWptrkoyz28wnI9V0aHeAuaKnak"
    
    # TODO: confirm the two strings are different.
    if s1 == s2:
        print("strings cannot be equal")
    else:
        # TODO: print the MD5 digest (hex) of each, and check whether they are equal.
        digest1 = hashlib.sha256(s1).hexdigest()
        digest2 = hashlib.sha256(s2).hexdigest()

        print(digest1)
        print(digest2)

        print("Are they equal?: ", digest1 == digest2)


if __name__ == "__main__":
    main()
