-- 02_evaluation.sql
-- Evaluation model. Reasoning in docs/decisions.md.

-- The 6 fixed questions and their weights (decision c)
CREATE TABLE question (
    id      INT           PRIMARY KEY,
    label   VARCHAR(100)  NOT NULL,
    weight  INT           NOT NULL
);

INSERT INTO question (id, label, weight) VALUES
(1, 'Entrega de Resultados',  25),
(2, 'Execução e Qualidade',   20),
(3, 'Aprendizado',            20),
(4, 'Resolução de Problemas', 15),
(5, 'Colaboração/Liderança',  10),
(6, 'Visão Estratégica',      10);

-- The header: one row per evaluation
CREATE TABLE evaluation (
    id            SERIAL        PRIMARY KEY,
    leader_id     INT           NOT NULL,   -- who evaluates
    employee_id   INT           NOT NULL,   -- who is evaluated
    submitted_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    week_start    DATE          GENERATED ALWAYS AS (
        date_trunc('week', submitted_at AT TIME ZONE 'America/Sao_Paulo')::date
    ) STORED,
    final_score   NUMERIC(3,2)  NOT NULL CHECK (final_score BETWEEN 1 AND 4),

    CONSTRAINT fk_evaluation_leader
        FOREIGN KEY (leader_id)   REFERENCES employee(id) ON DELETE RESTRICT,
    CONSTRAINT fk_evaluation_employee
        FOREIGN KEY (employee_id) REFERENCES employee(id) ON DELETE RESTRICT,
    CONSTRAINT chk_no_self_evaluation CHECK (leader_id <> employee_id),
    CONSTRAINT uq_one_per_week UNIQUE (leader_id, employee_id, week_start)
);

-- The items: one row per answered question (decision d)
CREATE TABLE answer (
    evaluation_id  INT  NOT NULL REFERENCES evaluation(id) ON DELETE RESTRICT,
    question_id    INT  NOT NULL REFERENCES question(id)   ON DELETE RESTRICT,
    score          INT  NOT NULL CHECK (score BETWEEN 1 AND 4),
    PRIMARY KEY (evaluation_id, question_id)
);

-- Immutability: reject any UPDATE or DELETE (decision f)
CREATE FUNCTION reject_change() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION '% is immutable', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_evaluation_immutable
    BEFORE UPDATE OR DELETE ON evaluation
    FOR EACH ROW EXECUTE FUNCTION reject_change();

CREATE TRIGGER trg_answer_immutable
    BEFORE UPDATE OR DELETE ON answer
    FOR EACH ROW EXECUTE FUNCTION reject_change();
