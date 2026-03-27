from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "planner_data.json"
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "study_planner")

DEFAULT_CATEGORIES = ["GATE DA", "DSA in Python", "College Study"]
TRACKS = {
    "dsa": {
        "title": "DSA in Python",
        "duration_days": 90,
        "theme": "dsa",
        "overview": "Build strong problem-solving skill with a focused 90-day DSA roadmap.",
        "details": [
            "Arrays, strings, hashing, stacks, queues",
            "Linked lists, recursion, trees, heaps, graphs",
            "Daily coding practice with revision blocks",
        ],
    },
    "gate-da": {
        "title": "GATE DA",
        "duration_days": 120,
        "theme": "gate",
        "overview": "Prepare for GATE DA with concept study, revision, and question practice.",
        "details": [
            "Mathematics, probability, machine learning, data science basics",
            "Revision cycles with previous year question practice",
            "Topic-based daily consistency and timed sessions",
        ],
    },
    "college-work": {
        "title": "College Work",
        "duration_days": 30,
        "theme": "college",
        "overview": "Stay ahead in classes, assignments, notes, and submissions every day.",
        "details": [
            "Lecture revision, assignments, practical work, and deadlines",
            "Structured daily study blocks to avoid backlog",
            "Room to track subject-wise effort and priorities",
        ],
    },
}
TRACK_TO_CATEGORY = {
    "dsa": "DSA in Python",
    "gate-da": "GATE DA",
    "college-work": "College Study",
}
MOTIVATION_QUOTES = [
    {
        "quote": "The successful warrior is the average man, with laser-like focus.",
        "author": "Bruce Lee",
    },
    {
        "quote": "Do not pray for an easy life, pray for the strength to endure a difficult one.",
        "author": "Bruce Lee",
    },
    {
        "quote": "Knowing is not enough, we must apply. Willing is not enough, we must do.",
        "author": "Bruce Lee",
    },
    {
        "quote": "It does not matter how slowly you go as long as you do not stop.",
        "author": "Confucius",
    },
    {
        "quote": "Success is the sum of small efforts, repeated day in and day out.",
        "author": "Robert Collier",
    },
    {
        "quote": "Discipline is choosing between what you want now and what you want most.",
        "author": "Abraham Lincoln",
    },
]


mongo_client: MongoClient | None = None


