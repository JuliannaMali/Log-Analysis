import json
import time
import redis
import re
import os
import socket

WORKER_ID = f"{socket.gethostname()}-{os.getpid()}"

r = redis.Redis(host="redis", port=6379, decode_responses=True)

WORD_RE = re.compile(r"\b\w+\b")


def process_chunk(lines):
    errors = sum(1 for l in lines if "ERROR" in l)
    warnings = sum(1 for l in lines if "WARNING" in l)
    infos = sum(1 for l in lines if "INFO" in l)

    word_count = {}
    for line in lines:
        for word in WORD_RE.findall(line.lower()):
            word_count[word] = word_count.get(word, 0) + 1

    return errors, warnings, infos, word_count


while True:
    result = r.blpop("log_queue", timeout=0)
    if result is None:
        continue

    _, raw = result
    task = json.loads(raw)

    task_id = task["task_id"]
    lines = task["lines"]

    chunk_id = r.hincrby(f"task:{task_id}", "next_chunk_id", 1)

    r.hset(
        f"task:{task_id}:chunks",
        chunk_id,
        json.dumps({
            "worker": WORKER_ID,
            "lines": len(lines)
        })
    )

    print(f"[{WORKER_ID}] processing chunk {chunk_id} for task {task_id}")

    errors, warnings, infos, words = process_chunk(lines)

    with r.pipeline() as pipe:
        pipe.hincrby(f"task:{task_id}", "errors", errors)
        pipe.hincrby(f"task:{task_id}", "warnings", warnings)
        pipe.hincrby(f"task:{task_id}", "infos", infos)
        pipe.hincrby(f"task:{task_id}", "processed_chunks", 1)

        current_words = json.loads(r.hget(f"task:{task_id}", "words"))
        for w, c in words.items():
            current_words[w] = current_words.get(w, 0) + c

        pipe.hset(f"task:{task_id}", "words", json.dumps(current_words))
        pipe.execute()

    processed = int(r.hget(f"task:{task_id}", "processed_chunks"))
    total = int(r.hget(f"task:{task_id}", "total_chunks"))

    if processed == total:
        r.hset(f"task:{task_id}", "status", "done")

    time.sleep(0.05)
