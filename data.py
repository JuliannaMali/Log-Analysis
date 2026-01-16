import json
import time
import urllib.request
import urllib.error

API_URL = "http://localhost:8000"

import random
levels = ["INFO", "ERROR", "WARNING", "DEBUG", "CRITICAL"]
events = ["something happened", "user login", "disk full", "memory low", "service restarted"]

log = "\n".join(f"{random.choice(levels)} {random.choice(events)}" for _ in range(1500))


data = json.dumps({"log": log}).encode("utf-8")

req = urllib.request.Request(
    f"{API_URL}/analyze",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode())

task_id = result["task_id"]
print(f"✅ Task ID: {task_id}\n")

while True:
    try:
        with urllib.request.urlopen(f"{API_URL}/status/{task_id}") as resp:
            status = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print("Błąd:", e)
        break

    print(
        f"status={status['status']} | "
        f"chunks={status['processed_chunks']}/{status['total_chunks']} | "
        f"errors={status['errors']} | "
        f"warnings={status['warnings']} | "
        f"infos={status['infos']}"
    )

    if "by_worker" in status:
        print("  workers:")
        for w, c in status["by_worker"].items():
            print(f"    {w}: {c} chunk(s)")


    if status["status"] == "done":
        print("\nZAKOŃCZONE")
        print("Top words:", status["top_words"])
        break

    time.sleep(1)