def create_app() -> Flask:
    app = Flask(__name__)

    DATA_DIR.mkdir(exist_ok=True)
    ensure_storage()

    @app.route("/")
    def dashboard() -> str:
        data = load_data()
        goals = data["goals"]
        tasks = data["tasks"]
        tracks_map = get_all_tracks(data)

        today = date.today().isoformat()
        today_tasks = [task for task in tasks if task["due_date"] == today]
        completed_today = sum(1 for task in today_tasks if task["status"] == "Completed")
        pending_tasks = [task for task in tasks if task["status"] != "Completed"]
        overdue_tasks = [
            task
            for task in pending_tasks
            if task["due_date"] and task["due_date"] < today
        ]

        active_goals = [goal for goal in goals if goal["status"] != "Completed"]
        goal_cards = [decorate_goal(goal) for goal in goals]
        next_goal = min(
            (goal for goal in goal_cards if goal["status"] != "Completed"),
            key=lambda goal: goal["days_left"],
            default=None,
        )
        today_minutes = sum(parse_minutes(task["estimated_time"]) for task in today_tasks)
        pending_minutes = sum(parse_minutes(task["estimated_time"]) for task in pending_tasks)
        completed_minutes = sum(
            parse_minutes(task["estimated_time"])
            for task in tasks
            if task["status"] == "Completed"
        )
        total_progress = round(
            sum(goal["progress"] for goal in goals) / len(goals), 1
        ) if goals else 0
        quote_index = date.today().toordinal() % len(MOTIVATION_QUOTES)

        return render_template(
            "dashboard.html",
            page_title="Dashboard",
            goals=goal_cards,
            today_tasks=today_tasks,
            pending_tasks=pending_tasks[:6],
            overdue_tasks=overdue_tasks,
            active_goals=active_goals,
            stats={
                "goal_count": len(goals),
                "task_count": len(tasks),
                "completed_today": completed_today,
                "total_progress": total_progress,
                "today_minutes": today_minutes,
                "pending_minutes": pending_minutes,
                "completed_minutes": completed_minutes,
            },
            categories=data["categories"],
            today=today,
            next_goal=next_goal,
            quote=MOTIVATION_QUOTES[quote_index],
            quotes=MOTIVATION_QUOTES,
            quote_index=quote_index,
            tracks=get_track_cards(data),
        )

    @app.route("/goals", methods=["GET", "POST"])
    def goals() -> str:
        data = load_data()
        if request.method == "POST":
            goal = {
                "id": next_id(data["goals"]),
                "title": request.form["title"].strip(),
                "category": request.form["category"],
                "description": request.form["description"].strip(),
                "start_date": request.form["start_date"],
                "target_date": request.form["target_date"],
                "status": request.form["status"],
                "progress": clamp_progress(request.form["progress"]),
            }
            data["goals"].append(goal)
            save_data(data)
            return redirect(url_for("goals"))

        goals_with_meta = [decorate_goal(goal) for goal in data["goals"]]
        return render_template(
            "goals.html",
            page_title="Goals",
            goals=goals_with_meta,
            categories=data["categories"],
            today=date.today().isoformat(),
        )

    @app.route("/goals/<int:goal_id>/edit", methods=["GET", "POST"])
    def edit_goal(goal_id: int) -> str:
        data = load_data()
        goal = next((goal for goal in data["goals"] if goal["id"] == goal_id), None)
        if goal is None:
            return redirect(url_for("goals"))

        if request.method == "POST":
            goal["title"] = request.form["title"].strip()
            goal["category"] = request.form["category"]
            goal["description"] = request.form["description"].strip()
            goal["start_date"] = request.form["start_date"]
            goal["target_date"] = request.form["target_date"]
            goal["status"] = request.form["status"]
            goal["progress"] = clamp_progress(request.form["progress"])
            save_data(data)
            return redirect(url_for("goals"))

        return render_template(
            "edit_goal.html",
            page_title="Edit Goal",
            goal=goal,
            categories=data["categories"],
        )

    @app.post("/goals/<int:goal_id>/delete")
    def delete_goal(goal_id: int):
        data = load_data()
        data["goals"] = [goal for goal in data["goals"] if goal["id"] != goal_id]
        for task in data["tasks"]:
            if task["goal_id"] == goal_id:
                task["goal_id"] = None
        save_data(data)
        return redirect(url_for("goals"))

    @app.route("/tasks", methods=["GET", "POST"])
    def tasks() -> str:
        data = load_data()
        if request.method == "POST":
            task = {
                "id": next_id(data["tasks"]),
                "goal_id": int(request.form["goal_id"]) if request.form["goal_id"] else None,
                "title": request.form["title"].strip(),
                "category": request.form["category"],
                "due_date": request.form["due_date"],
                "priority": request.form["priority"],
                "status": request.form["status"],
                "estimated_time": request.form["estimated_time"].strip(),
            }
            data["tasks"].append(task)
            save_data(data)
            return redirect(url_for("tasks"))

        task_rows = [decorate_task(task, data["goals"]) for task in data["tasks"]]
        return render_template(
            "tasks.html",
            page_title="Daily Tasks",
            tasks=task_rows,
            goals=data["goals"],
            categories=data["categories"],
            today=date.today().isoformat(),
        )

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    def edit_task(task_id: int) -> str:
        data = load_data()
        task = next((task for task in data["tasks"] if task["id"] == task_id), None)
        if task is None:
            return redirect(url_for("tasks"))

        if request.method == "POST":
            task["goal_id"] = int(request.form["goal_id"]) if request.form["goal_id"] else None
            task["title"] = request.form["title"].strip()
            task["category"] = request.form["category"]
            task["due_date"] = request.form["due_date"]
            task["priority"] = request.form["priority"]
            task["status"] = request.form["status"]
            task["estimated_time"] = request.form["estimated_time"].strip()
            save_data(data)
            return redirect(url_for("tasks"))

        return render_template(
            "edit_task.html",
            page_title="Edit Task",
            task=task,
            goals=data["goals"],
            categories=data["categories"],
        )

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id: int):
        data = load_data()
        data["tasks"] = [task for task in data["tasks"] if task["id"] != task_id]
        save_data(data)
        return redirect(url_for("tasks"))

    @app.route("/progress")
    def progress() -> str:
        data = load_data()
        goals = [decorate_goal(goal) for goal in data["goals"]]
        tasks = data["tasks"]

        completed_tasks = sum(1 for task in tasks if task["status"] == "Completed")
        completion_rate = round((completed_tasks / len(tasks)) * 100, 1) if tasks else 0

        category_summary = []
        for category in data["categories"]:
            category_tasks = [task for task in tasks if task["category"] == category]
            done = sum(1 for task in category_tasks if task["status"] == "Completed")
            rate = round((done / len(category_tasks)) * 100, 1) if category_tasks else 0
            category_summary.append(
                {
                    "name": category,
                    "task_count": len(category_tasks),
                    "completion_rate": rate,
                }
            )

        return render_template(
            "progress.html",
            page_title="Progress",
            goals=goals,
            category_summary=category_summary,
            completed_tasks=completed_tasks,
            total_tasks=len(tasks),
            completion_rate=completion_rate,
        )

    @app.route("/track/<track_slug>")
    def track_detail(track_slug: str) -> str:
        data = load_data()
        track = get_all_tracks(data).get(track_slug)
        if not track:
            return redirect(url_for("dashboard"))

        completed_days = set(data.get("track_progress", {}).get(track_slug, []))
        day_notes = data.get("track_day_notes", {}).get(track_slug, {})
        plan = generate_day_plan(track_slug, track, completed_days, day_notes)
        completed_count = len(completed_days)
        return render_template(
            "track_detail.html",
            page_title=track["title"],
            track_slug=track_slug,
            track=track,
            plan=plan,
            completed_count=completed_count,
            progress_percent=round((completed_count / track["duration_days"]) * 100, 1),
            is_custom_track=track_slug not in TRACKS,
        )

    @app.post("/tracks/add")
    def add_track():
        data = load_data()
        title = request.form["title"].strip()
        duration_days = max(1, int(request.form["duration_days"]))
        overview = request.form["overview"].strip()
        details_text = request.form["details"].strip()

        if not title:
            return redirect(url_for("dashboard"))

        slug = slugify(title)
        all_tracks = get_all_tracks(data)
        original_slug = slug
        counter = 2
        while slug in all_tracks:
            slug = f"{original_slug}-{counter}"
            counter += 1

        theme_cycle = ["dsa", "gate", "college"]
        custom_track = {
            "title": title,
            "duration_days": duration_days,
            "theme": theme_cycle[len(data.get("custom_tracks", [])) % len(theme_cycle)],
            "overview": overview or f"Custom study plan for {title}.",
            "details": [line.strip() for line in details_text.splitlines() if line.strip()] or [
                "Custom focus block",
                "Daily progress planning",
                "Track your own roadmap",
            ],
        }

        data.setdefault("custom_tracks", []).append({"slug": slug, **custom_track})
        data.setdefault("track_progress", {})[slug] = []
        save_data(data)
        return redirect(url_for("dashboard"))

    @app.post("/track/<track_slug>/toggle-day")
    def toggle_track_day(track_slug: str):
        data = load_data()
        track = get_all_tracks(data).get(track_slug)
        if not track:
            return redirect(url_for("dashboard"))

        day = int(request.form["day"])
        if day < 1 or day > track["duration_days"]:
            return redirect(url_for("track_detail", track_slug=track_slug))

        progress = data.setdefault("track_progress", {})
        completed = set(progress.get(track_slug, []))
        if day in completed:
            completed.remove(day)
        else:
            completed.add(day)

        progress[track_slug] = sorted(completed)
        sync_goal_progress(data, track_slug)
        save_data(data)
        return redirect(url_for("track_detail", track_slug=track_slug))

    @app.post("/track/<track_slug>/save-note")
    def save_track_note(track_slug: str):
        data = load_data()
        track = get_all_tracks(data).get(track_slug)
        if not track:
            return redirect(url_for("dashboard"))

        day = int(request.form["day"])
        if day < 1 or day > track["duration_days"]:
            return redirect(url_for("track_detail", track_slug=track_slug))

        notes = data.setdefault("track_day_notes", {})
        track_notes = notes.setdefault(track_slug, {})
        track_notes[str(day)] = request.form["note"].strip()
        save_data(data)
        return redirect(url_for("track_detail", track_slug=track_slug))

    @app.post("/track/<track_slug>/delete")
    def delete_track(track_slug: str):
        if track_slug in TRACKS:
            return redirect(url_for("track_detail", track_slug=track_slug))

        data = load_data()
        data["custom_tracks"] = [
            track for track in data.get("custom_tracks", []) if track["slug"] != track_slug
        ]
        data.get("track_progress", {}).pop(track_slug, None)
        data.get("track_day_notes", {}).pop(track_slug, None)
        save_data(data)
        return redirect(url_for("dashboard"))

    @app.route("/seed")
    def seed() -> str:
        save_data(seed_data())
        return redirect(url_for("dashboard"))

    return app


