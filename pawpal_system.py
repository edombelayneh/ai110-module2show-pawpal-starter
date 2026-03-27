from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta


# Maps time_of_day labels to (start_hour, end_hour) in 24h format
TIME_RANGES: dict[str, tuple[int, int]] = {
    "morning":   (6,  12),
    "afternoon": (12, 17),
    "evening":   (17, 21),
    "any":       (6,  21),
}

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

EDITABLE_FIELDS = {"title", "duration_minutes", "priority", "time_of_day", "completed"}


@dataclass
class Owner:
    name: str
    available_hours: float
    wake_time: str  # e.g. "7:00 AM"
    pets: list[Pet] = field(default_factory=list)


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str       # "low" | "medium" | "high"
    time_of_day: str    # "morning" | "afternoon" | "evening" | "any"
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    completed: bool = False

    def edit(self, field: str, value) -> None:
        """Validate and update a single editable field on this task."""
        if field not in EDITABLE_FIELDS:
            raise ValueError(f"'{field}' is not an editable field. Choose from: {EDITABLE_FIELDS}")
        if field == "priority" and value not in PRIORITY_ORDER:
            raise ValueError(f"priority must be 'low', 'medium', or 'high', got '{value}'")
        if field == "time_of_day" and value not in TIME_RANGES:
            raise ValueError(f"time_of_day must be one of {list(TIME_RANGES)}, got '{value}'")
        if field == "duration_minutes" and (not isinstance(value, int) or value <= 0):
            raise ValueError(f"duration_minutes must be a positive integer, got {value!r}")
        if field == "completed" and not isinstance(value, bool):
            raise ValueError(f"completed must be True or False, got {value!r}")
        setattr(self, field, value)

    def mark_complete(self) -> None:
        """Mark this task as done so the scheduler skips it."""
        self.completed = True


@dataclass
class PlanEntry:
    task: Task
    start_time: str  # e.g. "8:00 AM"
    reason: str


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its unique ID, raising ValueError if not found."""
        for i, t in enumerate(self.tasks):
            if t.task_id == task_id:
                self.tasks.pop(i)
                return
        raise ValueError(f"No task with id '{task_id}' found for {self.name}")


@dataclass
class Schedule:
    pet: Pet
    date: str  # e.g. "2026-03-27"
    plan: list[PlanEntry] = field(default_factory=list)

    def generate(self) -> None:
        """Build a time-ordered plan for the day based on priority, duration, and time preferences."""
        # Sort tasks high -> medium -> low, skip already completed ones
        sorted_tasks = sorted(
            [t for t in self.pet.tasks if not t.completed],
            key=lambda t: PRIORITY_ORDER[t.priority]
        )

        available_minutes = self.pet.owner.available_hours * 60
        used_minutes = 0

        # Use wake_time as the base for the day's clock
        current = datetime.strptime(self.pet.owner.wake_time, "%I:%M %p")

        self.plan = []

        for task in sorted_tasks:
            # Stop if there's no time left
            if used_minutes + task.duration_minutes > available_minutes:
                break

            # Get the preferred time window for this task
            range_start_h, range_end_h = TIME_RANGES[task.time_of_day]
            window_start = current.replace(hour=range_start_h, minute=0, second=0)
            window_end   = current.replace(hour=range_end_h,   minute=0, second=0)

            # Jump forward to the window if we haven't reached it yet
            if current < window_start:
                current = window_start

            # If we've already passed the window, schedule at current time (best effort)
            if current >= window_end and task.time_of_day != "any":
                reason = (
                    f"{task.priority.capitalize()} priority; "
                    f"preferred {task.time_of_day} but scheduled late due to earlier tasks"
                )
            else:
                reason = (
                    f"{task.priority.capitalize()} priority; "
                    f"fits {task.time_of_day} window and within "
                    f"{self.pet.owner.available_hours}h available"
                )

            start_time_str = current.strftime("%I:%M %p").lstrip("0")
            self.plan.append(PlanEntry(task=task, start_time=start_time_str, reason=reason))

            current += timedelta(minutes=task.duration_minutes)
            used_minutes += task.duration_minutes

    def explain(self) -> str:
        """Return a human-readable summary of the generated plan."""
        if not self.plan:
            return "No plan yet — call generate() first."

        lines = [f"Schedule for {self.pet.name} on {self.date}:"]
        for entry in self.plan:
            lines.append(
                f"  {entry.start_time} — {entry.task.title} "
                f"({entry.task.duration_minutes} min) [{entry.task.priority}]: "
                f"{entry.reason}"
            )
        return "\n".join(lines)
