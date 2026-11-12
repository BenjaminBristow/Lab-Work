"""
Lab 6, Task 3 - TEMPLATE (the client you complete).
First run the provided server in one terminal:
    python3 echo_server.py
Then run this in another:
    python3 send_client.py

Documentation: https://requests.readthedocs.io/en/latest/user/quickstart/
"""

import requests
from json_and_messages import make_envelope, open_envelope
import json

SERVER = "http://localhost:8000"


def main():
    # TODO: Make an encrypted envelope using your Task 2 code.
    envelope = make_envelope("Hurray!")

    # TODO: POST the envelope to SERVER + "/send". The envelope is already a
    #       JSON string, so send it as the request body (data=envelope) with a
    #       "Content-Type: application/json" header. Print the response.
    r = requests.post(
        SERVER + "/send", 
        data=envelope, 
        headers={"Content-Type": "application/json"}
        )
    print("r: ", r, "\n",
          "r.status_code: ", r.status_code, "\n",
          "r.text: ", r.text,"\n",
          "r.json: ", r.json())
    
    # TODO: GET SERVER + "/receive" and read the list of messages from the
    #       JSON response (the server returns {"messages": [...]}).
    r = requests.get(
        SERVER + "/receive"
    )
    print("\n Response \n")
    print(r.text)

    recovered = json.loads(r.text)
    for message in recovered.get("messages"):
        # TODO: decrypt the envelope you got back with open_envelope and print it.
        print(open_envelope(message))




if __name__ == "__main__":
    main()