def ensure_storage() -> None:
    data = load_data()
    changed = False

    if "track_progress" not in data:
        data["track_progress"] = {slug: [] for slug in get_all_tracks(data)}
        changed = True

    if "custom_tracks" not in data:
        data["custom_tracks"] = []
        changed = True

    if "track_day_notes" not in data:
        data["track_day_notes"] = {}
        changed = True

    for slug in get_all_tracks(data):
        if slug not in data["track_progress"]:
            data["track_progress"][slug] = []
            changed = True

    for goal in data.get("goals", []):
        if goal.get("category") in DEFAULT_CATEGORIES and goal.get("progress") != 0:
            goal["progress"] = 0
            changed = True

    if changed:
        save_data(data)


def load_data() -> dict[str, Any]:
    collection = get_planner_collection()
    if collection is None:
        return load_local_data()

    state = collection.find_one({"_id": "planner_state"})
    if state is None:
        initial_data = load_initial_data()
        collection.replace_one(
            {"_id": "planner_state"},
            {"_id": "planner_state", "payload": initial_data},
            upsert=True,
        )
        return initial_data
    return state["payload"]


def save_data(data: dict[str, Any]) -> None:
    collection = get_planner_collection()
    if collection is None:
        save_local_data(data)
        return

    collection.replace_one(
        {"_id": "planner_state"},
        {"_id": "planner_state", "payload": data},
        upsert=True,
    )


