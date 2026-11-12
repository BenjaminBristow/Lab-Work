"""
Lab 5, Task 1, Question 1 - TEMPLATE
Encodings: bytes, UTF-8, hex and base64.
Fill in the sections marked TODO, then run with:
    python3 cryptography_basic_functions.py

Useful documentation:
  base64:  https://docs.python.org/3/library/base64.html
  bytes.hex(): https://docs.python.org/3/library/stdtypes.html#bytes.hex
  str.encode / bytes.decode:
    https://docs.python.org/3/library/stdtypes.html#str.encode
"""

import base64


# --- Helper functions (Question 1, part 3) -------------------------------
def b64e(data: bytes) -> str:
    """Encode bytes as a base64 text string."""
    # TODO: return the base64 encoding of `data` as a str.
    pass


def b64d(text: str) -> bytes:
    """Decode a base64 text string back to bytes."""
    # TODO: return the bytes that `text` base64-decodes to.
    pass


def main():
    # Part 1: text <-> bytes with UTF-8.
    message = input("Enter a message: ")
    
    # TODO: convert `message` (a str) to bytes using UTF-8.
    message_bytes = message.encode('utf-8')

    # TODO: print the bytes and their length.
    print(len(message_bytes), message_bytes)

    # TODO: convert the bytes back to a str and check it equals `message`.
    decoded_message = message_bytes.decode('utf-8')
    if decoded_message == message:
        print("message correctly decoded")

    # Part 2: show bytes as hex and as base64.
    data = b"\x00\x10\xff\x42"

    # TODO: print `data` as a hex string.
    hex_data = data.hex()
    print(hex_data)

    # TODO: print `data` as a base64 string (use b64e).
    b64_data = base64.b64encode(data)
    print(b64_data)

    # Part 3: round-trip some bytes through the helpers.
    # TODO: pick some bytes, encode then decode them with b64e/b64d,
    #       and check you recover the original.

    pass  # TODO: remove this once you have added your code above


if __name__ == "__main__":
    main()
