# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - The objects I want to have:
    1. Pet
    2. Task (e.g. feed, walk, bathe, play, get shots)
    3. Schedule
    4. Owner
- What classes did you include, and what responsibilities did you assign to each?
  - Owner: name, available hours, wake time
  - Task: title, duration (minutes), priority, time of day — supports editing via edit()
  - Pet: name, species, owner, list of tasks — can add/remove tasks
  - Schedule: pet + date → generates a daily plan and explains it in plain text

**b. Design changes**

- Did your design change during implementation?
  - Yes.
- If yes, describe at least one change and why you made it.
  - I replaced cost with duration_minutes on Task — the scheduler works with time, not money, so duration is what actually matters.
  - I made Owner its own class so the scheduler can read things like available hours and wake time without digging into Pet.
  - Tasks moved from Schedule to Pet, since a pet's tasks don't change day to day — Schedule just uses them to build that day's plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - Time budget: the owner's available hours cap how many minutes of tasks can fit in a day.
  - Priority: tasks are ranked high, medium, low. Higher priority tasks are always placed first.
  - Time-of-day preference: each task has a preferred window (morning, afternoon, evening, or any). The scheduler jumps its clock forward to that window if it hasn't arrived yet.
  - Task buffer: a configurable gap between tasks gives the owner transition time and counts against the daily budget.
  - Completion status: already-done tasks are filtered out before scheduling so they never take up time.
- How did you decide which constraints mattered most?
  - Priority first, because critical tasks like feeding or medication must be protected on a busy day. Time budget second, since the whole point is fitting care into a real schedule. Time-of-day preference is softer, so the scheduler places a task late rather than skipping it if the preferred window has passed.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - The scheduler is greedy and single-pass. It sorts tasks once by priority, then places them in order using a moving clock. If a task does not fit the remaining budget it is skipped, and the scheduler never goes back to try a different order that might fit more tasks in.
- Why is that tradeoff reasonable for this scenario?
  - A pet owner rarely has more than a handful of tasks in a day, so greedy works well in practice. The most important tasks always get placed first because they are sorted to the top. A backtracking solver would be harder to build and explain, and the payoff would only ever be fitting one or two extra low-priority tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - I used AI throughout the project for brainstorming the class structure, generating edge case ideas for testing, writing the test suite, and drafting the README section. It was especially useful for thinking through what could go wrong before writing a single test.
- What kinds of prompts or questions were most helpful?
  - Asking "what are the most important edge cases for X" produced much more useful output than asking it to just write tests. Starting with edge cases first made the tests more meaningful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - When AI suggested testing that adjacent tasks conflict, I pushed back. A task ending at 8:30 AM and another starting at 8:30 AM should not be a conflict. The interval check uses strict less-than, so touching boundaries are fine. I had AI flip that test to assert no conflict instead.
- How did you evaluate or verify what the AI suggested?
  - I ran the tests and read the actual scheduler code to confirm the boundary condition matched what the test was claiming. The code says A.start < B.end and B.start < A.end, so equal endpoints do not overlap.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - Sorting correctness: tasks come back in true chronological order, high priority before low, time-constrained windows before flexible "any" tasks.
  - Recurrence: completing a daily or weekly task creates a new pending copy with a fresh ID. One-time tasks do not.
  - Conflict detection: overlapping tasks are flagged, adjacent tasks are not, and cross-pet conflicts where the owner would need to be in two places are caught.
  - Budget edge cases: a task that exactly fits the remaining budget is scheduled, tasks too large are skipped, and completed tasks never appear in the plan.
- Why were these tests important?
  - These are the behaviors most likely to fail silently. A wrong sort order, a missing recurrence, or a false conflict would not crash the program — they would just produce a bad plan with no error, which is harder to catch.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - 4 out of 5. The core logic is tested and all 23 tests pass. The remaining uncertainty is in untested paths: the UI layer, the explain() output text, and what happens when wake_time is set later than a task's preferred window.
- What edge cases would you test next if you had more time?
  - A morning task with a wake_time of 1:00 PM, to verify the scheduler does not place it in the past.
  - filter_tasks() across multiple pets with mixed completion states.
  - A plan where only lower-priority tasks fit after a high-priority task consumes most of the budget.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - The scheduler's sort logic. Using a three-key tuple to handle priority, window type, and window start hour in a single sorted() call is clean and easy to reason about. The tests confirmed it works correctly even in cases like "any" vs constrained windows at the same priority level.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - I would add a date field to Task so recurring tasks track when the next occurrence is actually due, instead of just creating a copy immediately. Right now a weekly task completed on Monday generates a new task that the scheduler would place the very next day, which is wrong.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - AI is most useful when you already know enough to evaluate what it gives you. It generated good test ideas, but I still had to read the actual code to confirm whether each test was making the right assertion. The adjacent-task boundary case is a good example: AI initially got it wrong, and catching that required understanding the interval logic myself.