def load_initial_data() -> dict[str, Any]:
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    return seed_data()


def load_local_data() -> dict[str, Any]:
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    data = seed_data()
    save_local_data(data)
    return data


def save_local_data(data: dict[str, Any]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def get_mongo_client() -> MongoClient | None:
    global mongo_client
    if not MONGODB_URI:
        return None
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URI)
    return mongo_client


def get_planner_collection():
    client = get_mongo_client()
    if client is None:
        return None
    return client[MONGODB_DB_NAME]["planner_state"]


def next_id(records: list[dict[str, Any]]) -> int:
    return max((record["id"] for record in records), default=0) + 1


def clamp_progress(value: str) -> int:
    number = int(value)
    return max(0, min(100, number))


def parse_minutes(value: str) -> int:
    text = (value or "").strip().lower()
    if not text:
        return 0

    digits = "".join(char for char in text if char.isdigit())
    if not digits:
        return 0

    amount = int(digits)
    if "hour" in text or "hr" in text or text.endswith("h"):
        return amount * 60
    return amount


def seed_data() -> dict[str, Any]:
    today = date.today()
    return {
        "categories": DEFAULT_CATEGORIES,
        "goals": [
            {
                "id": 1,
                "title": "Revise Probability for GATE DA",
                "category": "GATE DA",
                "description": "Cover concepts, formulas, and previous year questions.",
                "start_date": today.isoformat(),
                "target_date": (today + timedelta(days=10)).isoformat(),
                "status": "In Progress",
                "progress": 0,
            },
            {
                "id": 2,
                "title": "Solve 50 Python DSA Questions in 21 Days",
                "category": "DSA in Python",
                "description": "Focus on arrays, strings, recursion, and sorting with a 21-day challenge.",
                "start_date": today.isoformat(),
                "target_date": (today + timedelta(days=21)).isoformat(),
                "status": "In Progress",
                "progress": 0,
            },
        ],
        "tasks": [
            {
                "id": 1,
                "goal_id": 1,
                "title": "Revise Bayes theorem and conditional probability",
                "category": "GATE DA",
                "due_date": today.isoformat(),
                "priority": "High",
                "status": "Pending",
                "estimated_time": "90 min",
            },
            {
                "id": 2,
                "goal_id": 2,
                "title": "Solve 3 array problems in Python",
                "category": "DSA in Python",
                "due_date": today.isoformat(),
                "priority": "Medium",
                "status": "Pending",
                "estimated_time": "60 min",
            },
            {
                "id": 3,
                "goal_id": None,
                "title": "Review college lecture notes",
                "category": "College Study",
                "due_date": today.isoformat(),
                "priority": "Low",
                "status": "Pending",
                "estimated_time": "45 min",
            },
        ],
        "track_progress": {slug: [] for slug in TRACKS},
        "track_day_notes": {},
        "custom_tracks": [],
    }


def decorate_task(task: dict[str, Any], goals: list[dict[str, Any]]) -> dict[str, Any]:
    goal_lookup = {goal["id"]: goal["title"] for goal in goals}
    row = dict(task)
    row["goal_title"] = goal_lookup.get(task["goal_id"], "Independent Task")
    return row


