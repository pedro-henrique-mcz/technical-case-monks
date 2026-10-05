This document records the main design decisions, each with its reasoning and the alternatives discarded.
AI tools helped polish the wording; every decision was made and reviewed by me.

## (a) What "one week" means

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

## (g) How the API identifies the current leader

**Decision:** The front end stores the selected leader's id in `localStorage` and sends it
on every request in the `X-Leader-Id` HTTP header. The API reads the leader from this header.

**Why:** "Who is asking" is identity, not a resource, so it belongs in a header, not in the URL.
This is the same place real authentication goes (`Authorization: Bearer <token>`): adding login
later only changes how the header is read, not the routes. The API stays stateless: every request
carries its own identity.

**Alternatives considered:**
- Path parameter (`/leaders/{id}/subordinates`): mixes who is asking with what is being asked.
- Query parameter (`?leader_id=1`): same issue, and ends up in browser history and server logs.

**Limitations:** There is no login, as stated in the challenge, so any client can send any id.
The server still validates that the id exists and only returns employees below that leader.

## (h) Tests run against a separate database

**Decision:** Tests use a database named `monks_test` on the same Postgres server as the
compose. It is dropped and rebuilt from `db/init` at the start of every run, and the
evaluation tables are emptied with `TRUNCATE` before each test.

**Why:** Running the tests never erases data created by hand during development or for a demo.
Every run starts from the exact schema that ships with the project. `TRUNCATE` is used
instead of `DELETE` because the immutability trigger blocks `DELETE`, and `TRUNCATE`
does not fire row-level triggers.

**Discarded alternative:** Using the compose database (`monks`). Zero setup, but every
test run would wipe the evaluations created while testing the app.

## (i) Distance in the hierarchy and cycles

**Decision:** To order evaluations by "highest evaluator first", the recursive query carries a
`depth` column (1 = direct report). Because `leader_lead` is many-to-many, the same person can be
reached through more than one path; the distance used is the shortest one (`MIN(depth)`), which is
the closest relationship to the viewer. Cycles are stopped with Postgres's `CYCLE` clause.

**Why:** With a `depth` column, rows reached through different paths are no longer identical, so
`UNION` stops removing them and no longer protects against a cycle. `CYCLE` marks the row that
closes a loop and stops there. A test inserts a cycle and checks that the query still returns.

**Discarded alternative:** Tracking the path in an array by hand (`path || id`, `NOT id = ANY(path)`).
It works, but `CYCLE` (Postgres 14+) does the same thing in one line.

## (j) The highlight in the list: one rule, no N+1

**Decision:** The visibility rule (decisions b and i) lives in one SQL fragment,
`VISIBLE_EVALUATIONS_CTE`, which numbers each employee's visible evaluations with `display_order`
(highest evaluator first, then newest week). The detail endpoint returns all of them in that order;
`GET /subordinates` takes only `display_order = 1`. The list is built from two fixed queries
(subordinates + highlights) merged by employee id in the service.

**Why:** The highlight in the list and the first item of the detail can never disagree, because
they come from the same rule. Two queries cost the same for 3 or 300 people.

**Discarded alternative:** Calling the detail query once per subordinate. Reuses the code, but it is
an N+1: one database round trip per person in the list.
**Discarded alternative:** One single query joining employees and evaluations. One round trip less,
but the employee repository would have to know about evaluations.
