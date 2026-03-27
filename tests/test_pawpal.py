from pawpal_system import Owner, Pet, Task


def make_owner():
    return Owner(name="Alex", available_hours=3.0, wake_time="7:00 AM")


def make_task():
    return Task(title="Morning walk", duration_minutes=30, priority="high", time_of_day="morning")


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Biscuit", species="dog", owner=make_owner())
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
