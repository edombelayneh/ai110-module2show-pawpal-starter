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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
