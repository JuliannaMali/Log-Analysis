import uuid
import json
from fastapi import FastAPI
from pydantic import BaseModel
import redis

app = FastAPI()
r = redis.Redis(host="redis", port=6379, decode_responses=True)

CHUNK_SIZE = 30


class LogRequest(BaseModel):
    log: str


@app.post("/analyze")
def analyze_log(req: LogRequest):
    task_id = str(uuid.uuid4())
    lines = req.log.splitlines()

    chunks = [
        lines[i:i + CHUNK_SIZE]
        for i in range(0, len(lines), CHUNK_SIZE)
    ]

    r.hset(f"task:{task_id}", mapping={
        "status": "processing",
        "total_chunks": len(chunks),
        "processed_chunks": 0,
        "next_chunk_id": 0,   
        "errors": 0,
        "warnings": 0,
        "infos": 0,
        "words": json.dumps({})
    })


    for chunk in chunks:
        r.rpush("log_queue", json.dumps({
            "task_id": task_id,
            "lines": chunk
        }))

    return {"task_id": task_id}


@app.get("/status/{task_id}")
def get_status(task_id: str):
    data = r.hgetall(f"task:{task_id}")
    chunks = r.hgetall(f"task:{task_id}:chunks")

    by_worker = {}
    for raw in chunks.values():
        info = json.loads(raw)
        w = info["worker"]
        by_worker[w] = by_worker.get(w, 0) + 1

    if not data:
        return {"error": "task not found"}

    words = json.loads(data["words"])

    return {
        "by_worker": by_worker,
        "status": data["status"],
        "processed_chunks": int(data["processed_chunks"]),
        "total_chunks": int(data["total_chunks"]),
        "errors": int(data["errors"]),
        "warnings": int(data["warnings"]),
        "infos": int(data["infos"]),
        "top_words": dict(sorted(words.items(), key=lambda x: x[1], reverse=True)[:5])
    }