from pawpal_system import Owner, Pet, Task, Schedule

# --- Setup ---
owner = Owner(name="Alex", available_hours=3.0, wake_time="7:00 AM")

dog = Pet(name="Biscuit", species="dog", owner=owner)
cat = Pet(name="Luna",    species="cat", owner=owner)

owner.pets = [dog, cat]

# --- Tasks for Biscuit (dog) ---
dog.add_task(Task(title="Morning walk",    duration_minutes=30, priority="high",   time_of_day="morning"))
dog.add_task(Task(title="Feed breakfast",  duration_minutes=10, priority="high",   time_of_day="morning"))
dog.add_task(Task(title="Evening play",    duration_minutes=20, priority="medium", time_of_day="evening"))

# --- Tasks for Luna (cat) ---
cat.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high",   time_of_day="morning"))
cat.add_task(Task(title="Brush fur",        duration_minutes=15, priority="low",    time_of_day="afternoon"))
cat.add_task(Task(title="Evening feeding",  duration_minutes=10, priority="high",   time_of_day="evening"))

# --- Generate and print schedules ---
print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)

for pet in owner.pets:
    schedule = Schedule(pet=pet, date="2026-03-27")
    schedule.generate()
    print(schedule.explain())
    print()
