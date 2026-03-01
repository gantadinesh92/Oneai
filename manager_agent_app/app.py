from __future__ import annotations

import os
import random
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

ROLE_DEFAULTS = ["Data Engineer", "Scrum Master", "Data Scientist", "Software Engineer"]
STATUS_TODO = "todo"
STATUS_IN_PROGRESS = "in_progress"
STATUS_BLOCKED = "blocked"
STATUS_DONE = "done"


@dataclass
class SubAgent:
    id: str
    role: str
    active_task_id: Optional[str] = None


@dataclass
class Task:
    id: str
    title: str
    description: str
    role: str
    status: str = STATUS_TODO
    assignee_id: Optional[str] = None
    progress: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    history: List[str] = field(default_factory=list)


class ManagerAgent:
    def __init__(self, poll_interval_seconds: int = 5) -> None:
        self.poll_interval_seconds = poll_interval_seconds
        self.objective = ""
        self.sub_agents: Dict[str, SubAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.chat: List[Dict[str, str]] = []
        self._lock = threading.Lock()

        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    def set_objective(self, objective: str, roles: Optional[List[str]] = None) -> Dict[str, str]:
        with self._lock:
            self.objective = objective.strip()
            self.sub_agents.clear()
            self.tasks.clear()
            selected_roles = roles or ROLE_DEFAULTS

            for role in selected_roles:
                sub_id = str(uuid.uuid4())[:8]
                self.sub_agents[sub_id] = SubAgent(id=sub_id, role=role)

            for role in selected_roles:
                task_id = str(uuid.uuid4())[:8]
                title, description = self._role_task(role, self.objective)
                self.tasks[task_id] = Task(
                    id=task_id,
                    title=title,
                    description=description,
                    role=role,
                    history=[f"Task created for {role}"],
                )

            self.chat.append({"speaker": "manager", "text": f"Objective received: {self.objective}"})
            return {"message": f"Created {len(self.tasks)} tasks for {len(self.sub_agents)} sub-agents."}

    def _role_task(self, role: str, objective: str) -> tuple[str, str]:
        key = role.lower()
        if "scrum" in key:
            return (
                "Plan and track sprint",
                f"Create board, ceremonies, and dependency tracking for: {objective}",
            )
        if "data engineer" in key:
            return (
                "Build data ingestion and transformations",
                f"Implement data pipelines required for: {objective}",
            )
        if "data scientist" in key:
            return (
                "Create model experiments and analysis",
                f"Run experiments and KPI reporting for: {objective}",
            )
        if "software engineer" in key:
            return (
                "Build service components",
                f"Implement APIs, app logic, and integrations for: {objective}",
            )
        return (f"Deliver {role} workstream", f"Complete {role} tasks for: {objective}")

    def set_interval(self, interval_seconds: int) -> Dict[str, str]:
        with self._lock:
            self.poll_interval_seconds = max(2, min(interval_seconds, 600))
            return {"message": f"Polling set to {self.poll_interval_seconds} seconds."}

    def receive_chat(self, message: str) -> Dict[str, str]:
        with self._lock:
            self.chat.append({"speaker": "user", "text": message})
            reply = "Acknowledged. I will monitor progress, unblock issues, and keep the dashboard updated."
            self.chat.append({"speaker": "manager", "text": reply})
            return {"message": reply}

    def tick(self) -> None:
        with self._lock:
            for task in self.tasks.values():
                if task.status == STATUS_DONE:
                    continue
                if task.assignee_id is None:
                    self._assign_task(task)
                    task.updated_at = datetime.now(timezone.utc).isoformat()
                    continue

                if task.status == STATUS_TODO:
                    task.status = STATUS_IN_PROGRESS
                    task.progress = random.randint(5, 18)
                    task.history.append("Started")
                elif task.status == STATUS_IN_PROGRESS:
                    if random.random() < 0.1:
                        task.status = STATUS_BLOCKED
                        task.history.append("Blocked: awaiting input/dependency")
                    else:
                        task.progress = min(100, task.progress + random.randint(12, 28))
                        task.history.append(f"Progress {task.progress}%")
                        if task.progress >= 100:
                            task.status = STATUS_DONE
                            task.history.append("Completed")
                            assignee = self.sub_agents.get(task.assignee_id)
                            if assignee:
                                assignee.active_task_id = None
                elif task.status == STATUS_BLOCKED:
                    task.status = STATUS_IN_PROGRESS
                    task.progress = min(100, task.progress + random.randint(6, 14))
                    task.history.append("Manager unblocked and resumed")
                task.updated_at = datetime.now(timezone.utc).isoformat()

    def _assign_task(self, task: Task) -> None:
        for agent in self.sub_agents.values():
            if agent.role.lower() == task.role.lower() and agent.active_task_id is None:
                task.assignee_id = agent.id
                agent.active_task_id = task.id
                task.history.append(f"Assigned to {agent.role} ({agent.id})")
                return

        for agent in self.sub_agents.values():
            if agent.active_task_id is None:
                task.assignee_id = agent.id
                agent.active_task_id = task.id
                task.history.append(f"Assigned cross-functionally to {agent.role} ({agent.id})")
                return

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            totals = {STATUS_TODO: 0, STATUS_IN_PROGRESS: 0, STATUS_BLOCKED: 0, STATUS_DONE: 0}
            for task in self.tasks.values():
                totals[task.status] += 1
            return {
                "objective": self.objective,
                "poll_interval_seconds": self.poll_interval_seconds,
                "azure_configured": bool(self.azure_endpoint and self.azure_deployment and self.azure_api_key),
                "azure": {
                    "endpoint": self.azure_endpoint,
                    "deployment": self.azure_deployment,
                    "api_version": self.azure_api_version,
                },
                "totals": totals,
                "tasks": [asdict(t) for t in self.tasks.values()],
                "sub_agents": [asdict(s) for s in self.sub_agents.values()],
                "chat": list(self.chat),
            }


manager = ManagerAgent()


def monitor_loop() -> None:
    while True:
        time.sleep(manager.poll_interval_seconds)
        manager.tick()


threading.Thread(target=monitor_loop, daemon=True).start()


@app.get("/")
def dashboard() -> str:
    return render_template("manager_dashboard.html")


@app.post("/api/objective")
def api_set_objective():
    data = request.get_json(silent=True) or {}
    objective = data.get("objective", "").strip()
    roles = data.get("roles")
    if not objective:
        return jsonify({"error": "objective is required"}), 400
    if roles is not None and not isinstance(roles, list):
        return jsonify({"error": "roles must be a list"}), 400
    return jsonify(manager.set_objective(objective, roles))


@app.post("/api/config")
def api_set_config():
    data = request.get_json(silent=True) or {}
    interval = data.get("poll_interval_seconds")
    if not isinstance(interval, int):
        return jsonify({"error": "poll_interval_seconds must be an integer"}), 400
    return jsonify(manager.set_interval(interval))


@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400
    return jsonify(manager.receive_chat(message))


@app.get("/api/state")
def api_state():
    return jsonify(manager.snapshot())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5050")), debug=True)
