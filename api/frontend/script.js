const API_URL = "";

async function sendLog() {
    const log = document.getElementById("logInput").value;
    const resp = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({log})
    });
    const data = await resp.json();
    document.getElementById("taskId").value = data.task_id;
    alert("Task ID: " + data.task_id);
}

async function getStatus() {
    const taskId = document.getElementById("taskId").value;
    const resp = await fetch(`/status/${taskId}`);
    const data = await resp.json();
    document.getElementById("statusOutput").textContent = JSON.stringify(data, null, 2);
}

async function filterLog() {
    const taskId = document.getElementById("taskId").value;
    const level = document.getElementById("filterLevel").value;
    const keyword = document.getElementById("filterKeyword").value;
    const params = new URLSearchParams();
    if(level) params.append("level", level);
    if(keyword) params.append("keyword", keyword);

    const resp = await fetch(`/task/${taskId}/filter?` + params.toString());
    const data = await resp.json();

    const percent = data.total > 0
        ? ((data.count / data.total) * 100).toFixed(2)
        : 0;

    document.getElementById("filterCount").textContent =
        `Znaleziono: ${data.count} wpisów. Jest to ${percent}% wszystkich zgromadzonych logów`;

    document.getElementById("filterOutput").textContent = data.lines.join("\n");
}

function exportCSV() {
    const taskId = document.getElementById("taskId").value;
    window.location.href = `/task/${taskId}/export`;
}

const btn = document.getElementById("demo-btn");
const info = document.getElementById("task-info");


btn.addEventListener("click", async () => {
    info.textContent = "Generating logs...";
    try {
        const resp = await fetch("/generate_demo", { method: "POST" });
        const data = await resp.json();
        document.getElementById("taskId").value = data.task_id;
        info.textContent = `✅ Task ID: ${data.task_id}`;
        pollStatus(data.task_id);

        
        pollStatus(data.task_id);
    } catch (err) {
        info.textContent = "Error generating demo logs";
        console.error(err);
    }
});

async function pollStatus(taskId) {
    const statusElem = document.createElement("p");
    info.appendChild(statusElem);

    const interval = setInterval(async () => {
        const resp = await fetch(`/status/${taskId}`);
        if (!resp.ok) {
            statusElem.textContent = "Task not found";
            clearInterval(interval);
            return;
        }
        const data = await resp.json();
        statusElem.textContent = `Status: ${data.status} | Chunks: ${data.processed_chunks}/${data.total_chunks}`;

        if (data.status === "done") {
            clearInterval(interval);
            statusElem.textContent += " ✅ Done!";
        }
    }, 1000);
}