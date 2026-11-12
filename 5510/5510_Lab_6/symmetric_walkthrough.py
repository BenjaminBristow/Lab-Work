"""
Lab 6, Task 1 - TEMPLATE
Symmetric encryption basics with the cryptography library.
Fill in the sections marked TODO, then run with:
    python3 symmetric_walkthrough.py

Documentation:
  AESGCM:           https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM
  ChaCha20Poly1305: https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305


def main():
    message = "Attack at dawn".encode("utf-8")   # text -> bytes (UTF-8, from Lab 5)

    print("\n --- Q1: AES-GCM ----------------------------------------------------- \n")
    # TODO: generate a 256-bit AES-GCM key (AESGCM.generate_key).
    key = AESGCM.generate_key(bit_length = 256)

    # TODO: create a fresh 12-byte nonce with os.urandom.
    nonce = os.urandom(12)

    # TODO: make an AESGCM object, encrypt `message` (associated data = None),
    #       print the ciphertext as hex, then decrypt and print the text.
    aesgcm = AESGCM(key)
    cyphertext = aesgcm.encrypt(nonce, message, None)
    print(cyphertext.hex())
    result = aesgcm.decrypt(nonce, cyphertext, None)
    print(result.decode("utf-8"))

    print("\n --- Q2: ChaCha20-Poly1305 ------------------------------------------ \n")
    # TODO: do the same as Q1 with ChaCha20Poly1305 (generate_key, a fresh
    #       12-byte nonce, encrypt, decrypt) and print the recovered text.
    key = ChaCha20Poly1305.generate_key()
    nonce = os.urandom(12)
    chacha = ChaCha20Poly1305(key)
    cyphertext = chacha.encrypt(nonce, message, None)
    print(cyphertext.hex())
    result = chacha.decrypt(nonce, cyphertext, None)
    print(result.decode('utf-8'))

    print("\n --- Q3: why the nonce matters -------------------------------------- \n")
    m = "same message".encode("utf-8")

    # TODO: encrypt m TWICE with DIFFERENT fresh nonces and print both ciphertexts.
    key = AESGCM.generate_key(bit_length = 256)
    aesgcm = AESGCM(key)

    nonce = os.urandom(12)
    cyphertext = aesgcm.encrypt(nonce, m, None)
    print("cypher1: ", cyphertext.hex())

    nonce = os.urandom(12)
    cyphertext2 = aesgcm.encrypt(nonce, m, None)
    print("cypher2: ", cyphertext2.hex())


    # TODO: encrypt m TWICE with the SAME nonce and print both.
    # Then answer the questions in the worksheet.
    print("\n")
    key = AESGCM.generate_key(bit_length = 256)
    aesgcm = AESGCM(key)

    nonce = os.urandom(12)
    cyphertext = aesgcm.encrypt(nonce, m, None)
    print("cypher1: ", cyphertext.hex())

    cyphertext2 = aesgcm.encrypt(nonce, m, None)
    print("cypher2: ", cyphertext2.hex())

    print("\n --- Q4 [Stretch]: brute-force time for a 128-bit key --------------- \n")
    # TODO: assuming 10**9 keys per second, compute how long it would take to
    #       try all 2**128 keys, and print the result in years.

    speed = 10**9
    amount = 2**128
    time = amount/speed/60/60/24/365
    print(time)


if __name__ == "__main__":
    main()
