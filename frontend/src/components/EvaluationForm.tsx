import { useEffect, useState, type FormEvent } from "react";
import { ApiError, createEvaluation, listQuestions, type Question } from "../api";

const SCALE = [1, 2, 3, 4];

const ERROR_MESSAGES: Record<number, string> = {
  403: "Você não pode avaliar essa pessoa: ela não está abaixo de você na hierarquia.",
  409: "Você já avaliou essa pessoa nesta semana.",
  422: "Respostas inválidas: responda as 6 perguntas com nota de 1 a 4.",
};

type Props = {
  leaderId: number;
  employeeId: number;
  onSaved: () => void;
  onCancel: () => void;
};

export function EvaluationForm({ leaderId, employeeId, onSaved, onCancel }: Props) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [scores, setScores] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listQuestions()
      .then(setQuestions)
      .catch(() => setError("Não foi possível carregar as perguntas."));
  }, []);

  const answered = questions.filter((question) => scores[question.id] !== undefined).length;
  const complete = questions.length > 0 && answered === questions.length;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!complete || submitting) return;

    // The button stays disabled until the answer arrives, so a double click sends one request.
    // If two still get through, the database's UNIQUE turns the second one into a 409.
    setSubmitting(true);
    setError(null);
    try {
      await createEvaluation(
        leaderId,
        employeeId,
        questions.map((question) => ({ question_id: question.id, score: scores[question.id] })),
      );
      onSaved();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? (ERROR_MESSAGES[err.status] ?? `Erro inesperado (${err.status}). Tente de novo.`)
          : "Sem conexão com o servidor. Tente de novo.",
      );
      setSubmitting(false);
    }
  }

  return (
    <form className="evaluation-form" onSubmit={handleSubmit}>
      {questions.map((question) => (
        <fieldset key={question.id} disabled={submitting}>
          <legend>
            {question.label} <span className="muted">peso {question.weight}</span>
          </legend>
          <div className="scale">
            {SCALE.map((score) => (
              <label key={score}>
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  checked={scores[question.id] === score}
                  onChange={() => setScores((current) => ({ ...current, [question.id]: score }))}
                />
                {score}
              </label>
            ))}
          </div>
        </fieldset>
      ))}

      {error && <p className="error" role="alert">{error}</p>}

      <div className="form-actions">
        <button type="submit" disabled={!complete || submitting}>
          {submitting ? "Enviando…" : "Enviar avaliação"}
        </button>
        <button type="button" className="secondary" onClick={onCancel} disabled={submitting}>
          Cancelar
        </button>
        <span className="muted">{answered} de {questions.length} respondidas</span>
      </div>
    </form>
  );
}
