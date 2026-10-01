Hello guys, I'm Pedro, and this document will allow you to understand some of my softwares 
decisions and architectural choices.

## (a) What is a "week"

**Decision:** A week is an ISO 8601 week (Monday to Sunday) in the company time zone,
`America/Sao_Paulo`. The evaluation timestamp is set by the server and stored in UTC
(`timestamptz`). The client never sends the date.

**Why:** The client clock can be wrong or tampered with ("never trust the client").
One fixed time zone gives the same rule to everyone, even in a country with 4 time zones.

**Discarded alternative:** Using each user's local time zone. The same leader–employee
pair could get different week boundaries, which makes "one per week" ambiguous. 
