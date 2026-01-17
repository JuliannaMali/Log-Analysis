import os
import uuid
import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import redis
import random
from data import generate_logs


app = FastAPI()

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")


r = redis.Redis(host="redis", port=6379, decode_responses=True)

CHUNK_SIZE = 30
LOG_LEVELS = ["INFO", "ERROR", "WARNING", "DEBUG", "CRITICAL"]

class LogRequest(BaseModel):
    log: str

@app.get("/")
def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))



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
        **{lvl.lower(): 0 for lvl in LOG_LEVELS},
        "words": json.dumps({}),
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
    if not data:
        return {"error": "task not found"}

    words = json.loads(data.get("words", "{}"))
    workers = r.hgetall(f"task:{task_id}:workers")

    def safe_int(val):
        try:
            return int(val)
        except (TypeError, ValueError):
            return 0

    log_levels = {lvl.lower(): safe_int(data.get(lvl.lower())) for lvl in LOG_LEVELS}

    return {
        "status": data.get("status", "unknown"),
        "processed_chunks": safe_int(data.get("processed_chunks")),
        "total_chunks": safe_int(data.get("total_chunks")),
        **log_levels,
        "top_words": dict(sorted(words.items(), key=lambda x: x[1], reverse=True)[:10]),
        "by_worker": {k: safe_int(v) for k, v in workers.items()}
    }

@app.get("/task/{task_id}/filter")
def filter_logs(task_id: str, level: str | None = None, keyword: str | None = None):
    logs = r.lrange(f"task:{task_id}:logs", 0, -1)
    total = len(logs)
    if not logs:
        return {"lines": []}

    result = []

    for line in logs:
        if level and level not in line:
            continue
        if keyword and keyword.lower() not in line.lower():
            continue
        result.append(line)

    return {
        "count": len(result),
        "total": total,
        "lines": result
    }


@app.post("/generate_demo")
def generate_demo_logs():
    task_id = str(uuid.uuid4())
    lines = generate_logs(5000)

    counts = {lvl.lower(): 0 for lvl in LOG_LEVELS}
    words = {}

    for line in lines:
        for lvl in LOG_LEVELS:
            if line.startswith(lvl):
                counts[lvl.lower()] += 1
                break
        for word in line.split():
            word = word.lower()
            words[word] = words.get(word, 0) + 1

    chunks = [lines[i:i + CHUNK_SIZE] for i in range(0, len(lines), CHUNK_SIZE)]

    workers = {}
    num_workers = 3
    for i, chunk in enumerate(chunks):
        worker_id = f"worker-{i % num_workers}"
        workers[worker_id] = workers.get(worker_id, 0) + len(chunk)

    r.hset(f"task:{task_id}", mapping={
        "status": "done",
        "total_chunks": len(chunks),
        "processed_chunks": len(chunks),
        **counts,
        "words": json.dumps(words)
    })

    r.hset(f"task:{task_id}:workers", mapping=workers)

    for line in lines:
        r.rpush(f"task:{task_id}:logs", line)

    return {"task_id": task_id}


@app.get("/task/{task_id}/export")
def export_csv(task_id: str):
    logs = r.lrange(f"task:{task_id}:logs", 0, -1)
    if not logs:
        return Response("No logs", status_code=404)

    csv_content = "level,message\n"
    for line in logs:
        if " " in line:
            level, msg = line.split(" ", 1)
        else:
            level, msg = line, ""
        csv_content += f"{level},{msg}\n"

    return Response(
        csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={task_id}.csv"
        }
    )
