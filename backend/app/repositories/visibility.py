"""The visibility rule (decisions b and i), written once and reused by every query that shows evaluations.

`visible_evaluation` holds the evaluations the viewer may see: the evaluated employee is below the
viewer, and the evaluator is the viewer or someone below them. `display_order` numbers the evaluations
of each employee: highest evaluator first (closest to the viewer), then newest week. So
`display_order = 1` is the highlighted one. Every query that uses it passes `%(viewer_id)s`.
"""

VISIBLE_EVALUATIONS_CTE = """
    WITH RECURSIVE tree (id, depth) AS (
        SELECT lead_id, 1
        FROM leader_lead
        WHERE leader_id = %(viewer_id)s
        UNION ALL
        SELECT leader_lead.lead_id, tree.depth + 1
        FROM leader_lead
        JOIN tree ON leader_lead.leader_id = tree.id
    ) CYCLE id SET is_cycle USING path,
    distance AS (
        -- Shortest path to each person. The viewer is 0, even if a cycle leads back to them.
        SELECT id, MIN(depth) AS depth
        FROM (
            SELECT id, depth FROM tree WHERE NOT is_cycle
            UNION ALL
            SELECT %(viewer_id)s, 0
        ) AS reached
        GROUP BY id
    ),
    visible_evaluation AS (
        SELECT evaluation.id,
               evaluation.leader_id,
               evaluation.employee_id,
               evaluation.week_start,
               evaluation.final_score,
               ROW_NUMBER() OVER (
                   PARTITION BY evaluation.employee_id
                   ORDER BY evaluator.depth, evaluation.week_start DESC, evaluation.submitted_at DESC
               ) AS display_order
        FROM evaluation
        JOIN distance AS evaluator ON evaluator.id = evaluation.leader_id
        JOIN distance AS evaluated ON evaluated.id = evaluation.employee_id
        WHERE evaluated.depth > 0
    )
"""
