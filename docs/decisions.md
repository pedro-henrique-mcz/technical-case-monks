Hello guys, I'm Pedro, and this document will allow you to understand some of my softwares 
decisions and architectural choices.
I am using some AI tools to make the MD text a bit more polished and easier to understand, 
but all final decisions were carefully considered and made by me. 


**Decision:** A week is an ISO 8601 week (Monday to Sunday) in the company time zone,
`America/Sao_Paulo`. The evaluation timestamp is set by the server and stored in UTC
(`timestamptz`). The client never sends the date.

**Why:** The client clock can be wrong or tampered with ("never trust the client").
One fixed time zone gives the same rule to everyone, even in a country with 4 time zones.

**Discarded alternative:** Using each user's local time zone. The same leader–employee
pair could get different week boundaries, which makes "one per week" ambiguous. 

## (b) What "highest hierarchy" means

**Decision:** A viewer sees an evaluation only if (1) the evaluated employee is below
the viewer and (2) the evaluator is the viewer or someone below the viewer.
Evaluations made by peers or superiors are never shown.
The highlighted "latest evaluation" is the one from the highest evaluator visible to
the viewer (closest to the viewer in the tree), even if it is older. The others are
listed below it. Every evaluation shows its week, so the viewer knows how recent it is.

**Why:** Least privilege: each leader sees only what their position in the tree allows.
The challenge asks to always respect the highest hierarchy, so authority wins over recency.

**Discarded alternative:** Most recent week first, with the hierarchy used only as a
tie-breaker. It reads the requirement too loosely.

## (c) Questions and weights: table or code

**Decision:** The 6 questions and their weights live in a `question` table, seeded by
a migration. Weights are never edited in place; the score of each evaluation is
frozen at submission time (see decision e).

**Why:** The challenge fixes the values, but a table lets answers reference questions
with a foreign key (the database rejects an answer to a question that does not exist)
and allows future changes without touching code. Freezing the score keeps old
evaluations exactly as they were when submitted: a value decided in the past
must not change because a weight changed today.

## (d) Answers: 6 columns or a child table

**Decision:** A child table `answer` with one row per question:
(evaluation_id, question_id, score). Primary key on (evaluation_id, question_id),
`CHECK (score BETWEEN 1 AND 4)`. The backend requires exactly the 6 questions and
inserts the evaluation and its answers in a single transaction.

**Why:** Each answer references its question with a foreign key, so the weight comes
from the `question` table and a new question needs no schema change. The database
cannot easily guarantee "exactly 6 answers", so that rule lives in the backend.

**Discarded alternative:** 6 columns on `evaluation`. Simpler, but question names
become column names, with no foreign key, and adding a question changes the table.
**Discarded alternative:** Weights as constants in the code. Simpler, but there is no
foreign key protection, and changing a weight would silently change every past score
if scores were recalculated.

## (e) Final score: stored or computed

**Decision:** The final score is stored in `evaluation.final_score` (`numeric(3,2)`),
computed once by the backend at submission, in the same transaction as the answers:
`sum(score × weight) / 100`, which gives a value from 1.00 to 4.00.

**Why:** It is a snapshot. The score must reflect the criteria at the moment of
submission. If a weight changes later, past evaluations stay exactly as they were.
Since evaluations are immutable, the stored value can never drift from its answers.

**Discarded alternative:** Computing the score on every read. Always "fresh", but a
weight change would silently rewrite every past score.

## (f) How the database enforces "one per week" and "immutable"

**Decision:**
- One per week: `evaluation.week_start` (the Monday of the ISO week, computed by the
  server) and `UNIQUE (leader_id, employee_id, week_start)`. A duplicate returns 409.
- Immutable: the API has no update or delete endpoints, and a trigger on `evaluation`
  and `answer` rejects any `UPDATE` or `DELETE`. Foreign keys to `employee` use
  `ON DELETE RESTRICT`, so deleting an employee cannot erase evaluation history.

**Why:** Rules enforced only in the backend can be bypassed. A "check, then insert"
in the code fails under a race condition (a double click sends two requests that both
pass the check). The database is the final word: the second insert always fails.

**Discarded alternative:** Enforcing both rules only in the backend. Simpler, but a
double click, a script or a manual query could break them.
