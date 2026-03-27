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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
