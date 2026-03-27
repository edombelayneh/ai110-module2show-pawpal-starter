from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    available_hours: float
    wake_time: str  # e.g. "7:00 AM"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str       # "low" | "medium" | "high"
    time_of_day: str    # "morning" | "afternoon" | "evening" | "any"

    def edit(self, field: str, value) -> None:
        # TODO: validate field and value, then update
        pass


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        # TODO: append task to self.tasks
        pass

    def remove_task(self, title: str) -> None:
        # TODO: remove task matching title from self.tasks
        pass


@dataclass
class Schedule:
    pet: Pet
    date: str  # e.g. "2026-03-27"
    plan: list[dict] = field(default_factory=list)
    # each dict: {"task": Task, "start_time": str, "reason": str}

    def generate(self) -> None:
        # TODO:
        # 1. sort pet.tasks by priority (high -> medium -> low)
        # 2. fit tasks into pet.owner.available_hours
        # 3. respect time_of_day preferences when assigning start_time
        # 4. build reason string for each task
        # 5. populate self.plan
        pass

    def explain(self) -> str:
        # TODO: return a human-readable summary of self.plan
        pass
