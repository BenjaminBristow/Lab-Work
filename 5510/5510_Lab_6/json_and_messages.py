"""
Lab 6, Task 2 - TEMPLATE
Working with JSON, and packaging an encrypted message.
Fill in the sections marked TODO, then run with:
    python3 json_and_messages.py

Documentation:
  json:   https://docs.python.org/3/library/json.html
  AESGCM: https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM
  base64 was introduced in Lab 5 (b64e / b64d below).
"""

import base64
import json
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"), validate=True)


# A shared key, hardcoded into both sender and receiver (this lab only).
SHARED_KEY = bytes.fromhex("00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")


# --- Q3: encrypted envelope -----------------------------------------
def make_envelope(message: str) -> str:
    """Encrypt a message and bundle the nonce and ciphertext into a JSON string."""
    # TODO: create a fresh nonce; encrypt `message` with AES-GCM under SHARED_KEY.
    aesgcm = AESGCM(SHARED_KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)

    # TODO: build a dict with the nonce and ciphertext, each base64-encoded (b64e),
    #       and return it as a JSON string (json.dumps).
    envelope = {
        "nonce": b64e(nonce),
        "ciphertext": b64e(ciphertext),
    }
    return json.dumps(envelope)

# --- Q3: encrypted envelope -----------------------------------------
def open_envelope(envelope: str) -> str:
    """Parse a JSON envelope, decrypt it, and return the message."""
    # TODO: parse the JSON (json.loads); b64d the nonce and ciphertext; decrypt
    #       with AES-GCM; return the message as a str.
    aesgcm = AESGCM(SHARED_KEY)
    data = json.loads(envelope)
    nonce = b64d(data.get("nonce"))
    ciphertext = b64d(data.get("ciphertext"))
    bytes_result = aesgcm.decrypt(nonce, ciphertext, None)
    return bytes_result.decode('utf-8')

def main():
    print("\n  --- Q1: dict <-> JSON string --------------------------------------- \n")
    d = {"from": "alice", "to": "bob", "count": 3}
    # TODO: turn d into a JSON string (json.dumps) and print it; parse it back
    #       (json.loads) and print one of the values.
    string = json.dumps(d)
    print(string, type(string))

    jsonfile = json.loads(string)
    print(jsonfile["from"], type(jsonfile["from"]), "in", type(jsonfile))

    print("\n --- Q2: bytes need base64 before they can go in JSON ----------------\n")
    raw = os.urandom(8)
    # TODO: try json.dumps({"key": raw}) inside try/except TypeError to see it
    #       fail, and explain why in a comment.
    try: 
        json.dumps({"key": raw})
    except TypeError:
        print("type error occured") # json cannot do raw bytes therefore it needs to be b64 encoded

    # TODO: base64-encode the bytes (b64e), put THAT in a dict, dump to JSON,
    #       load it back, and b64d the value to recover the original bytes.
    dump = json.dumps({"key": b64e(raw)})
    load = json.loads(dump)
    raw_result = b64d(load.get("key"))
    print(raw_result)

    print("\n --- Q3: encrypted envelope -----------------------------------------\n")
    message = "Meet me at the north gate at noon."
    # TODO: make an envelope with make_envelope, print it, recover it with
    #       open_envelope, and check the message is unchanged.
    envelope = make_envelope(message)
    print(envelope)
    opened_envelope = open_envelope(envelope)
    print(opened_envelope)

    print("\n --- Q4 [Stretch]: nested dicts and missing fields ------------------\n")
    # TODO: build a dict that CONTAINS another dict, convert to JSON and back,
    #       read a value from the inner dict, and use .get("field", default)
    #       to read a field that is not present without crashing.
    nested_dict = {
        "inner_dict": {
            "test": "hurray!"
        }
    }

    jsonfile = json.dumps(nested_dict)
    recovered = json.loads(jsonfile)
    print(recovered.get("inner_dict").get("test"))

    print("\n  --- Q5 [Stretch]: tampering is detected ----------------------------\n")
    # TODO: take a valid envelope, change one character of its base64
    #       ciphertext, and try to open_envelope it inside try/except InvalidTag.
    message = "Meet me at the north gate at noon."
    envelope = make_envelope(message)

    data = json.loads(envelope)
    ct = data["ciphertext"]  
    tampered_char = "B" if ct[0] == "A" else "A"
    data["ciphertext"] = tampered_char + ct[1:]
    tampered_envelope = json.dumps(data)

    try:
        result = open_envelope(tampered_envelope)
        print(result)
    except InvalidTag:
        print("InvalidTag error detected")


if __name__ == "__main__":
    main()
