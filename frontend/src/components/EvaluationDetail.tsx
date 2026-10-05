import { useEffect, useState } from "react";
import { listEvaluations, type Answer, type Evaluation, type Subordinate } from "../api";
import { formatScore, formatWeek } from "../format";
import { EvaluationForm } from "./EvaluationForm";

type Props = {
  leaderId: number;
  employee: Subordinate;
  onEvaluated: () => void;
};

export function EvaluationDetail({ leaderId, employee, onEvaluated }: Props) {
  const [evaluations, setEvaluations] = useState<Evaluation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);
  const [formOpen, setFormOpen] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false; // an answer that arrives after the person changed must not be shown
    listEvaluations(leaderId, employee.id)
      .then((data) => { if (!ignore) setEvaluations(data); })
      .catch(() => { if (!ignore) setError("Não foi possível carregar as avaliações."); });
    return () => { ignore = true; };
  }, [leaderId, employee.id, version]);

  function handleSaved() {
    setFormOpen(false);
    setNotice("Avaliação enviada.");
    setVersion((current) => current + 1); // reload this detail
    onEvaluated(); // and the list, whose highlight may have changed
  }

  // The API already returns them in order: the first one is the highlight (decision b).
  const highlight = evaluations?.[0];
  const history = evaluations?.slice(1) ?? [];

  return (
    <section className="detail">
      <header className="detail-header">
        <div>
          <h2>{employee.name}</h2>
          <p className="muted">{employee.position_name}</p>
        </div>
        {!formOpen && (
          <button type="button" onClick={() => { setFormOpen(true); setNotice(null); }}>
            Avaliar
          </button>
        )}
      </header>

      {notice && <p className="notice" role="status">{notice}</p>}

      {formOpen && (
        <EvaluationForm
          leaderId={leaderId}
          employeeId={employee.id}
          onSaved={handleSaved}
          onCancel={() => setFormOpen(false)}
        />
      )}

      {error && <p className="error">{error}</p>}
      {evaluations === null && !error && <p className="muted">Carregando…</p>}
      {evaluations?.length === 0 && <p className="muted">Ainda não avaliado.</p>}

      {highlight && (
        <>
          <h3>Avaliação em destaque</h3>
          <div className="card">
            <EvaluationSummary evaluation={highlight} />
            <AnswersTable answers={highlight.answers} />
          </div>
        </>
      )}

      {history.length > 0 && (
        <>
          <h3>Histórico</h3>
          {history.map((evaluation) => (
            <details key={evaluation.id} className="card">
              <summary><EvaluationSummary evaluation={evaluation} /></summary>
              <AnswersTable answers={evaluation.answers} />
            </details>
          ))}
        </>
      )}
    </section>
  );
}

function EvaluationSummary({ evaluation }: { evaluation: Evaluation }) {
  return (
    <span className="summary">
      <span className="score">{formatScore(evaluation.final_score)}</span>
      <span className="muted">
        semana de {formatWeek(evaluation.week_start)} · por {evaluation.leader_name}
      </span>
    </span>
  );
}

function AnswersTable({ answers }: { answers: Answer[] }) {
  return (
    <table>
      <thead>
        <tr><th>Pergunta</th><th>Peso</th><th>Nota</th></tr>
      </thead>
      <tbody>
        {answers.map((answer) => (
          <tr key={answer.question_id}>
            <td>{answer.label}</td>
            <td>{answer.weight}</td>
            <td>{answer.score}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
