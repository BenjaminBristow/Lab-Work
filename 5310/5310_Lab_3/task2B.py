import threading
import time
import random

# Shared buffer and related synchronization primitives
BUFFER = []
MAX_SIZE = 5

lock = threading.Lock()
condition = threading.Condition(lock)

# Producer: generate items and add them to the buffer
def producer():
    for i in range(10):
        item = f"item-{i}"
        with condition:
            while len(BUFFER) >= MAX_SIZE:
                # Buffer full → wait for consumer to consume
                print(f"[producer] Buffer full ({len(BUFFER)}). Waiting...")
                condition.wait()

            BUFFER.append(item)
            print(f"[producer] produced {item} (size={len(BUFFER)})")
            condition.notify()  # wake one waiting consumer

        # Simulate time to produce next item
        time.sleep(random.uniform(0.2, 0.5))

    # Signal end of production
    with condition:
        print("[producer] Done producing. Signaling end.")
        BUFFER.append(None)  # sentinel for consumer to stop
        condition.notify_all()

# Consumer: remove items from the buffer and process them
def consumer(cid):
    while True:
        with condition:
            while not BUFFER:
                # Buffer empty → wait for producer to produce
                print(f"[consumer {cid}] Buffer empty. Waiting...")
                condition.wait()

            item = BUFFER.pop(0)
            if item is None:
                # Sentinel value → stop consuming
                BUFFER.insert(0, None)  # reinsert for other consumers
                print(f"[consumer {cid}] Stopping (received sentinel).")
                condition.notify_all()
                break

            print(f"[consumer {cid}] consumed {item} (size={len(BUFFER)})")
            condition.notify()  # wake waiting producer if buffer was full

        # Simulate time to process the item
        time.sleep(random.uniform(0.3, 0.7))

def main():
    num_consumers = 2

    t_producer = threading.Thread(target=producer)
    consumers = [threading.Thread(target=consumer, args=(cid,)) for cid in range(num_consumers)]

    # Start all threads
    t_producer.start()
    for t in consumers: t.start()

    # Wait for threads to finish
    t_producer.join()
    for t in consumers: t.join()

    print("\n[main] All threads finished.")

if __name__ == "__main__":
    main()