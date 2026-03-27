import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, TIME_RANGES, PRIORITY_ORDER

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner ---
st.subheader("Owner")
col1, col2, col3, col4 = st.columns(4)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_hours = st.number_input("Available hours today", min_value=0.5, max_value=16.0, value=3.0, step=0.5)
with col3:
    wake_time = st.text_input("Wake time", value="7:00 AM")
with col4:
    buffer_minutes = st.number_input("Buffer between tasks (min)", min_value=0, max_value=30, value=5, step=1)

if (
    "owner" not in st.session_state
    or st.session_state.owner.name != owner_name
    or st.session_state.owner.available_hours != available_hours
    or st.session_state.owner.wake_time != wake_time
    or st.session_state.owner.task_buffer_minutes != int(buffer_minutes)
):
    try:
        st.session_state.owner = Owner(
            name=owner_name,
            available_hours=available_hours,
            wake_time=wake_time,
            task_buffer_minutes=int(buffer_minutes),
        )
    except ValueError as e:
        st.error(str(e))

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species, owner=st.session_state.owner)
    st.session_state.owner.pets.append(new_pet)
    st.success(f"Added {pet_name} the {species}!")

if st.session_state.owner.pets:
    st.write("Pets:", ", ".join(f"{p.name} ({p.species})" for p in st.session_state.owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task ---
st.subheader("Schedule a Task")

if not st.session_state.owner.pets:
    st.warning("Add a pet first.")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        time_of_day = st.selectbox("Time of day", ["morning", "afternoon", "evening", "any"])

    if st.button("Add task"):
        task = Task(title=task_title, duration_minutes=int(duration), priority=priority, time_of_day=time_of_day)
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    if selected_pet.tasks:
        st.write(f"{selected_pet_name}'s tasks:")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status_filter = st.selectbox(
                "Filter by status", ["all", "pending", "completed"], key="task_status_filter"
            )
        with col_f2:
            sort_order = st.selectbox(
                "Sort by", ["default", "time of day", "priority", "duration"], key="task_sort"
            )

        tasks_to_show = list(selected_pet.tasks.values())

        if status_filter == "pending":
            tasks_to_show = [t for t in tasks_to_show if not t.completed]
        elif status_filter == "completed":
            tasks_to_show = [t for t in tasks_to_show if t.completed]

        if sort_order == "time of day":
            tasks_to_show = sorted(tasks_to_show, key=lambda t: TIME_RANGES[t.time_of_day][0])
        elif sort_order == "priority":
            tasks_to_show = sorted(tasks_to_show, key=lambda t: PRIORITY_ORDER[t.priority])
        elif sort_order == "duration":
            tasks_to_show = sorted(tasks_to_show, key=lambda t: t.duration_minutes)

        st.table([
            {
                "title": t.title,
                "duration (min)": t.duration_minutes,
                "priority": t.priority,
                "time of day": t.time_of_day,
                "status": "done" if t.completed else "pending",
            }
            for t in tasks_to_show
        ])
    else:
        st.info(f"No tasks yet for {selected_pet_name}.")

st.divider()

# --- Task Overview (all pets) ---
st.subheader("Task Overview")

if not st.session_state.owner.pets:
    st.info("No pets yet.")
else:
    all_pets = st.session_state.owner.pets
    pet_filter_options = ["All pets"] + [p.name for p in all_pets]

    col_p, col_s, col_so = st.columns(3)
    with col_p:
        pet_filter = st.selectbox("Filter by pet", pet_filter_options, key="overview_pet")
    with col_s:
        overview_status = st.selectbox(
            "Filter by status", ["all", "pending", "completed"], key="overview_status"
        )
    with col_so:
        overview_sort = st.selectbox(
            "Sort by", ["default", "time of day", "priority", "duration"], key="overview_sort"
        )

    if pet_filter == "All pets":
        all_tasks = [
            (p.name, t)
            for p in all_pets
            for t in p.tasks.values()
        ]
    else:
        target_pet = next(p for p in all_pets if p.name == pet_filter)
        all_tasks = [(target_pet.name, t) for t in target_pet.tasks.values()]

    if overview_status == "pending":
        all_tasks = [(pn, t) for pn, t in all_tasks if not t.completed]
    elif overview_status == "completed":
        all_tasks = [(pn, t) for pn, t in all_tasks if t.completed]

    if overview_sort == "time of day":
        all_tasks = sorted(all_tasks, key=lambda x: TIME_RANGES[x[1].time_of_day][0])
    elif overview_sort == "priority":
        all_tasks = sorted(all_tasks, key=lambda x: PRIORITY_ORDER[x[1].priority])
    elif overview_sort == "duration":
        all_tasks = sorted(all_tasks, key=lambda x: x[1].duration_minutes)

    if all_tasks:
        st.table([
            {
                "pet": pn,
                "title": t.title,
                "duration (min)": t.duration_minutes,
                "priority": t.priority,
                "time of day": t.time_of_day,
                "status": "done" if t.completed else "pending",
            }
            for pn, t in all_tasks
        ])
    else:
        st.info("No tasks match the selected filters.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if not st.session_state.owner.pets:
    st.warning("Add a pet and some tasks first.")
else:
    sched_pet_name = st.selectbox("Schedule for", [p.name for p in st.session_state.owner.pets], key="sched_select")
    sched_pet = next(p for p in st.session_state.owner.pets if p.name == sched_pet_name)

    if st.button("Generate schedule"):
        from datetime import date
        schedule = Schedule(pet=sched_pet, date=str(date.today()))
        schedule.generate()
        st.text(schedule.explain())
