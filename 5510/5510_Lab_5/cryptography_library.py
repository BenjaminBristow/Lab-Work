"""
Lab 5, Task 2 - TEMPLATE
Generating, storing and using an Ed25519 key pair.
Fill in the sections marked TODO, then run with:
    python3 cryptography_library.py

Useful documentation:
  Ed25519 signing:
    https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
  Key serialization (private_bytes / public_bytes, Raw encoding):
    https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/
  Exceptions (InvalidSignature):
    https://cryptography.io/en/latest/exceptions/
"""

import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey)


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"), validate=True)


def main():
    # Q1: generate an Ed25519 key pair (a private key and its public key).
    # TODO: create the private key, then obtain the public key from it.

    # Q2: export the private key's raw bytes and print them and their length.
    # TODO: use priv.private_bytes(Encoding.Raw, PrivateFormat.Raw,
    #       NoEncryption()).  How many bytes is it?

    # Q3: base64-encode the private key bytes to text, decode back, and rebuild
    #     the key with Ed25519PrivateKey.from_private_bytes(...).
    # TODO: show the reloaded key matches the original (e.g. same public bytes).

    # Q4: export the public key's raw bytes, then rebuild a public key object
    #     with Ed25519PublicKey.from_public_bytes(...).
    # TODO.

    # Q5: encode a message to bytes and sign it with priv.sign(message).
    #     Print the signature as base64 and print its length.
    # TODO.

    # Q6: verify the signature against the message with pub.verify(sig, message).
    #     Print whether verification succeeded. (verify raises InvalidSignature
    #     on failure, so use try/except.)
    # TODO.

    # Q7: verify the SAME signature against a CHANGED message. Print whether it
    #     was accepted or rejected.
    # TODO.

    # Q8: generate a second key pair and try to verify your signature with the
    #     new public key. Print whether it was accepted or rejected.
    # TODO.

    # Q9 [Stretch]: write encode_fields(label, *fields) that length-prefixes
    #     each field, sign encode_fields("transfer", "alice", "bob", "100"),
    #     verify it, and show ("ab","c") and ("a","bc") give different bytes.
    # TODO.

    pass  # TODO: remove this once you have added your code above


if __name__ == "__main__":
    main()
