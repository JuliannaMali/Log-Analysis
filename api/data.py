import random

API_URL = "http://localhost:8000"

levels = ["INFO", "ERROR", "WARNING", "DEBUG", "CRITICAL"]
weights = [50, 10, 20, 15, 5]
events = [
    "user login",
    "user logout",
    "disk full",
    "disk almost full",
    "memory low",
    "service restarted",
    "service stopped unexpectedly",
    "connection timeout",
    "permission denied",
    "file not found",
    "database connection failed",
    "authentication failed",
    "invalid input",
    "configuration error",
    "timeout while processing request",
    "failed to send email",
    "resource limit exceeded",
    "network unreachable",
    "API rate limit exceeded",
    "failed to load module",
    "cache miss",
    "session expired",
    "unsupported operation",
    "data corruption detected",
    "unexpected shutdown",
    "service unavailable",
    "out of memory",
    "access violation",
    "failed to write file",
    "invalid credentials",
    "transaction rollback",
    "dependency not found",
    "process killed",
    "hardware failure detected",
    "user password changed",
    "session ended",
    "invalid token",
    "permission updated",
    "file download failed",
    "disk quota exceeded",
    "network latency high",
    "connection refused",
    "port blocked",
    "SSL certificate expired",
    "SSL handshake failed",
    "DNS resolution failed",
    "service restart failed",
    "user account locked",
    "memory leak detected",
    "process ended",
    "CPU usage high",
    "disk I/O high",
    "log rotation failed",
    "backup failed",
    "restore failed",
    "configuration mismatch",
    "deprecated API used",
    "connection closed",
    "heartbeat missed",
    "cache cleared",
    "database query failed",
    "data migration started",
    "data migration failed",
    "email queued",
    "email failed",
    "file deleted",
    "file moved",
    "file permission changed",
    "cron job failed",
    "user profile deleted",
    "token revoked",
    "API response sent",
    "memory allocation failed",
    "resource cleaned up",
    "service health check failed"
]

def generate_logs(n=55000):
    return [
        f"{random.choices(levels, weights=weights)[0]} {random.choice(events)}"
        for _ in range(n)
    ]


if __name__ == "__main__":
    logs = generate_logs()
    print("\n".join(logs))

