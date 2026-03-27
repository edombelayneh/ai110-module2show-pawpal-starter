from datetime import datetime

import pytest

from pawpal_system import Owner, Pet, PlanEntry, Schedule, Task, detect_conflicts


# ── helpers ───────────────────────────────────────────────────────────────────

def make_owner(hours=3.0, wake="7:00 AM", buffer=5):
    return Owner(name="Alex", available_hours=hours, wake_time=wake,
                 task_buffer_minutes=buffer)


def make_pet(owner=None):
    return Pet(name="Biscuit", species="dog", owner=owner or make_owner())


def make_task(title="Walk", duration=30, priority="medium",
              time_of_day="morning", frequency="once"):
    return Task(title=title, duration_minutes=duration, priority=priority,
                time_of_day=time_of_day, frequency=frequency)


def make_entry(title, start_time, duration, priority="medium"):
    """Build a PlanEntry directly, bypassing generate(), for conflict tests."""
    task = Task(title=title, duration_minutes=duration,
                priority=priority, time_of_day="morning")
    return PlanEntry(task=task, start_time=start_time, reason="test")


# ── existing tests ────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


# ── sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_time_true_chronological_order():
    """sort_by_time() uses datetime parsing, not string comparison.

    Lexicographic order: "12:00 PM" < "1:00 PM" < "9:00 AM" (wrong).
    Chronological order: "9:00 AM" < "12:00 PM" < "1:00 PM" (correct).
    """
    owner = make_owner(hours=8.0, wake="6:00 AM", buffer=0)
    pet = make_pet(owner)
    pet.add_task(make_task("Lunch meds",    20, "medium", "afternoon"))
    pet.add_task(make_task("Evening walk",  30, "low",    "evening"))
    pet.add_task(make_task("Morning feed",  15, "high",   "morning"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()
    sorted_entries = sched.sort_by_time()

    parsed = [datetime.strptime(e.start_time, "%I:%M %p") for e in sorted_entries]
    assert parsed == sorted(parsed), (
        f"sort_by_time() returned out-of-order times: "
        f"{[e.start_time for e in sorted_entries]}"
    )


def test_sort_by_time_pm_after_am():
    """12:00 PM must appear after 9:00 AM, not before (lexicographic trap)."""
    owner = make_owner(hours=8.0, wake="6:00 AM", buffer=0)
    pet = make_pet(owner)
    pet.add_task(make_task("Afternoon task", 30, "medium", "afternoon"))
    pet.add_task(make_task("Morning task",   30, "high",   "morning"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()
    sorted_entries = sched.sort_by_time()

    titles = [e.task.title for e in sorted_entries]
    assert titles.index("Morning task") < titles.index("Afternoon task")


def test_sort_high_priority_scheduled_before_low():
    """High-priority tasks are placed before low-priority ones in the plan."""
    owner = make_owner(hours=4.0, wake="6:00 AM", buffer=0)
    pet = make_pet(owner)
    pet.add_task(make_task("Low task",  30, "low",  "morning"))
    pet.add_task(make_task("High task", 30, "high", "morning"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()

    assert sched.plan[0].task.title == "High task", (
        f"Expected High task first, got {[e.task.title for e in sched.plan]}"
    )


def test_sort_constrained_window_before_any_same_priority():
    """With equal priority, morning-constrained task sorts before 'any' task."""
    owner = make_owner(hours=4.0, wake="6:00 AM", buffer=0)
    pet = make_pet(owner)
    pet.add_task(make_task("Flexible",  30, "medium", "any"))
    pet.add_task(make_task("Morning",   30, "medium", "morning"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()

    assert sched.plan[0].task.title == "Morning", (
        f"Expected Morning task first, got {[e.task.title for e in sched.plan]}"
    )


# ── recurrence logic ──────────────────────────────────────────────────────────

def test_next_occurrence_once_returns_none():
    """`next_occurrence()` on a one-time task must return None."""
    task = make_task(frequency="once")
    assert task.next_occurrence() is None


def test_next_occurrence_daily_is_uncompleted_copy():
    """`next_occurrence()` returns a fresh, uncompleted task with a new ID."""
    task = make_task(frequency="daily")
    task.mark_complete()
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.task_id != task.task_id
    assert next_task.title == task.title
    assert next_task.frequency == "daily"


def test_complete_daily_task_adds_new_pending_task():
    """Completing a daily task leaves the old one in history and adds a new pending one."""
    pet = make_pet()
    task = make_task(frequency="daily")
    pet.add_task(task)

    next_task = pet.complete_task(task.task_id)

    assert pet.tasks[task.task_id].completed is True   # original still present
    assert next_task is not None
    assert next_task.task_id in pet.tasks              # new task registered
    assert len(pet.tasks) == 2


def test_complete_once_task_does_not_create_new_task():
    """Completing a one-time task must not insert a new task."""
    pet = make_pet()
    task = make_task(frequency="once")
    pet.add_task(task)

    result = pet.complete_task(task.task_id)

    assert result is None
    assert len(pet.tasks) == 1


def test_complete_weekly_task_adds_new_task():
    """Weekly tasks regenerate just like daily tasks."""
    pet = make_pet()
    task = make_task(frequency="weekly")
    pet.add_task(task)

    next_task = pet.complete_task(task.task_id)

    assert next_task is not None
    assert next_task.frequency == "weekly"
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_recurring_new_task_has_different_id():
    """The regenerated task must be tracked independently (distinct task_id)."""
    pet = make_pet()
    task = make_task(frequency="daily")
    pet.add_task(task)

    next_task = pet.complete_task(task.task_id)
    assert next_task.task_id != task.task_id


# ── conflict detection ────────────────────────────────────────────────────────

def test_conflicts_same_start_time_flagged():
    """Two tasks starting at the same time must produce a conflict warning."""
    sched = Schedule(pet=make_pet(), date="2026-03-27")
    sched.plan = [
        make_entry("Walk", "8:00 AM", 30),
        make_entry("Feed", "8:00 AM", 20),
    ]

    warnings = sched.conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feed" in warnings[0]


def test_conflicts_partial_overlap_flagged():
    """Task B starting mid-way through Task A is a conflict."""
    sched = Schedule(pet=make_pet(), date="2026-03-27")
    sched.plan = [
        make_entry("Walk", "8:00 AM", 30),   # 8:00–8:30
        make_entry("Feed", "8:15 AM", 30),   # 8:15–8:45  overlaps
    ]

    assert len(sched.conflicts()) == 1


def test_conflicts_adjacent_tasks_not_a_conflict():
    """Tasks that share only an endpoint (A ends when B starts) must not conflict.

    The interval check uses strict < so touching boundaries are allowed.
    """
    sched = Schedule(pet=make_pet(), date="2026-03-27")
    sched.plan = [
        make_entry("Walk", "8:00 AM", 30),   # 8:00–8:30
        make_entry("Feed", "8:30 AM", 20),   # 8:30–8:50  adjacent, no overlap
    ]

    assert sched.conflicts() == [], "Adjacent tasks should not be flagged as conflicting"


def test_conflicts_single_task_no_conflict():
    """A one-task plan can never conflict with itself."""
    sched = Schedule(pet=make_pet(), date="2026-03-27")
    sched.plan = [make_entry("Walk", "8:00 AM", 30)]

    assert sched.conflicts() == []


def test_conflicts_empty_plan_no_conflict():
    """An empty plan produces no conflicts."""
    sched = Schedule(pet=make_pet(), date="2026-03-27")
    sched.plan = []

    assert sched.conflicts() == []


def test_detect_conflicts_cross_pet_overlap():
    """Two pets with overlapping tasks must raise a cross-pet warning."""
    owner = make_owner(hours=4.0, wake="6:00 AM", buffer=0)
    pet1 = Pet(name="Biscuit", species="dog", owner=owner)
    pet2 = Pet(name="Luna",    species="cat", owner=owner)

    sched1 = Schedule(pet=pet1, date="2026-03-27")
    sched2 = Schedule(pet=pet2, date="2026-03-27")
    sched1.plan = [make_entry("Walk", "8:00 AM", 30)]
    sched2.plan = [make_entry("Feed", "8:00 AM", 20)]

    warnings = detect_conflicts([sched1, sched2])
    cross = [w for w in warnings if "cross-pet" in w]
    assert len(cross) >= 1


def test_detect_conflicts_non_overlapping_no_warnings():
    """Non-overlapping schedules across two pets produce no warnings."""
    owner = make_owner(hours=4.0, wake="6:00 AM", buffer=0)
    pet1 = Pet(name="Biscuit", species="dog", owner=owner)
    pet2 = Pet(name="Luna",    species="cat", owner=owner)

    sched1 = Schedule(pet=pet1, date="2026-03-27")
    sched2 = Schedule(pet=pet2, date="2026-03-27")
    sched1.plan = [make_entry("Walk", "8:00 AM", 30)]   # 8:00–8:30
    sched2.plan = [make_entry("Feed", "9:00 AM", 20)]   # 9:00–9:20

    assert detect_conflicts([sched1, sched2]) == []


# ── budget edge cases ─────────────────────────────────────────────────────────

def test_task_fits_exactly_at_budget_boundary():
    """A task whose duration equals the full budget should be scheduled, not skipped."""
    owner = make_owner(hours=0.5, wake="7:00 AM", buffer=0)  # 30 min
    pet = make_pet(owner)
    pet.add_task(make_task("Exact fit", 30, "high", "morning"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()

    assert len(sched.plan) == 1
    assert sched.plan[0].task.title == "Exact fit"
    assert sched.skipped == []


def test_all_tasks_skipped_when_budget_too_small():
    """Tasks that exceed the budget all land in skipped; plan is empty."""
    owner = make_owner(hours=0.1, wake="7:00 AM", buffer=0)  # ~6 min
    pet = make_pet(owner)
    pet.add_task(make_task("Long walk",  60, "high",   "morning"))
    pet.add_task(make_task("Grooming",   45, "medium", "afternoon"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()

    assert sched.plan == []
    assert len(sched.skipped) == 2


def test_completed_tasks_excluded_from_generated_plan():
    """Completed tasks must not appear in the plan, regardless of priority."""
    owner = make_owner(hours=3.0, wake="7:00 AM", buffer=0)
    pet = make_pet(owner)

    done = make_task("Done walk", 30, "high", "morning")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task("Pending feed", 20, "medium", "morning"))

    sched = Schedule(pet=pet, date="2026-03-27")
    sched.generate()

    titles = [e.task.title for e in sched.plan]
    assert "Done walk" not in titles
    assert "Pending feed" in titles


def test_owner_invalid_available_hours_raises():
    """Owner rejects available_hours=0 at construction time."""
    with pytest.raises(ValueError):
        Owner(name="Alex", available_hours=0, wake_time="7:00 AM")
