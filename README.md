## Lab-Work

Lab work from my Computer Science labs at Lancaster University. This page is a contents list for everything in the repo.

## Contents

- [5310](#5310)
  - [Lab 2: Processes](#5310-lab-2-processes)
  - [Lab 3: Pipes, Threads and Synchronisation](#5310-lab-3-pipes-threads-and-synchronisation)
  - [Lab 4: Networking with Mininet](#5310-lab-4-networking-with-mininet)
  - [Lab 5: Sockets and Echo Servers](#5310-lab-5-sockets-and-echo-servers)
- [5510](#5510)
  - [Lab 5: Cryptography Basics](#5510-lab-5-cryptography-basics)
  - [Lab 6: Symmetric Encryption and Messaging](#5510-lab-6-symmetric-encryption-and-messaging)

---

## 5310

### 5310 Lab 2: Processes

Folder: [`5310/5310_Lab_2`](5310/5310_Lab_2)

- [`infinite_loop.py`](5310/5310_Lab_2/infinite_loop.py) - loop that prints its PID every second, with a SIGINT handler
- [`memory_isolation.py`](5310/5310_Lab_2/memory_isolation.py) - uses `fork()` to show a child process gets its own copy of memory
- [`prime.py`](5310/5310_Lab_2/prime.py) - counts primes in a range, split across a number of processes given on the command line
- [`zombie.py`](5310/5310_Lab_2/zombie.py) - creates a zombie process by delaying the parent's `wait()`

### 5310 Lab 3: Pipes, Threads and Synchronisation

Folder: [`5310/5310_Lab_3`](5310/5310_Lab_3)

- [`task1A.py`](5310/5310_Lab_3/task1A.py) - writing data through a pipe in chunks, pipe capacity and broken pipe handling
- [`task1B.py`](5310/5310_Lab_3/task1B.py) - parent process monitoring several child pipes with `select()`
- [`task2A.py`](5310/5310_Lab_3/task2A.py) - threads and a queue handling simulated I/O waits plus a small CPU step
- [`task2B.py`](5310/5310_Lab_3/task2B.py) - producer/consumer with a bounded buffer using a lock and condition variable
- [`hacker_primes_threadpool.py`](5310/5310_Lab_3/hacker_primes_threadpool.py) - hacker edition: a hand-written thread pool used to count primes
- [`week3-solution/`](5310/5310_Lab_3/week3-solution) - solution folder for this week

### 5310 Lab 4: Networking with Mininet

Folder: [`5310/5310_Lab_4`](5310/5310_Lab_4)

- [`topology.py`](5310/5310_Lab_4/topology.py) - Mininet topology with two hosts connected through one switch
- [`Makefile`](5310/5310_Lab_4/Makefile) - `make topo` starts the topology, `make clean` resets Mininet
- [`index.html`](5310/5310_Lab_4/index.html) - small web page fetched over HTTP between the hosts
- [`part1-http.pcapng`](5310/5310_Lab_4/part1-http.pcapng) - packet capture of the HTTP request (Part 1)
- [`part3.1-ping.pcapng`](5310/5310_Lab_4/part3.1-ping.pcapng) - packet capture of ping traffic (Part 3.1)
- [`week4-solution/`](5310/5310_Lab_4/week4-solution) - solution folder for this week

### 5310 Lab 5: Sockets and Echo Servers

Folder: [`5310/5310_Lab_5`](5310/5310_Lab_5)

Stage 1 - TCP echo service
- [`echo_server.py`](5310/5310_Lab_5/echo_server.py) - TCP echo server using `select()` to handle multiple clients
- [`echo_client.py`](5310/5310_Lab_5/echo_client.py) - interactive client that sends typed messages to the server

Stage 2 - binary protocol with `struct`
- [`struct_echo_server.py`](5310/5310_Lab_5/struct_echo_server.py) - echo server using a fixed-size binary packet (type, sequence number, timestamps, 32-byte message)
- [`struct_echo_client.py`](5310/5310_Lab_5/struct_echo_client.py) - matching client

Hacker's Edition
- [`hacker_echo_server.py`](5310/5310_Lab_5/hacker_echo_server.py) - echo server with a header plus variable-length payload
- [`hacker_echo_client.py`](5310/5310_Lab_5/hacker_echo_client.py) - matching client, including a `recv_exact` helper

Supporting files
- [`topology.py`](5310/5310_Lab_5/topology.py) - Mininet topology with four hosts and a Linux router node
- [`Makefile`](5310/5310_Lab_5/Makefile) - `make topo` starts the network, `make test` runs the tests, `make clean` resets Mininet
- [`tests/`](5310/5310_Lab_5/tests) - pytest files for each client, server and the topology

---

## 5510

### 5510 Lab 5: Cryptography Basics

Folder: [`5510/5510_Lab_5`](5510/5510_Lab_5)

- [`cryptography_basic_functions.py`](5510/5510_Lab_5/cryptography_basic_functions.py) - bytes, UTF-8, hex and base64 encodings
- [`hashing.py`](5510/5510_Lab_5/hashing.py) - SHA-256 and MD5 hashing, and collisions
- [`randomness.py`](5510/5510_Lab_5/randomness.py) - secure randomness with `os.urandom` and `secrets`, compared with `random`
- [`cryptography_library.py`](5510/5510_Lab_5/cryptography_library.py) - generating, storing and using an Ed25519 key pair to sign and verify
- [`one_time_pad.py`](5510/5510_Lab_5/one_time_pad.py) - stretch task: one-time pad with XOR and why a key must never be reused

### 5510 Lab 6: Symmetric Encryption and Messaging

Folder: [`5510/5510_Lab_6`](5510/5510_Lab_6)

- [`symmetric_walkthrough.py`](5510/5510_Lab_6/symmetric_walkthrough.py) - AES-GCM and ChaCha20-Poly1305 encryption with the `cryptography` library
- [`json_and_messages.py`](5510/5510_Lab_6/json_and_messages.py) - working with JSON and packaging an encrypted message into an envelope
- [`echo_server.py`](5510/5510_Lab_6/echo_server.py) - provided mailbox server (`POST /send`, `GET /receive`)
- [`send_client.py`](5510/5510_Lab_6/send_client.py) - client that sends an encrypted envelope to the server

---

## Running the code

- 5310 Lab 2 and 3: run with `python3 <file>.py`
- 5310 Lab 4 and 5: need Mininet, run `make topo` in the lab folder
- 5310 Lab 5 tests: `make test`
- 5510 Lab 5 and 6: need the `cryptography` package (`pip install cryptography`), and `requests` for `send_client.py`
- 5510 Lab 6 client and server: start `echo_server.py` in one terminal, then run `send_client.py` in another

## Licence

MIT, see [`LICENSE`](LICENSE).