def decorate_goal(goal: dict[str, Any]) -> dict[str, Any]:
    row = dict(goal)
    row["days_left"] = get_days_left(goal["target_date"])
    row["duration_days"] = get_duration_days(goal["start_date"], goal["target_date"])
    return row


def get_track_cards(data: dict[str, Any]) -> list[dict[str, Any]]:
    cards = []
    progress = data.get("track_progress", {})
    for slug, track in get_all_tracks(data).items():
        completed_count = len(progress.get(slug, []))
        cards.append(
            {
                "slug": slug,
                "title": track["title"],
                "duration_days": track["duration_days"],
                "overview": track["overview"],
                "details": track["details"],
                "theme": track["theme"],
                "completed_count": completed_count,
                "remaining_count": track["duration_days"] - completed_count,
                "progress_percent": round((completed_count / track["duration_days"]) * 100, 1),
            }
        )
    return cards


def generate_day_plan(
    track_slug: str,
    track: dict[str, Any],
    completed_days: set[int],
    day_notes: dict[str, str],
) -> list[dict[str, Any]]:
    if track_slug == "dsa":
        blocks = [
            ("Arrays and Strings", "Solve 3 questions and revise patterns"),
            ("Hashing and Stack", "Practice implementation and 2 mixed problems"),
            ("Linked List and Recursion", "Write code by hand and trace logic"),
            ("Trees and Heaps", "Learn concept and solve 2 medium questions"),
            ("Graphs and Revision", "Revise notes and solve 1 graph problem"),
        ]
    elif track_slug == "gate-da":
        blocks = [
            ("Mathematics", "Study a concept and solve 15 short questions"),
            ("Probability", "Revise formulas and solve PYQs"),
            ("Machine Learning", "Read topic notes and practice examples"),
            ("Data Science", "Focus on definitions, algorithms, and concepts"),
            ("Revision", "Do one-hour recap with error notebook"),
        ]
    else:
        if track_slug == "college-work":
            blocks = [
                ("Lecture Review", "Revise class notes and highlight key points"),
                ("Assignment Work", "Complete pending written or coding tasks"),
                ("Practical/Lab", "Finish record work or experiment preparation"),
                ("Subject Practice", "Read one topic in depth and summarize it"),
                ("Deadline Check", "Plan tomorrow around upcoming college work"),
            ]
        else:
            title = track["title"]
            blocks = [
                (f"{title} Core Work", f"Work on the main topic for {title} with full focus"),
                (f"{title} Practice", f"Do practice work and track mistakes for {title}"),
                (f"{title} Revision", f"Revise what you learned in {title} and note weak areas"),
                (f"{title} Deep Focus", f"Spend one longer session improving consistency in {title}"),
                (f"{title} Review", f"Review progress and plan the next day for {title}"),
            ]

    plan = []
    for day in range(1, track["duration_days"] + 1):
        block = blocks[(day - 1) % len(blocks)]
        plan.append(
            {
                "day": day,
                "focus": block[0],
                "detail": block[1],
                "minutes": 90 if track_slug == "dsa" else 120 if track_slug == "gate-da" else 60,
                "completed": day in completed_days,
                "note": day_notes.get(str(day), ""),
            }
        )
    return plan


def get_all_tracks(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tracks = dict(TRACKS)
    for custom in data.get("custom_tracks", []):
        slug = custom["slug"]
        tracks[slug] = {
            "title": custom["title"],
            "duration_days": custom["duration_days"],
            "theme": custom["theme"],
            "overview": custom["overview"],
            "details": custom["details"],
        }
    return tracks


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts) or "custom-track"


def sync_goal_progress(data: dict[str, Any], track_slug: str) -> None:
    category = TRACK_TO_CATEGORY.get(track_slug)
    track = get_all_tracks(data).get(track_slug)
    if not category or not track:
        return

    completed_count = len(data.get("track_progress", {}).get(track_slug, []))
    progress = round((completed_count / track["duration_days"]) * 100) if track["duration_days"] else 0
    for goal in data.get("goals", []):
        if goal.get("category") == category:
            goal["progress"] = progress


def get_days_left(target_date: str) -> int:
    target = datetime.strptime(target_date, "%Y-%m-%d").date()
    return (target - date.today()).days


def get_duration_days(start_date: str, target_date: str) -> int:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    target = datetime.strptime(target_date, "%Y-%m-%d").date()
    return max((target - start).days, 0)


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
