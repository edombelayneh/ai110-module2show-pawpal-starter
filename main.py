from pawpal_system import Owner, Pet, Task, Schedule, detect_conflicts

# --- Setup ---
owner = Owner(name="Alex", available_hours=3.0, wake_time="7:00 AM")

dog = Pet(name="Biscuit", species="dog", owner=owner)
cat = Pet(name="Luna",    species="cat", owner=owner)

owner.pets = [dog, cat]

# --- Tasks for Biscuit (dog) — mixed frequencies, added out of time order ---
dog.add_task(Task(title="Evening play",    duration_minutes=20, priority="medium", time_of_day="evening",   frequency="daily"))
dog.add_task(Task(title="Feed breakfast",  duration_minutes=10, priority="high",   time_of_day="morning",   frequency="daily"))
dog.add_task(Task(title="Afternoon nap",   duration_minutes=15, priority="low",    time_of_day="afternoon", frequency="once"))
dog.add_task(Task(title="Morning walk",    duration_minutes=30, priority="high",   time_of_day="morning",   frequency="daily"))
dog.add_task(Task(title="Flea treatment",  duration_minutes=5,  priority="high",   time_of_day="any",       frequency="weekly"))

# --- Tasks for Luna (cat) — also out of order ---
cat.add_task(Task(title="Evening feeding",  duration_minutes=10, priority="high", time_of_day="evening",   frequency="daily"))
cat.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high", time_of_day="morning",   frequency="daily"))
cat.add_task(Task(title="Brush fur",        duration_minutes=15, priority="low",  time_of_day="afternoon", frequency="weekly"))

# ── Day 1 schedule ──────────────────────────────────────────────────────────
print("=" * 45)
print("  DAY 1 — SCHEDULE")
print("=" * 45)

dog_sched = Schedule(pet=dog, date="2026-03-27")
cat_sched = Schedule(pet=cat, date="2026-03-27")
dog_sched.generate()
cat_sched.generate()

print(dog_sched.explain())
print()
print(cat_sched.explain())
print()

# ── Conflict detection — natural cross-pet overlaps ──────────────────────────
# Both pets have high-priority morning tasks that start at wake_time (7:00 AM),
# so the owner would need to be in two places at once.
print("=" * 45)
print("  CONFLICT DETECTION — Day 1")
print("=" * 45)

warnings = detect_conflicts([dog_sched, cat_sched])
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts found.")
print()

# ── Forced explicit overlap demo ─────────────────────────────────────────────
# Add two tasks to a fresh pet that are guaranteed to overlap in time:
# "Pill" starts at 7:00 AM (30 min) and "Weigh-in" starts at 7:10 AM (10 min).
print("=" * 45)
print("  FORCED OVERLAP DEMO (same pet, same time)")
print("=" * 45)

demo_owner = Owner(name="Demo", available_hours=2.0, wake_time="7:00 AM", task_buffer_minutes=0)
demo_pet   = Pet(name="Rex", species="dog", owner=demo_owner)
demo_pet.add_task(Task(title="Morning pill",  duration_minutes=30, priority="high", time_of_day="morning"))
demo_pet.add_task(Task(title="Weigh-in",      duration_minutes=10, priority="high", time_of_day="morning"))

demo_sched = Schedule(pet=demo_pet, date="2026-03-27")
demo_sched.generate()

# Manually force both entries to the same start time to demonstrate detection
if len(demo_sched.plan) == 2:
    demo_sched.plan[1].start_time = demo_sched.plan[0].start_time

print(demo_sched.explain())
for w in demo_sched.conflicts():
    print(f"  {w}")
print()

# ── Complete some tasks (including recurring ones) ───────────────────────────
print("=" * 45)
print("  COMPLETING TASKS")
print("=" * 45)

# Complete "Feed breakfast" (daily) for Biscuit
feed_id = next(tid for tid, t in dog.tasks.items() if t.title == "Feed breakfast" and not t.completed)
new_feed = dog.complete_task(feed_id)
print(f"Completed 'Feed breakfast' (daily)  → next occurrence created: {new_feed is not None}")

# Complete "Afternoon nap" (once) for Biscuit
nap_id = next(tid for tid, t in dog.tasks.items() if t.title == "Afternoon nap")
new_nap = dog.complete_task(nap_id)
print(f"Completed 'Afternoon nap'   (once)  → next occurrence created: {new_nap is not None}")

# Complete "Flea treatment" (weekly) for Biscuit
flea_id = next(tid for tid, t in dog.tasks.items() if t.title == "Flea treatment" and not t.completed)
new_flea = dog.complete_task(flea_id)
print(f"Completed 'Flea treatment'  (weekly)→ next occurrence created: {new_flea is not None}")

# Complete "Clean litter box" (daily) for Luna
litter_id = next(tid for tid, t in cat.tasks.items() if t.title == "Clean litter box" and not t.completed)
new_litter = cat.complete_task(litter_id)
print(f"Completed 'Clean litter box'(daily) → next occurrence created: {new_litter is not None}")
print()

# ── Day 2 schedule — recurring tasks are automatically back ─────────────────
print("=" * 45)
print("  DAY 2 — SCHEDULE (after completions)")
print("=" * 45)

for pet in owner.pets:
    s = Schedule(pet=pet, date="2026-03-28")
    s.generate()
    print(s.explain())
    print()

# ── sort_by_time() demo ──────────────────────────────────────────────────────
dog_sched = Schedule(pet=dog, date="2026-03-28")
dog_sched.generate()

print("=" * 45)
print("  Biscuit's Day 2 plan — sorted by time")
print("=" * 45)
for entry in dog_sched.sort_by_time():
    freq_label = f"[{entry.task.frequency}]"
    print(f"  {entry.start_time} — {entry.task.title} ({entry.task.duration_minutes} min) {freq_label}")
print()

# ── filter_tasks() demos ─────────────────────────────────────────────────────
print("=" * 45)
print("  All PENDING tasks across both pets")
print("=" * 45)
for pet_name, task in owner.filter_tasks(completed=False):
    print(f"  [{pet_name}] {task.title} ({task.frequency})")
print()

print("=" * 45)
print("  All COMPLETED tasks (history)")
print("=" * 45)
for pet_name, task in owner.filter_tasks(completed=True):
    print(f"  [{pet_name}] {task.title} ({task.frequency})")
print()

print("=" * 45)
print("  Luna's tasks only")
print("=" * 45)
for pet_name, task in owner.filter_tasks(pet_name="Luna"):
    status = "done" if task.completed else "pending"
    print(f"  {task.title} [{task.frequency}] — {status}")
