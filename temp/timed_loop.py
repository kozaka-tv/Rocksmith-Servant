from time import time

HEARTBEAT = 2
MAX_COUNT = 3

print("begin timer")
measure1 = time()

count = 1
print(str(count) + " - " + str(measure1) + " timer started")

while count < MAX_COUNT:
    if time() - measure1 >= HEARTBEAT:
        measure1 = time()
        count += 1
        print(str(count) + " - " + str(measure1) + " " + str(HEARTBEAT) + " seconds gone...")

print("done")
